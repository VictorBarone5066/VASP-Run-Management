#!/usr/bin/env python3.6

# Error Check for VASP
import os
import sys
import ErrorCheckHeader as ech

origLoc = ech.pwd()
cd = os.chdir

#Get Command Line arguments
args = ech.ParseCommandLineArgs(argc = len(sys.argv), argv = sys.argv)

#Set root directory
##Sets working directory to wherever this code is unless a command line argument is passed
##by `./run -r myRootDir`
ROOT = origLoc + "//"
if(args["root"] != None):
    ROOT = args["root"]

# <codecell> MAIN

#Iterate through each subdirectory (I suggest not turning on followlinks - if a link points to a 
#parent directory, it will cause an infinite loop.
for path, dirs, files in os.walk(ROOT, topdown = True, followlinks = False):
    cd(path)

    #Condition to begin checking files
    if("POSCAR" in os.listdir()):
        #Check for pre-run problems
        if(args["pre"]):
            ech.CheckPoscar()
            ech.CheckPotcar()
            ech.CheckIncar()
            ech.CheckKPoints()

        #Check for post-run problems
        if(args["post"]):
            ech.CheckOutcarForTime()
            ##Re-sub with additional walltime if that is an issue
            if(ech.CheckWalltimeError()): 
                ech.AddWalltime()
#                ech.QSub()
                ###TODO:  Check force convergence, check completed vs requested ionic steps
                ###       *if completed ~~ requested, probably DONT need to add runtime.  In fact,
                ###       it might be better to calculate time per node and request runtime that way,
                ###       especially for jobs that would otherwise take a long time
                ###       *if forces are crazy high, the relaxation might be stuck.  In that case,
                ###       continuously resubbing is a waste of time.  Something else needs done
 

cd(origLoc)
