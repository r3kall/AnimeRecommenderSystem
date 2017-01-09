
import os

# Directories
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is the Project Root

FILE_DIR = os.path.join(ROOT_DIR, 'files')  # This is the directory of stored files

HTML_DIR = os.path.join(FILE_DIR, 'htmls')


# Files
LINKS_FILE = os.path.join(FILE_DIR, 'link-list.txt')
JSON_FILE = os.path.join(FILE_DIR, 'item-feature.json')
