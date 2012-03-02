#!/bin/sh

DUMPFILE=$1
NODROP=$2
[ -z $DUMPFILE ] && DUMPFILE=schema.sql

if [ ! -f $DUMPFILE ] ; then
  echo "Where is $DUMPFILE ?  I cant find it!"
  exit 1
fi

PSQL=`which psql`

[ -x $PSQL ] || PSQL=/usr/lib/postgresql/8.2/bin/psql

if [ -z $NODROP ] ; then
  $PSQL -U postgres -c 'DROP DATABASE mailcheck;'
  $PSQL -U postgres -c 'CREATE DATABASE mailcheck;'
fi
echo "Using dumpfile $DUMPFILE"
$PSQL -U postgres mailcheck < $DUMPFILE
