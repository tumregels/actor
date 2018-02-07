import configparser
import logging
import os
import os.path as op
import sys
from collections import OrderedDict

import requests

if getattr(sys, 'frozen', False):
    # we are running in a bundle
    bundle_dir = sys._MEIPASS
    cwd = op.dirname(sys.executable)
else:
    # we are running in a normal Python environment
    bundle_dir = op.join(op.dirname(op.abspath(__file__)), op.pardir)
    cwd = bundle_dir

os.chdir(cwd)

logging.basicConfig(
    filename=op.join(cwd, 'log.txt'),
    filemode='w',
    format='%(asctime)s: %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)

# uncomment this line to print logs in console
# logging.getLogger('').addHandler(console)
logger = logging.getLogger(__name__)

config = configparser.ConfigParser(allow_no_value=True)
config.optionxform = str
config.read(op.join(cwd, 'config.txt'))

teen_activity_list = [act for act in config['ACTIVITIES']]
teen_backend_list = [be for be in config['BACKENDS']] if 'BACKENDS' in config else []

army_activity_list = [act for act in config['ACTIVITIES']]
army_backend_list = [be for be in config['ARMY_BACKENDS'] ] if 'ARMY_BACKENDS' in config else []

all_backends = list(OrderedDict((x, True) for x in army_backend_list + teen_backend_list).keys())
all_activities = list(OrderedDict((x, True) for x in army_activity_list + teen_activity_list).keys())

settings = config['SETTINGS']

settings.dates = config['DATES'] if 'DATES' in config else []

settings.download_path = op.abspath(
    settings.get('download_path', './downloads'))
settings.extension_path = op.abspath(
    settings.get('extension_path', op.join(cwd, 'assets/TumoExamHelper.crx')))
settings.browser_exe_path = op.abspath(
    settings.get('browser_exe_path', op.join(cwd, 'assets/Chromium.app/Contents/MacOS/Chromium')))
settings.chromedriver_path = op.abspath(
    settings.get('chromedriver_path', op.join(cwd, 'assets/chromedriver')))

logger.info('download_path:' + settings.download_path)
logger.info('extension_path:' + settings.extension_path)
logger.info('browser_exe_path:' + settings.browser_exe_path)
logger.info('chromedriver_path:' + settings.chromedriver_path)

status = settings.get('status', 0) # zero stands for pending
is_army_only = settings.getboolean('army_only') # TODO to be removed

session = requests.session()
session.verify = False


