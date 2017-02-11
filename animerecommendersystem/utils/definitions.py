
import os

# Directories
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # This is the Project Root

FILE_DIR = os.path.join(ROOT_DIR, 'files')  # This is the directory of stored files

HTML_DIR = os.path.join(FILE_DIR, 'htmls')

USERS_DIR = os.path.join(FILE_DIR, 'users')

# Files
LINKS_FILE = os.path.join(FILE_DIR, 'link-list.txt')
JSON_FILE = os.path.join(FILE_DIR, 'item-feature.json')
JSON_USER_FILE = os.path.join(FILE_DIR, 'user-item.json')
USER_CLUSTER_DICT = os.path.join(FILE_DIR, 'user-cluster-dict.npy')
USER_CLUSTER_MATRIX = os.path.join(FILE_DIR, 'user-cluster-matrix.npy')
USER_CLUSTER_INDICES = os.path.join(FILE_DIR, 'user-cluster-indices.npy')

# Anime states codes
WATCHING = 1
COMPLETED = 2
ON_HOLD = 3
DROPPED = 4
PLANNED = 6

# Predefined rates according to anime state
COMPLETED_RATE = 7
PLANNED_RATE = 7
DROPPED_RATE = 4
WATCHING_RATE = 6
ON_HOLD_RATE = 6
