The intent of this plugin is to provide users an easy way to find their location within a Liberty(.lib) file. Liberty files are
large files with a nested structure, and it is easy to get lost when reading or editing one.

Eventually, this may support multiple filetypes, but for now is focused on Liberty files.

# Dependancies
1. anytree (A python library)
2. vim compilied with at least Python2 (should also be forwards compatible)

# Installation
To install this plugin, use a plugin manager like [Pathogen](https://github.com/tpope/vim-pathogen).
Once you have a plugin manager setup, installing is as easy as running the following two commands:

`cd ~/.vim/bundle`

`git clone https://github.com/logan-markewich/liberty_pathing`

# Usage
`:ShowLocation` will display the current location in the statusline of your vim window. When opening a Liberty File, it will automatically be indexed for locations.

`:SaveLocation` will save a bookmark csv in your home directory. The path is printed in the statusline when ran. If multiple bookmarks are made in the same Liberty file, they will be appended.

The commands will also allow for tab completion so you don't have to type the entire command.

# Limitations/Improvements to Make
1. The indexing is very slow on super huge files (~200MB). It would be nice if there was some kind of index cache we could link into and use to avoid reindexing
every time.
2. The corner/cell name parsers should be used if available, otherwise the bookmarks don't work
