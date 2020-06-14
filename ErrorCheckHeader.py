# Header File for error checking in VASP
import os
import re
from glob import glob as glob
from math import floor as floor
import SetPWD

STARTING_LOC = SetPWD.STARTING_DIR + "//WarningsErrors.csv"

def pwd():
	return os.getcwd()	

#For dealing with command line arguments
def ParseCommandLineArgs(argc, argv):
    parsed = {"root": None,
              "pre": False,
              "post": False
             }
    
    i = 1

    while(i < argc + 1):
        #set root dir
        if(argv[i - 1][0:2] == "-r"):
            parsed["root"] = argv[i]
        #toggle pre-run info
        if(argv[i - 1][0] == '-' and argv[i - 1][2:4] == "re"):
            parsed["pre"] = True
        if(argv[i - 1][0] == '-' and argv[i - 1][2:5] == "ost"):
            parsed["post"] = True      
            
        i = i + 1

    return parsed


#Gets the end nLines lines of a file filePath (hopefully) quicker than reading through the entire thing.
#Increase buffer buff to speed things up for larger files (in increments of 2^n)
#w/ help from https://stackoverflow.com/questions/136168/get-last-n-lines-of-a-file-with-python-similar-to-tail
def Tail(filePath, nLines = 10, buff=1028):
    if(buff < 1):
        print("Setting buffer size < 1 is a bad idea\n")
        return ["Tail():  Bad buffer size"]
    
    infile = open(filePath, 'r')
    foundLines = []
    
    blockCnt = -1
    #keep going until there are n lines
    while (len(foundLines) < nLines):
        try:
            infile.seek(blockCnt * buff, os.SEEK_END)
        except IOError:  #just in case you have a small file
            infile.seek(0)
            foundLines = infile.readlines()
            break

        foundLines = infile.readlines()
        blockCnt = blockCnt - 1
    infile.close()
    
    return foundLines[-nLines:]

#Writes warnings / errors to a file given by warnFilePath.  Writes three columns in csv format:
#col 1 is the path of the warn/err causing file,
#col 2 is the code: (W)arning or (E)rror,
#col 3 is an optional message
def WarningErrorHandler(culpritFilePath, code, message = "No message given", warnFilePath = STARTING_LOC):
    inFile = open(warnFilePath, 'a') #append to the warning file
    inFile.write(str(culpritFilePath) + ',' + str(code) + ',' + str(message) + '\n')
    inFile.close()

#Checks that a file exists, and that it is a file (not a directory or something else)
def CheckFileExistence(filePath):
    return (os.path.exists(filePath) and os.path.isfile(filePath))

#Scans files for phrases.  filePath is the file to scan, and keys is a [LIST] of phrases to look for
#Returns true if any of the phrases is found, and false otherwise
def ScanFileForPhrases(filePath, keys):
    if(not(isinstance(keys, list))):
        print("WARNING:  ScaneFileForPhrases() expects a list as an argument into 'keys', and you have not supplied one.")
    with open (filePath, 'r') as infile: ##scan infile as read-only line-by-line
        for line in infile:
            for key in keys:
                if (re.search(key, line)):
                    infile.close()
                    return True
    infile.close()
    return False

#Returns a list of all lines in a file containing *key* (in regex style).  If no lines are found,
#returns false
def GetLinesContainingPhrase(filePath, key):
    ret = []
    with open (filePath, 'r') as infile: ##scan infile as read-only line-by-line
        for line in infile:
            if(re.search(key, line)):
                ret.append(line)
    infile.close()
    
    if(len(ret) == 0):
        return False
    return ret    
    
#Counts the number of lines in a file.  Returns 0 if the file is empty. Carriage returns do NOT count
#as empty lines.
def CountLines(filePath):
    i = -1
    with open(filePath) as inFile:
        for i, _ in enumerate(inFile):
            pass
    inFile.close()
    return i + 1    
  
#Returns the file in dirPath whose name contains key that was created most recently
def GetMostRecentFile(dirPath, key):   
    try:
        return str(max(glob(str(dirPath) + str(key)), key=os.path.getctime))
    except (ValueError):
        return "GetMostRecentFile():  No Found File Error"
        

def CheckPoscar(filePath = "POSCAR", minLines = 9):
    #Write errors / warnings for POSCAR
    if(not CheckFileExistence(filePath)):
        WarningErrorHandler(pwd(), 'E', str(filePath) + ' not found')
    elif(CountLines(filePath) < minLines):
        WarningErrorHandler(pwd(), 'E', str(filePath) + " has less than " + str(minLines) + " lines")

    #Both cases (so far) throw errors, so if either one is false the run can not continue
    return ((CheckFileExistence(filePath)) and (CountLines(filePath) >= minLines))
    
def CheckIncar(filePath = "INCAR", minLines = 1):
    #Write errors / warnings for INCAR
    if(not CheckFileExistence(filePath)):
        WarningErrorHandler(pwd(), 'E', str(filePath) + ' not found')
    elif(CountLines(filePath) < minLines):
        WarningErrorHandler(pwd(), 'W', str(filePath) + " has less than " + str(minLines) + " lines")

    #Get the 'state' of the file.  Any errors, return false.  Otherwise return true
    state = True
    if(state):
        state = CheckFileExistence(filePath)
    
    return state
    
def CheckKPoints(filePath = "KPOINTS", minLines = 2) :   
    #Write errors / warnings for KPOINTS
    if(not CheckFileExistence(filePath)):
        WarningErrorHandler(pwd(), 'W', str(filePath) + ' not found')
    elif(CountLines(filePath) < minLines):
        WarningErrorHandler(pwd(), 'W', str(filePath) + " has less than " + str(minLines) + " lines")
    
    #Vasp can start w/o a KPOINTS file, so this should always return true (albeit with warnings sometimes)
    return True  

def GetPoscarAtomOrder(inLoc, atomTypeLineNum = 5):
    atomTypes = []
    with open(inLoc) as infile:
        for i, line in enumerate(infile):
            if (i == atomTypeLineNum):
                for a in line.split():
                    atomTypes.append(a)
                infile.close()
                break    
    return atomTypes

def GetPotcarAtomOrder(inLoc, key = "VRHFIN ="):
    matchedLines = GetLinesContainingPhrase(inLoc, str(key))
    
    if(matchedLines):
        atomTypes = []
        for i in matchedLines:
            atomTypes.append(re.search('=(.+?):', i).group(1)) #fancy regex stuff.  Returns everything
                                                               #between = and :
        return atomTypes
    return False
    
def CheckPotcar(filePath = "POTCAR", poscarFilePath = "POSCAR"):
    #Write errors / warnings for POTCAR
    if(not CheckFileExistence(filePath)):
        WarningErrorHandler(pwd(), 'E', str(filePath) + " not found")   
    ##need to determine if POSCAR actually exists before we read it
    if(CheckFileExistence(poscarFilePath)):
        if(not(GetPoscarAtomOrder(poscarFilePath) == GetPotcarAtomOrder(filePath))):
            WarningErrorHandler(pwd(), 'W', "Atom orders in POSCAR and POTCAR do not match")

    #Get the 'state' of the file.  Any errors, return false.  Otherwise return true
    state = True
    if(state):
        state = CheckFileExistence(filePath)
    
    return state

#The end of an OUTCAR generally looks like this:
"""
 General timing and accounting informations for this job:
 ========================================================
  
                  Total CPU time used (sec):        1.205
                            User time (sec):        1.180
                          System time (sec):        0.025
                         Elapsed time (sec):        1.206
  
                   Maximum memory used (kb):       44644.
                   Average memory used (kb):           0.
  
                          Minor page faults:         6213
                          Major page faults:            0
                 Voluntary context switches:           44

"""
def CheckOutcarForTime(filePath = "OUTCAR"):
    #Make sure OUTCAR actually exists first
    if(not CheckFileExistence(filePath)):
        WarningErrorHandler(pwd(), 'E', str(filePath) + " not found")
        return False
    #If there is timing info at the end of the file, then it finished
    end = Tail(filePath, nLines = 32, buff = 4096)
    for words in end:
        if(re.search("Voluntary context switches", words)):
            return True
    #Otherwise write an error
    WarningErrorHandler(pwd(), 'E', str(filePath) + " does not end with runtime info")
    return False
    
    
def CheckWalltimeError(dirPath = "", fileName = "*RUN*.*", key = "process killed \(SIGTERM\)"):
    try:
        if(ScanFileForPhrases(str(GetMostRecentFile(dirPath, fileName)), [key])):
            WarningErrorHandler(pwd(), 'E', "Job exceeded walltime")
            return True
    except(FileNotFoundError):
        WarningErrorHandler(pwd(), 'W', str(fileName) + " not found")
    return False

#Converts Hr:Min:Sec formatted time into total seconds.  Returns total seconds
def HrMinSecToSec(hrs, mins, secs):
    if(isinstance(hrs, str)):
        hrs = int(hrs)
    if(isinstance(mins, str)):
        mins = int(mins)
    if(isinstance(secs, str)):
        secs = int(secs)
        
    return hrs*60**(2) + mins*60 + secs

#Converts total seconds to Hr:Min:Sec format.  Returns a tuple of (hrs, mins, secs)
def SecToHrMinSec(secs):
    if(isinstance(secs, str)):
        secs = int(secs)
        
    newHrs = floor(secs/60**(2))
    newMins = floor(60*(secs/60**(2) - newHrs))
    newSecs = floor(60*(60*(secs/60**(2) - newHrs) - newMins))    
    return newHrs, newMins, newSecs

#Returns the walltime as written to a run script.  Three (int) returns:  hrs, mins, secs
def GetWalltime(dirPath = "", fileName = "*RUN*", key = "walltime"):
    #For penn state machines, the run file you're looking for is the one with the shortest file name, 
    #since the returned file is the original name w/ a bunch of garbage after it ("RUN.o121218")
    shortestName = min(glob(dirPath + fileName), key=len)
    timeString = (GetLinesContainingPhrase(shortestName, key)[0].split('=')[-1].split())[0]
    hrs, mins, secs = timeString.split(':')
    return int(hrs), int(mins), int(secs)

def GetNewWalltimeString(oldHrs, oldMins, oldSecs, secsToAdd = 3600):
    oldSecsTot = HrMinSecToSec(oldHrs, oldMins, oldSecs)
    newSecsTot = oldSecsTot + secsToAdd
    newHrs, newMins, newSecs = SecToHrMinSec(newSecsTot)
    #Convert those to the appropriate string
    newTimeStr = ""
    if (newHrs < 10):
        newTimeStr += '0' + str(newHrs)
    else:
        newTimeStr += str(newHrs)
    if (newMins < 10):
        newTimeStr += ":0" + str(newMins)
    else:
        newTimeStr += ':' + str(newMins)        
    if (newSecs < 10):
        newTimeStr += ":0" + str(newSecs)
    else:
        newTimeStr += ':' + str(newSecs)    
    
    return newTimeStr
    
def AddWalltime(dirPath = "", fileName = "*RUN*", key = "walltime", secsToAdd = 3600):
    #Assume the file with walltime info is the runfile with the smallest name
    shortestName = min(glob(dirPath + fileName), key=len)    
    toReplace = (GetLinesContainingPhrase(shortestName, key)[0].split('=')[-1].split())[0]
    oldHrs, oldMins, oldSecs = GetWalltime(dirPath, fileName, key)
    replaceWith = GetNewWalltimeString(oldHrs, oldMins, oldSecs, secsToAdd)
    
    #Edit that file to replace old runtime with new runtime
    infile = open(shortestName, "r")
    lines = infile.read()
    infile.close()
    lines = lines.replace(toReplace, replaceWith)
    outfile = open(shortestName, "w")
    outfile.write(lines)
    outfile.close()
    
    return


def QSub(dirPath = "", fileName = "*RUN*"):
    command = "qsub " + min(glob(dirPath + fileName), key=len)    
    os.system(command)
    
    





    
