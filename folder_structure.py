import os

# Define the list of directories and files to ignore
IGNORE_DIRS = {'.git', '__pycache__', 'neurodragon.egg-info'}
IGNORE_FILES = {'.gitignore','folder_structure.py'}

def print_directory_structure(startpath):
    for root, dirs, files in os.walk(startpath):
        # Exclude ignored directories from being traversed
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if f not in IGNORE_FILES:
                print('{}{}'.format(subindent, f))

if __name__ == "__main__":
    print("Copy the following structure:")
    print_directory_structure(".")
