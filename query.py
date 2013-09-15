#!/usr/bin/env python3

import sys

def username(question):
	# Reserve this are in case I want to prevent special characters etc in the future
	return input(question)

def password(question):
	import getpass
	return getpass.getpass(question)

# Taken from http://code.activestate.com/recipes/577058-query-yesno/
#  with some personal modifications
def yes_no(question, default=True):
    choices = {"yes":True, "y":True, "ye":True,
               "no":False, "n":False }
    
    if default == None:
        prompt = " [y/n] "
    elif default == True:
        prompt = " [Y/n] "
    elif default == False:
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while 1:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return default
        elif choice in choices.keys():
            return choices[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")

