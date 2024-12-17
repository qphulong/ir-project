import sys
import os

SYSTEM_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SYSTEM_PATH)

from backend import Application

application = Application()
application.begin()
# output = application._get_all_text_from_fragment_id('cnn_L19wYWdlcy9jbTNscTZldHEwMDB4MjZwZTI2ajFnNXJx_text_10')
# print(output)
