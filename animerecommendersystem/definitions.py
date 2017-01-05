
import os

# Directories
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is the Project Root

FILE_DIR = os.path.join(ROOT_DIR, 'files')  # This is the directory of stored files

if not os.path.exists(FILE_DIR):
    os.makedirs(FILE_DIR)


# Files
LINKS_FILE = os.path.join(FILE_DIR, 'link-list.txt')
