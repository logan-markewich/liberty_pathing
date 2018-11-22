if !has("python")
  echo "vim has to be compilied with +python in order for liberty pathing to work"
  finish
endif

if exists('g:sample_plugin_loaded')
  finish
endif

let s:plugin_root_dir = fnamemodify(resolve(expand('<sfile>:p')), ':h')

python << EOF
import sys
from os.path import normpath, join
import vim
plugin_root_dir = vim.eval('s:plugin_root_dir')
python_root_dir = normpath(join(plugin_root_dir, '..', 'python'))
sys.path.insert(0, python_root_dir)
from liberty_pathing import *
filename = vim.eval("expand('%:p')")
indexed_file, library = index_file(filename) 
EOF

function Get_Location()
  python show_branching(indexed_file)
endfunction

function Save_Location()
  python save_location(indexed_file, filename, library)
endfunction

command! -nargs=0 ShowLocation call Get_Location()

command! -nargs=0 SaveLocation call Save_Location()

let g:sample_plugin_loaded = 1
