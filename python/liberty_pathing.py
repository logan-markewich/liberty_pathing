import urllib2
import json
#import vim

from anytree import Node, RenderTree

def index(filename):
    stack = list()
    tree = list()
    is_root = True
    line_num = 0
    with open(filename, 'r') as f:
        for line in f:
            line_num += 1
            # start of branch
            if '{' in line:    
                name = line.strip().split('{')[0].strip()
                if is_root:
                    tree.append(Node(name, line=line_num))
                    stack.append(tree[0])
                    is_root = False
                else:
                    tree.append(Node(name, parent=stack[-1], line=line_num))
                    stack.append(tree[-1])
            # end of branch
            elif '}' in line:
                stack.pop()
    
    print(RenderTree(tree[0]))
