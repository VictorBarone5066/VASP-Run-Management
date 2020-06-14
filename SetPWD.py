"""
Rant / Description of this file:
The absolutely insane stupid ridiculous inconceivably dumb ridiculous asinine way that I have to declare one (1) constant in python.  I need to save the directory
path of where we start the error search from so that errors are consistently written to the same file, in the same location, no matter what.  The main function calls
the header function, which has the method to write lines to a csv file.  but the header function is not the one being executed, so it does not know where it is.  Only
main does - fine.  So there are lines in main that determine the current location of the executed file, and save it to a variable.  So all I SHOULD have to do is tell the header file to grab that variable when it needs it.  This does not work, though, since the header file is only linked to main, but main is not linked to the 
header (why???).  OK, so then maybe I'll import main into the header file.  This does not work either since this creates a circular dependence, and python can't
handle that very well.  I can get around the circular dependence issue by shoving the import main statement into a function that is only called after both files are
initialized.  SURELY I can get access to this variable after both files are read in and the initial conditions are set, right?  No - importing a file, even if it and
all of its variables are set, reloads the entire file, even if you write `from main import variable`.  ALL of main is reloaded.  Which means that the original start
directory gets redefined to wherever an error happens to be found.  Which causes the location of the warnings file to be changed.  There is, as far as I know, no easy way to fix this, since there are no static (single runtime initialization) variables nor constant variables nor global-linked variables in python.  
"""
"""
This file is called by the header file to initialize the starting location of the script.  It should be called once and only once.
"""

import os
STARTING_DIR = os.getcwd()
