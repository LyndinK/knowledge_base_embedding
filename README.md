# KB package

This is a package to work with RDF graphs reified with embeddings and images

# installation directions:
1) download project source code
2) launch terminal
3) cd into project directory
4) launch "python -m build" command
5) this would generate wheel file in ./dist directory
6) cd ./dist
7) launch "pip3 install <.whl file>" command where <.whl file> is the file generated during step 4.
   pip3 is just an example here, use any package manager you fancy.
8) project is installed in the current environment with the name kb

# usage directions:

1) import KB class from kb package
2) create a class instance
3) Use read_ttlplus() to read existing archive OR
4) Use read_raw() to read raw data and create tllplus archive

# contact info:

get in touch with me via kirill.lyndin@gmail.com if you have any further questions