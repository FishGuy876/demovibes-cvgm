pidfile="/tmp/.demovibes-fcgi.pid"
pid=$(cat $pidfile)
echo "Killing old server (PID $pid) .."
kill $pid
echo "Starting FastCGI server .."
 ./manage.py runfcgi host=127.0.0.1 port=3033 method=threaded pidfile="$pidfile"
echo "Done"

