import sys
import os

SYSTEM_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SYSTEM_PATH)

from backend import Application

application = Application()
application.begin()