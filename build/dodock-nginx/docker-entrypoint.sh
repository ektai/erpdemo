#!/bin/bash

## Thanks
# https://serverfault.com/a/919212
##

set -e

rsync -a --delete /var/www/html/assets/js /assets
rsync -a --delete /var/www/html/assets/css /assets
rsync -a --delete /var/www/html/assets/frappe /assets
. /rsync

chmod -R 755 /assets

touch /var/www/html/sites/.build -r $(ls -td /assets/* | head -n 1)

if [[ -z "$DODOCK_PY" ]]; then
    export DODOCK_PY=0.0.0.0
fi

if [[ -z "$DODOCK_PY_PORT" ]]; then
    export DODOCK_PY_PORT=8000
fi

if [[ -z "$DODOCK_SOCKETIO" ]]; then
    export DODOCK_SOCKETIO=0.0.0.0
fi

if [[ -z "$SOCKETIO_PORT" ]]; then
    export SOCKETIO_PORT=9000
fi

if [[ -z "$HTTP_TIMEOUT" ]]; then
    export HTTP_TIMEOUT=120
fi

envsubst '${DODOCK_PY}
    ${DODOCK_PY_PORT}
    ${DODOCK_SOCKETIO}
    ${SOCKETIO_PORT}
    ${HTTP_TIMEOUT}' \
    < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

echo "Waiting for dodock-python to be available on $DODOCK_PY port $DODOCK_PY_PORT"
timeout 10 bash -c 'until printf "" 2>>/dev/null >>/dev/tcp/$0/$1; do sleep 1; done' $DODOCK_PY $DODOCK_PY_PORT
echo "dodock-python available on $DODOCK_PY port $DODOCK_PY_PORT"
echo "Waiting for dodock-socketio to be available on $DODOCK_SOCKETIO port $SOCKETIO_PORT"
timeout 10 bash -c 'until printf "" 2>>/dev/null >>/dev/tcp/$0/$1; do sleep 1; done' $DODOCK_SOCKETIO $SOCKETIO_PORT
echo "dodock-socketio available on $DODOCK_SOCKETIO port $SOCKETIO_PORT"

exec "$@"
