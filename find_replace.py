#!/usr/bin/env python
import os
import string
import re
from string import maketrans

def main():
    # Text variables
    intro = "\nWelcome to find&replace tool.";
    instr = ("  n to read in a new file\n" +
             "  f to find word in file\n" +
             "  r to replace word in file\n" +
             "  q to exit program\n")
    prompt = "Please enter another command" 

    # Intro text when program starts
    print intro + "\nCommands:"
    print instr; 

    # Variables for file input
    fileinput = ""
    goodfile = ""
    textfile = ""

    # User's command    
    userinput = raw_input()


    # Check user's input
    # Continue as long as user does not type in 'q'
    while(userinput is not 'q'):

        # New file
        if(userinput is 'n'):
            print "> Enter the file name"
            fileinput = raw_input();        
            if os.path.isfile(fileinput):
                textfile = open(fileinput,"rb+")
                goodfile = fileinput
                print "> File " + fileinput + " loaded successfully!"
            else:
                print "Invalid file name: " +  fileinput
                fileinput = goodfile # keep the file open if invalid input
                 
            print prompt;

        # Find word (file must be loaded first)
        if(userinput is 'f'):
            if os.path.isfile(fileinput):
                print "> Enter the word you would like to search for";
                searched = raw_input()
                find(textfile, searched)
                textfile = open(fileinput,"rb+") # keep file open
            else: 
                print "> Please load a file first"        
            print prompt;

        # Replace word
        if(userinput is 'r'):
            if os.path.isfile(fileinput):
                print "> Enter the word you would like to replace"
                replace = raw_input()
                print "> Enter the word you would like to replace " + "\"" + replace + "\"" + " with"
                change = raw_input()
                replaceAll(textfile, replace, change)
                textfile = open(fileinput,"rb+") # keep file open
            else:
                print "> Please load a file first"
            print prompt
                
   

        # Any other input commands besides the given will prompt
        # user to re-input a command.
        if userinput not in['n','f','r']:
            print "> Invalid command. " + prompt

        userinput = raw_input();

# Finds the word in the text file
def find(textfile, searched):
    found = 0;
    lines = textfile.readlines() 
    for i  in range(0, len(lines)):    # iterate through lines
        temp = lines[i]
        check = temp.split()
        for j in range(0, len(check)): # iterate through words
            if(compare(check[j], searched)):
                found = found + 1
                print "> " + textfile.name + " " + str(i + 1) + ": " + temp

    if found is not 0: 
        print "> " + str(found) + " Results Found."
    else:
        print "> No Results Found."
    return

# Helper function for find. Strips punctuation and ignores casing
def compare(this, tothis):
  lothis = this.lower().strip(string.punctuation)
  lotothis = tothis.lower().strip(string.punctuation)
  if lothis == lotothis:
      return True
  else:
      return False

def replaceAll(textfile, toReplace, replaceWith):
    olname = textfile.name
    newfile = open("temporary",'a') 
    lines = textfile.readlines()
    for i  in range(0, len(lines)):
        check = lines[i].split()           # Array of the line
        matches = quickfind(textfile, i, lines[i], check, toReplace) # Check if it exists and return indices
        if matches == False:
            newfile.write(lines[i]) 
        else:                              # Found matches
            print "Would you like to replace all on this line? Y or N?"
            answer = raw_input()
            while answer not in ['Y','N']: # Make sure user enter Y or N
                print "Invalid command, please select Y or N."
                answer = raw_input()
                
            if answer == "Y":              # replace occuring word
                newline = re.sub(re.compile(r'\b' + (toReplace) + r'\b',re.IGNORECASE),replaceWith,lines[i])
                newfile.write(newline)
            elif answer == "N":            # just append old line
                newfile.write(lines[i])
    os.remove(textfile.name)
    os.rename("temporary",olname) 
    return

def quickfind(textfile, linenr, line, linelist, term):
    found = False
    for i in range(0, len(linelist)):
        if(compare(linelist[i], term)):
            print "> " + textfile.name + " " + str(linenr + 1) + ": " + line
            found = True
    return found
            

if __name__ == '__main__': 
    main()

    
        
