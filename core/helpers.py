import sys

def help_option():
	print("\t\033[01;32m")
	print("\trun    : load module.")
	print("\tlist   : list modules.")
	print("\tinfo   : get info for about module.")
	print("\tback   : back")
	print("\thelp   : help \033[00m")

def version():
    if sys.version[:3] == "3.6" or "3" in sys.version[:3]:
        pass # All good
    elif "2" in sys.version[:3]:
        print("Vortus has no support for Python 2.")
    else:
        print("Your Python version is very old ..")