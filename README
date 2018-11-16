The future intent of this plugin is to provide users an easy way to find their location within a Liberty(.lib) file. 
If you don't know what that is, this plugin isn't for you.

Eventually, this may support multiple filetypes, but for now is focused on Liberty files.

# Installation
To install this plugin, use a plugin manager like [Pathogen](https://github.com/tpope/vim-pathogen).
Once you have a plugin manager setup, installing is as easy as running the following two commands:
`cd ~/.vim/bundle`
`git clone https://github.com/logan-markewich/liberty_pathing`

# Usage
When opening a Liberty File, it will automatically be indexed. After indexing, type `:ShowLocation` anywhere within your file.
This will display the current location in the statusline of your vim window.
The command will also allow for tab completion so you don't have to type the entire command.

# Limitations/Improvements to Make
1. The indexing is very slow. It would be nice if there was some kind of index cache we could link into and use to avoid reindexing
every time.
2. The liberty path could be more accurate if it included some distinct attributes in the timing() groups.
