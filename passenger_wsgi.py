import sys

import os

INTERP = os.path.expanduser("/var/www/u1181746/data/botflaskenv/bin/python")
if sys.executable != INTERP:
   os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(os.getcwd())

from reger import application

    