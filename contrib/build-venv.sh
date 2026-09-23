#!/bin/bash
# Attempt to rebuild cvgm_virt from contrib/requirements.txt on a modern base.
#
# Production's venv is a copied binary artifact that cannot be rebuilt on
# Debian 9. This script tests whether it can be rebuilt from scratch on
# bullseye instead — the step that has to work before the app can move off
# Debian 9.
#
# It deliberately ALWAYS exits 0 and writes a verdict to /build/report.txt,
# so the image builds even on failure and the log can be read. Check the
# OVERALL line, not the exit code.

set -u
VENV="${VENV:-/opt/cvgm_virt}"
REQ="${REQ:-/build/requirements.txt}"
REPORT=/build/report.txt
PY="$VENV/bin/python"
PIP="$VENV/bin/pip"

: > "$REPORT"
say() { echo "$*" | tee -a "$REPORT"; }
rule() { say "------------------------------------------------------------"; }

say "CVGM venv rebuild test"
say "date:   $(date -u +%Y-%m-%dT%H:%M:%SZ)"
say "base:   $(. /etc/os-release && echo "$PRETTY_NAME")"
say "python: $(python2.7 -V 2>&1)"
say "arch:   $(dpkg --print-architecture)"
rule

# --no-wheel is THE FIX for Django's missing templates, not an optimisation.
#
# Django 1.3's setup.py overrides distutils INSTALL_SCHEMES with
# `scheme['data'] = scheme['purelib']`, so its data_files (all 88 templates,
# including admin/login.html) install INTO site-packages. That override is a
# distutils mechanism: it fires under legacy `setup.py install` and is
# ignored by bdist_wheel, which packs data_files into <name>.data/data/ for
# pip to install to sys.prefix instead.
#
# So whenever `wheel` is present, pip builds a wheel first and the templates
# land in $VENV/django/... while site-packages/django has ZERO .html files.
# /admin/ then 500s with TemplateDoesNotExist: admin/login.html. This is the
# long-standing reason a venv had to be copied rather than rebuilt.
#
# Removing `wheel` makes pip fall back to `setup.py install` for sdists. It
# does NOT stop pip installing pre-built wheels it downloads - wheel is only
# needed to BUILD them - so Pillow still arrives as a cp27mu manylinux wheel
# with no compiler involved. Verified both on 2026-09-17.
virtualenv -p python2.7 --no-wheel "$VENV" >/dev/null 2>&1 || { say "FATAL: virtualenv creation failed"; say "OVERALL: FAIL"; exit 0; }
say "venv:   $($PY -V 2>&1) at $VENV"
say "pip:    $($PIP --version)"
rule

# ---------------------------------------------------------------- stage 1
# Everything except MySQL-python, which is the only pin needing a compiler
# and the only one expected to fail.
# pyenchant is excluded here and handled separately in stage 3. Its setup.py
# does `import enchant` at build time, which fires its ctypes loader looking
# for libenchant.so.1 (enchant 1.x) before anything is installed. bullseye
# ships enchant-2 only, so it raises ImportError during egg_info and pip
# aborts the ENTIRE batch - every other pin then silently never installs.
grep -viE '^(MySQL-python|pyenchant)' "$REQ" | grep -vE '^\s*(#|$)' > /tmp/req-nomysql.txt
say "STAGE 1: installing $(wc -l < /tmp/req-nomysql.txt) pins (all but MySQL-python, pyenchant)"
if $PIP install --no-build-isolation -r /tmp/req-nomysql.txt >/tmp/s1.log 2>&1; then
    say "  -> OK"
    S1=ok
else
    say "  -> FAILED; last 25 lines:"
    tail -25 /tmp/s1.log | sed 's/^/     /' | tee -a "$REPORT" >/dev/null
    tail -25 /tmp/s1.log | sed 's/^/     /'
    S1=fail
fi
rule

# ---------------------------------------------------------------- stage 2
# MySQL-python 1.2.3 (2010) #includes "my_config.h", which MySQL 8 and
# MariaDB Connector/C no longer ship. Ladder of increasingly pragmatic
# fallbacks; the first that works wins.
say "STAGE 2: MySQL adapter"
MYSQL_RESULT="none"

try_mysql() {
    local label="$1"; shift
    say "  trying: $label"
    if $PIP install --no-build-isolation "$@" >/tmp/s2.log 2>&1; then
        say "    -> OK ($label)"
        MYSQL_RESULT="$label"
        return 0
    fi
    say "    -> failed. Cause:"
    grep -iE 'fatal error|error:|No such file|not found|cannot find' /tmp/s2.log \
        | grep -viE 'errored out|Check the logs' | tail -3 | sed 's/^/       /' | tee -a "$REPORT" >/dev/null
    grep -iE 'fatal error|error:|No such file|not found|cannot find' /tmp/s2.log \
        | grep -viE 'errored out|Check the logs' | tail -3 | sed 's/^/       /'
    return 1
}

try_mysql "MySQL-python==1.2.3 (as pinned)" "MySQL-python==1.2.3"

if [ "$MYSQL_RESULT" = none ]; then
    # my_config.h is a generated config header; an empty one is enough for
    # MySQL-python's purposes on a MariaDB Connector/C include path.
    INC="$(mysql_config --include 2>/dev/null | tr ' ' '\n' | sed -n 's/^-I//p' | head -1)"
    if [ -n "$INC" ] && [ -d "$INC" ]; then
        say "  shimming $INC/my_config.h (empty stub)"
        : > "$INC/my_config.h"
        try_mysql "MySQL-python==1.2.3 + my_config.h shim" "MySQL-python==1.2.3"
    fi
fi

# mysqlclient IS MySQLdb — the maintained fork of this same C extension.
# Django 1.3 only requires MySQLdb.version_info >= (1,2,1,'final').
[ "$MYSQL_RESULT" = none ] && try_mysql "mysqlclient==1.3.14 (fork)" "mysqlclient==1.3.14"
[ "$MYSQL_RESULT" = none ] && try_mysql "mysqlclient==1.4.6 (fork)"  "mysqlclient==1.4.6"

if [ "$MYSQL_RESULT" = none ]; then
    say "  -> ALL MySQL adapter options failed; last 25 lines:"
    tail -25 /tmp/s2.log | sed 's/^/     /' | tee -a "$REPORT" >/dev/null
    tail -25 /tmp/s2.log | sed 's/^/     /'
fi
rule

# ---------------------------------------------------------------- stage 3
say "STAGE 3: pyenchant (optional - nothing in the codebase imports it)"
PYENCHANT_RESULT="skipped"
if $PIP install --no-build-isolation 'pyenchant==2.0.0' >/tmp/s3.log 2>&1; then
    say "  -> installed OK"
    PYENCHANT_RESULT="installed"
else
    say "  -> failed (expected): needs libenchant.so.1, bullseye ships enchant-2 only"
    grep -iE 'ImportError|not found' /tmp/s3.log | tail -2 | sed 's/^/     /' | tee -a "$REPORT" >/dev/null
    grep -iE 'ImportError|not found' /tmp/s3.log | tail -2 | sed 's/^/     /'
    PYENCHANT_RESULT="FAILED (not fatal)"
fi
rule

# ---------------------------------------------------------------- stage 3b
# Assert the data_files fix held. This is a verification, NOT a workaround:
# the cause is fixed by --no-wheel above. If this ever fails, something
# reintroduced wheel-based installation - do not paper over it by copying
# files, find out what put `wheel` back.
say "STAGE 3b: verifying package data landed inside site-packages"
SP="$($PY -c 'import site; print(site.getsitepackages()[0])' 2>/dev/null || echo "$VENV/lib/python2.7/site-packages")"
DJ_HTML=$(find "$SP/django" -name '*.html' 2>/dev/null | wc -l)
say "  django .html files in site-packages: $DJ_HTML (0 means the wheel path was used)"

# The decisive test: the exact template whose absence 500s /admin/.
# Checked on disk, NOT by importing django.contrib.admin - that import pulls
# in settings, so it raises without DJANGO_SETTINGS_MODULE and would report
# a perfectly good install as broken.
ADMIN_LOGIN="$SP/django/contrib/admin/templates/admin/login.html"
if [ -f "$ADMIN_LOGIN" ] && [ "$DJ_HTML" -gt 50 ]; then
    say "  admin/login.html present  -> /admin/ will render"
    DATAFILES_OK=yes
else
    say "  admin/login.html MISSING  -> /admin/ will 500 (TemplateDoesNotExist)"
    DATAFILES_OK=no
fi

# Informational only. Packages WITHOUT Django's INSTALL_SCHEMES override
# (django_authopenid, django_extensions) legitimately install data_files to
# the prefix; their templates are shipped as package_data separately and are
# already inside site-packages. A stray dir here is normal for them and is
# not evidence of a regression.
for d in "$VENV"/*/; do
    name="$(basename "$d")"
    case "$name" in bin|lib|lib64|include|share|man|src|local) continue ;; esac
    if [ -d "$SP/$name" ]; then
        has=$(find "$SP/$name" -name '*.html' 2>/dev/null | wc -l)
        say "  note: \$VENV/$name also exists (site-packages copy has $has .html files)"
    fi
done
rule

say "STAGE 4: import verification"
IMPORTS_OK=yes
# $2: required | optional | needs-django
#   needs-django - the module cannot be imported outside a configured Django
#   project (haystack 1.2.7 raises ImproperlyConfigured at import time when
#   HAYSTACK_SITECONF is unset). Checking presence is the honest test here;
#   importing it proves nothing about the install.
#
# NOTE: str() around __version__ is deliberate. Whoosh exposes it as a TUPLE
# (2, 3, 2), and sys.stdout.write() on a tuple raises
# "TypeError: expected a string or other character buffer object" - which
# previously reported a perfectly good install as MISSING.
check() {
    local mod="$1" required="$2" out
    if [ "$required" = needs-django ]; then
        if out=$($PY -c "import imp, sys; f=imp.find_module('$mod'); sys.stdout.write(f[1] or 'ok')" 2>&1); then
            say "  PRESENT  $mod (not imported: needs a configured Django project)"
        else
            say "  MISSING  $mod  <-- REQUIRED"
            IMPORTS_OK=no
            say "           $(echo "$out" | tail -1)"
        fi
        return
    fi
    if out=$($PY -c "import $mod, sys; sys.stdout.write(str(getattr($mod,'__version__','?')))" 2>/tmp/imp.err); then
        say "  OK       $mod ($out)"
    else
        if [ "$required" = required ]; then
            say "  MISSING  $mod  <-- REQUIRED"
            IMPORTS_OK=no
        else
            say "  absent   $mod  (optional)"
        fi
        say "           $(tail -1 /tmp/imp.err 2>/dev/null)"
    fi
}
check django    required
check MySQLdb   required
check PIL       required
check whoosh    required
check jinja2    required
check haystack  needs-django
check south     required
check tagging   required
check pycountry required
check memcache  required
check openid    optional
check enchant   optional   # nothing in the codebase imports this

rule

say "MySQL adapter: $MYSQL_RESULT"
say "pyenchant:     $PYENCHANT_RESULT"
say "package data:  ${DATAFILES_OK:-unknown}"
if [ "$S1" = ok ] && [ "$MYSQL_RESULT" != none ] && [ "$IMPORTS_OK" = yes ] && [ "${DATAFILES_OK:-no}" = yes ]; then
    say "OVERALL: PASS"
else
    say "OVERALL: FAIL"
fi
exit 0
