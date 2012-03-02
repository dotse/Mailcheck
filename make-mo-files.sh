#!/bin/bash

path=$(cd ${0%/*} && echo $PWD/${0##*/})
path=`dirname "$path"`

echo "Generating en..."
(cd $path/locale/en_US/LC_MESSAGES && msgfmt -o mailcheck.mo mailcheck.po)

echo "Generating sv..."
(cd $path/locale/sv_SE/LC_MESSAGES && msgfmt -o mailcheck.mo mailcheck.po)

echo "Done"

