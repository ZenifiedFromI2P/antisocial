#!/bin/sh
URL="https://bitbucket.org/squeaky/portable-pypy/downloads/pypy3.3-5.5-alpha-20161013-linux_x86_64-portable.tar.bz2"
THENPWD=$(pwd)
# Fetch PyPy3
wget -o pypy.tar.bz2 $URL
sha512sum pypy.tar.bz2 | grep 1cd7a00da376b2db29b3e1f3e9bb7a77afc8ad988b3f13fd0805f37b23960a34
c=$?
if [[ $c != 0 ]]; then
  echo "MITM detected, the hash didn't match !!!"
  exit
fi
tar -jxvf pypy.tar.bz2
cd pypy3.3-5.5-alpha-20161013-linux_x86_64-portable
cd bin
./virtualenv-pypy $THENPWD/venv
source $THENPWD/venv/bin/activate
cd $THENPWD
pip install -r requirements.txt
python manage.py runserver
unset $THENPWD
