#!/bin/bash

set -o nounset

DB="db.sqlite3"
TEMPLATE="$1"
DATA="$2"

: ${PORT=8000}

ps aux | grep -i 'python manage.py' | grep -v grep | cut -f2 -d' ' | xargs -I{} kill -9 {}

if [[ -e "$DB" ]];
    then rm "$DB"
fi

python manage.py syncdb --noinput

python manage.py publish_hits "$TEMPLATE" "$DATA"

python manage.py runserver $PORT



