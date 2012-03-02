#!/bin/sh

DUMPFILE=$1
[ -z $DUMPFILE ] && DUMPFILE=data.sql

if [ ! -f $DUMPFILE ] ; then
  echo "Where is $DUMPFILE ?  I cant find it!"
  exit 1
fi

PSQL=`which psql`

[ -x $PSQL ] || PSQL=/usr/lib/postgresql/8.2/bin/psql

echo "Using dumpfile $DUMPFILE"
$PSQL -U postgres mailcheck < $DUMPFILE
