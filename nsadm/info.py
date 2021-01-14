"""Information.
"""

import os

import appdirs


APP_NAME = 'nsadm'
AUTHOR = 'ns_usovietnam'
DESCRIPTION = 'Automatically update and format dispatches.'

# Pluggy project name for loader plugins.
DISPATCH_LOADER_PROJ = 'NSADMDispatchLoader'
VAR_LOADER_PROJ = 'NSADMVarLoader'
CRED_LOADER_PROJ = 'NSADMCredLoader'

# Default directories
default_dirs = appdirs.AppDirs(APP_NAME, AUTHOR)
CONFIG_DIR = default_dirs.user_config_dir
DATA_DIR = default_dirs.user_cache_dir
LOGGING_DIR = default_dirs.user_log_dir

# Loader plugin directory path.
LOADER_DIR_PATH = 'nsadm/loaders'

CONFIG_ENVVAR = 'NSADM_CONFIG'
CONFIG_NAME = 'config.toml'
# Default general configuration path for copying to proper place
DEFAULT_CONFIG_PATH = 'nsadm/config.toml'

# Logging configuration
LOGGING_PATH = os.path.join(LOGGING_DIR, 'nsadm_log.log')
LOGGING_CONFIG = {
    'version': 1,

    'formatters': {
        'NSADMFormatter': {
            'format': '[%(asctime)s %(name)s %(levelname)s] %(message)s'
        }
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'NSADMFormatter',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'NSADMFormatter',
            'filename': LOGGING_PATH,
            'maxBytes': 5000000,
            'backupCount': 2
        }
    },

    'root': {
        'level': 'DEBUG',
        'handlers': ['console', 'file']
    }
}

# Category name and code reference.
SUBCATEGORIES_1 = {'overview': '100',
                  'history': '101',
                  'geography': '102',
                  'culture': '103',
                  'politics': '104',
                  'legislation': '105',
                  'religion': '106',
                  'military': '107',
                  'economy': '108',
                  'international': '109',
                  'trivia': '110',
                  'miscellaneous': '111'}

SUBCATEGORIES_3 = {'policy': '305',
                   'news': '315',
                   'opinion': '325',
                   'campaign': '385'}

SUBCATEGORIES_5 = {'military': '505',
                   'trade': '515',
                   'sport': '525',
                   'drama': '535',
                   'diplomacy': '545',
                   'science': '555',
                   'culture': '565',
                   'other': '595'}

SUBCATEGORIES_8 = {'gameplay': '835',
                   'reference': '845'}

CATEGORIES = {'factbook': {'num': '1', 'subcategories': SUBCATEGORIES_1},
              'bulletin': {'num': '3', 'subcategories': SUBCATEGORIES_3},
              'account': {'num': '5', 'subcategories': SUBCATEGORIES_5},
              'meta': {'num': '8', 'subcategories': SUBCATEGORIES_8}}