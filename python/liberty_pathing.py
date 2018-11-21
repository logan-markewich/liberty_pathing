import urllib2
import json
import vim
import time
import gzip

from anytree import Node, RenderTree, search


def index_file(filename):
  stack = list()
  tree = list()
  is_root = True
  line_num = 0
  
  if not('.lib' in filename or '.gz' in filename):
    return None
  
  print("Indexing " + filename)  
  
  open_func = gzip.open if '.gz' in filename else open
  f = open_func(filename, 'r')  
  for line in f:
    line_num += 1
    if '{' in line:    
      if 'timing ()' in line or 'timing()' in line:
        true_line = line_num
        attributes = set() 
        while True:
          line = f.next()
          line_num += 1
          if ':' in line:
            attributes.add(line.strip())
          else:
            break

        # Build up timing name with attributes
        name = 'timing('
        for attribute in attributes:
          name += attribute.replace(' ', '').replace(':', '=').replace(';', '') + ', '
        name = name.strip().strip(',') + ')'

        tree.append(Node(name, parent=stack[-1], startLine=true_line))
        stack.append(tree[-1])

        # Need to check if current line is a new group (it probably is if we just got timing attributes)
        if '{' in line:
          name = line.strip().split('{')[0].strip()
          tree.append(Node(name, parent=stack[-1], startLine=line_num))
          stack.append(tree[-1])
      else:  
        name = line.strip().split('{')[0].strip()

        if is_root:
          tree.append(Node(name, startLine=line_num))
          stack.append(tree[0])
          is_root = False
        else:
          tree.append(Node(name, parent=stack[-1], startLine=line_num))
          stack.append(tree[-1])


    elif '}' in line:
      index = tree.index(stack[-1])
      tree[index].endLine = line_num
      stack.pop()
  print("Indexing Complete!")  
  return tree


def show_branching(tree):
  row, col = vim.current.window.cursor
  print(str(search.findall(tree[0], filter_=lambda node: node.startLine <= row and node.endLine >= row)[-1]).split("'")[1].replace(" ",""))
    
