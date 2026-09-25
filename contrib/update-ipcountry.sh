#!/bin/bash
#
# Refresh ipcountry.db from DB-IP's free "IP to Country Lite" database.
#
# DB-IP publishes a new file on the 1st of each month (about 06:30 UTC) at
#   https://download.db-ip.com/free/dbip-country-lite-YYYY-MM.mmdb.gz
# Licence: CC BY 4.0, which requires a visible link to https://db-ip.com on the site.
#
# The new file is checked with the app's own reader (demovibes/ip2cc/mmdb.py)
# before it replaces the live one; if anything fails, the live file is left
# alone. The previous file is kept as ipcountry.db.prev. The app opens the file
# once per worker, so a graceful reload (SIGHUP to the uWSGI master, the same
# as `systemctl reload`, allowed as cvgm) follows a successful swap.
#
# Usage: update-ipcountry.sh [-n]    -n = download and check only, change nothing
# Cron:  output is appended to ~/logs/update-ipcountry.log by the crontab line.

set -u
export PATH=/usr/local/bin:/usr/bin:/bin

SITE=/home/cvgm/cvgm.net
DB=$SITE/ipcountry.db
PY=/home/cvgm/cvgm_virt2/bin/python
UNIT=cvgm-uwsgi-app
DRY=0
[ "${1:-}" = "-n" ] && DRY=1

log() { echo "$(date '+%F %T') $*"; }
fail() { log "FAILED: $*; live file unchanged"; exit 1; }

# Same filesystem as $DB, so the final mv is an atomic rename.
WORK=$(mktemp -d "$SITE/.ipcountry-XXXXXX") || fail "mktemp"
trap 'rm -rf "$WORK"' EXIT

# This month's file; before it is published (early on the 1st), last month's.
month=""
for m in "$(date -u +%Y-%m)" "$(date -u -d "$(date -u +%Y-%m-15) -1 month" +%Y-%m)"; do
    url="https://download.db-ip.com/free/dbip-country-lite-$m.mmdb.gz"
    if curl -fsS --max-time 300 -o "$WORK/new.mmdb.gz" "$url"; then
        month=$m
        break
    fi
    log "not available: $url"
done
[ -n "$month" ] || fail "no file could be downloaded"
gzip -dc "$WORK/new.mmdb.gz" > "$WORK/new.mmdb" || fail "gunzip $month"

if cmp -s "$WORK/new.mmdb" "$DB"; then
    log "unchanged: $month is already live"
    exit 0
fi

# Check it with the reader the site uses.
"$PY" - "$WORK/new.mmdb" "$SITE/demovibes" <<'EOF' || fail "check of $month"
import os, sys, time
sys.path.insert(0, sys.argv[2])
from ip2cc import mmdb

path = sys.argv[1]
size = os.path.getsize(path)
assert size > 2 * 1024 * 1024, "file too small: %d bytes" % size
db = mmdb.CountryByIP(path)
kind = db.metadata["database_type"]
assert "Country" in kind, "unexpected database type %r" % kind
assert db.metadata["ip_version"] == 6, "no IPv6 in this file"
# Well-known addresses; each must give a two-letter code, Google DNS must be US.
for ip in ("8.8.8.8", "1.1.1.1", "212.58.244.1", "2001:4860:4860::8888"):
    cc = db[ip]
    assert len(cc) == 2 and cc.isalpha(), "%s -> %r" % (ip, cc)
assert db["8.8.8.8"] == "US", "8.8.8.8 -> %r" % db["8.8.8.8"]
print "check ok: %s, built %s, %d bytes" % (
    kind, time.strftime("%Y-%m-%d", time.gmtime(db.metadata["build_epoch"])), size)
EOF

if [ $DRY -eq 1 ]; then
    log "dry run: $month downloaded and checked; nothing changed"
    exit 0
fi

chmod 644 "$WORK/new.mmdb"
cp -p "$DB" "$DB.prev" || fail "backup of the current file"
mv -f "$WORK/new.mmdb" "$DB" || fail "swap"
log "installed $month (previous file kept as $DB.prev)"

pid=$(systemctl show -p MainPID --value "$UNIT")
if [ -n "$pid" ] && [ "$pid" != "0" ] && kill -HUP "$pid"; then
    log "reloaded $UNIT (pid $pid)"
else
    log "WARNING: could not reload $UNIT; the new file is used after the next reload"
    exit 1
fi
