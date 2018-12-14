import vim
import gzip
import os.path
import imp

from imp import load_source
from anytree import Node, RenderTree, search
from os.path import expanduser

# Import parsers (if defined)
all_parsers = None
cell_name_parser = None
unified_parser_file = os.path.expandvars('$SOLIDO_EXTERNAL_PARSERS')
cell_parser_file = os.path.expandvars('$SOLIDO_CELL_NAME_PARSER')

if unified_parser_file != '$SOLIDO_EXTERNAL_PARSERS':
  all_parsers = load_source(unified_parser_file.split('/')[-1].split('.')[0], unified_parser_file)
elif cell_parser_file != '$SOLIDO_CELL_NAME_PARSER':
  cell_name_parser = load_source(cell_parser_file.split('/')[-1].split('.')[0], cell_parser_file)

# Constants
NO_ATTRIBUTES = ['cell', 'library', 'pin', 'bus', 'bundle', 'propagated_noise_low', 'propagated_noise_high', 'output_voltage_high', 'output_voltage_low']
IGNORE_ATTRIBUTES = ['value', 'sdf_cond', 'miller_cap_fall', 'miller_cap_rise', 'is_needed', 'stage_type', 'is_inverting']


# Function to index liberty file into a tree structure
# Inputs:
#   filename  - Path to a Liberty file to open.
# Outputs:
#   tree      - Set of anytree nodes containing indexed Liberty file locations.
#               Each node contains the name of the group, start line of the group, and end line
#               Will also return None if it is not a .lib or .lib.gz file
def index_file(filename):
  stack = list()
  tree = list()
  is_root = True
  line_num = 0
  
  # Check file type
  if not(filename.endswith('.lib') or filename.endswith('.lib.gz')):
    return None
  
  print("Indexing " + filename)  
  
  # Pick open function
  open_func = gzip.open if filename.endswith(".gz") else open
  
  f = open_func(filename, 'r')  
  for line in f:
    line_num += 1
    if '{' in line:    
      # Do we need to check for attributes?
      if not line.split('(')[0].strip() in NO_ATTRIBUTES:
        group = line.split('(')[0].strip()
        true_line = line_num
        attributes = set() 
        while True:
          line = f.next()
          line_num += 1
          # Grab attributes (they have : in them) or grab indexes for vectors
          if ':' in line or ('index' in line and 'vector' in group):
            attributes.add(line.strip().replace('\t',''))
          elif line.strip() == '':
            continue
          else:
            break

        # Build up group name with attributes
        name = group.split('(')[0].strip() + '{'
        for attribute in attributes:
          if ':' in attribute:
            if not attribute.split(':')[0].strip() in IGNORE_ATTRIBUTES:
              name += attribute.replace(' ', '').replace(':', '=').replace(';', '').replace('"','') + ', '
          else:
            name += attribute.replace(' ', '').replace(';', '').replace('"','') + ', '
        name = name.strip().strip(',') + '}'
        
        # Add group node to tree
        tree.append(Node(name, parent=stack[-1], start_line=true_line))
        stack.append(tree[-1])

        # Need to check if current line is a new group (it probably is if we just got group attributes)
        if '{' in line:
          name = line.strip().split('{')[0].strip()
          tree.append(Node(name, parent=stack[-1], start_line=line_num))
          stack.append(tree[-1])
        elif '}' in line:
          index = tree.index(stack[-1])
          tree[index].end_line = line_num
          stack.pop()
      else:
        # Add a group that doesn't need attributes
        name = line.strip().split('{')[0].strip() 

        # Check if we need (or can) use the cell name parser
        if 'cell' in name:
          cell = name.split('(')[1].strip(')').strip()
          if all_parsers != None:
            try:
              name = 'cell(' + all_parsers.parse_cell_name(cell) +')'
              name = name.replace('%(','[[').replace(')s',']]')
            except AttributeError:
              name = line.strip().split('{')[0].strip()
          elif cell_name_parser != None:
            try:
              name = 'cell(' + cell_name_parser.parse_cell_name(cell) +')'
              name = name.replace('%(','[[').replace(')s',']]')
            except AttributeError:
              name = line.strip().split('{')[0].strip()
        if is_root:
          name = name.split('(')[0]
          tree.append(Node(name, start_line=line_num))
          stack.append(tree[0])
          is_root = False
        else:
          tree.append(Node(name, parent=stack[-1], start_line=line_num))
          stack.append(tree[-1])
    elif '}' in line:
      # Reached end of group, record endline and remove from stack
      index = tree.index(stack[-1])
      tree[index].end_line = line_num
      stack.pop()

  f.close()
  print("Indexing Complete!")  
  return tree


# Function show user current Liberty location to user.
# Inputs:
#   tree  - Set of anytree nodes containing indexed Liberty file locations.
def show_branching(tree):
  row, col = vim.current.window.cursor
  print(str(search.findall(tree[0], filter_=lambda node: node.start_line <= row and node.end_line >= row)[-1]).split("'")[1].replace(" ",""))


# Helper function to get length of a file in lines
# Inputs:
#   filename  - Path to a file to open.
# Outputs:
#   i         - Length of file in lines.
def _get_file_len(filename):
  with open(filename) as f:
    for i, l in enumerate(f):
      pass
  return i + 1


# Function to save the current Liberty location into a bookmark file for use in MLChar.
# Multiple bookmarks made in the same Liberty file will appear in the same bookmark.
# Inputs:
#   tree      - Set of anytree nodes containing indexed Liberty file locations.
#   filename  - Path to a Liberty file to open.
# Outputs:
#   A file in your home directory with the saved bookmark. 
def save_location(tree, filename):
  row, col = vim.current.window.cursor
  
  # Get the name of the node that is in the current location
  location = str(search.findall(tree[0], filter_=lambda node: node.start_line <= row and node.end_line >= row)[-1]).split("'")[1].replace(" ","")
  location_list = location.split('/')

  # Formate end of location for bookmark
  if '(' in location_list[-1] and location_list[-1] in NO_ATTRIBUTES:
    location_list[-1] = location_list[-1].split('(')[0]

  # Build the bookmark entry
  base_name = filename.split('/')[-1]
  library = base_name.split('.lib')[0]
  
  bookmark = ''
  for item in location_list:
    bookmark += item + '/'
  bookmark = bookmark.strip('/')  
  bookmark += '",' + library
  bookmark += ',,,,ID'
  bookmark = '"' + bookmark

  # Check if bookmark csv already exists based on current Liberty file name
  # If it exists, append the new bookmark
  # If not, create a file with the proper header and bookmark
  bookmark_file_path = expanduser("~") + '/' + base_name + '_bookmark.csv'
  
  if os.path.isfile(bookmark_file_path):
    file_len = _get_file_len(bookmark_file_path)
    bookmark = bookmark.replace(",ID",','+str(file_len))
    with open(bookmark_file_path, 'a') as f:
      f.write(bookmark)
      f.write('\n')
  else:
    with open(bookmark_file_path, 'a+') as f:
      f.write('group_key_path,corner,indexes,origin_file,notes,id')
      f.write('\n')
      bookmark = bookmark.replace(',ID',',1')
      f.write(bookmark)
      f.write('\n')
  
  # Notify user of saved location of bookmark
  print("Bookmarked saved in " + bookmark_file_path)
