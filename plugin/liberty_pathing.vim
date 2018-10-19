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
EOF

function! PrintCountry()
  python print_country()
endfunction

command! -nargs=0 PrintCountry call PrintCountry()

function! InsertCountry()
  python insert_country()
endfunction

command! -nargs=0 InsertCountry call InsertCountry()

let g:sample_plugin_loaded = 1
