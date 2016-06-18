# Explanation of files

* utils.py:     Functions to print stuff, makes debugging easier
* parser.py:    Functions to parse s-expressions to python lists
* main.py:      Handles communication with server
* state.py:     Contains object WorlState. It is a singleton so we use its attributes as global variables
* strategy.py:  The most important file, here you define your strategy