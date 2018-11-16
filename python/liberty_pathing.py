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
  print("Indexing " + filename)  
  if '.gz' in filename:
    with gzip.open(filename, 'r') as f:
      for line in f:
        line_num += 1
        # start of branch
        if '{' in line:    
          name = line.strip().split('{')[0].strip()
          if is_root:
            tree.append(Node(name, startLine=line_num))
            stack.append(tree[0])
            is_root = False
          else:
            tree.append(Node(name, parent=stack[-1], startLine=line_num))
            stack.append(tree[-1])
        # end of branch
        elif '}' in line:
          index = tree.index(stack[-1])
          tree[index].endLine = line_num
          stack.pop()
  else:    
    with open(filename, 'r') as f:
      for line in f:
        line_num += 1
        # start of branch
        if '{' in line:    
          name = line.strip().split('{')[0].strip()
          if is_root:
            tree.append(Node(name, startLine=line_num))
            stack.append(tree[0])
            is_root = False
          else:
            tree.append(Node(name, parent=stack[-1], startLine=line_num))
            stack.append(tree[-1])
        # end of branch
        elif '}' in line:
          index = tree.index(stack[-1])
          tree[index].endLine = line_num
          stack.pop()
    
  return tree

def show_branching(tree):
  row, col = vim.current.window.cursor
  print(str(search.findall(tree[0], filter_=lambda node: node.startLine <= row and node.endLine >= row)[-1]).split("'")[1].replace(" ",""))
  #print(RenderTree(tree[0]))
    
