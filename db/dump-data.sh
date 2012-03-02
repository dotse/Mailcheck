#!/bin/sh

DUMPFILE=data.sql

PG_DUMP=`which pg_dump`
PSQL=`which psql`

[ -x $PG_DUMP ] || PG_DUMP=/usr/lib/postgresql/8.2/bin/pg_dump
[ -x $PSQL ] || PSQL=/usr/lib/postgresql/8.2/bin/psql

echo -n "Dumping db data: "
$PG_DUMP --data-only --attribute-inserts -U postgres mailcheck > $DUMPFILE
echo "done"
