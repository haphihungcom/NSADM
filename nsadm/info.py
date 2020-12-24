APP_NAME = 'nsadm'
AUTHOR = 'ns_usovietnam'
DESCRIPTION = 'Automatically update and format dispatches.'

# Pluggy project name for loader plugins.
DISPATCH_LOADER_PROJ = 'NSADMDispatchLoader'
VAR_LOADER_PROJ = 'NSADMVarLoader'
CRED_LOADER_PROJ = 'NSADMCredLoader'

# Loader plugin directory path.
LOADER_DIR_PATH = 'loaders'

CONFIG_ENVVAR = 'NSADM_CONFIG'
CONFIG_NAME = 'config.toml'
# Default general configuration path for copying to proper place
DEFAULT_CONFIG_PATH = 'nsadm/config.toml'

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