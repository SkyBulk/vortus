import os
import sys

# sqlmap version (<major>.<minor>.<month>.<monthly commit>)
VERSION = "1.3.8.12"
TYPE = "dev" if VERSION.count('.') > 2 and VERSION.split('.')[-1] != '0' else "stable"
TYPE_COLORS = {"dev": 33, "stable": 90, "pip": 34}
VERSION_STRING = "sqlmap/%s#%s" % ('.'.join(VERSION.split('.')[:-1]) if VERSION.count('.') > 2 and VERSION.split('.')[-1] == '0' else VERSION, TYPE)
DESCRIPTION = "automatic SQL injection and database takeover tool"
SITE = "http://sqlmap.org"
DEFAULT_USER_AGENT = "%s (%s)" % (VERSION_STRING, SITE)
DEV_EMAIL_ADDRESS = "dev@sqlmap.org"
ISSUES_PAGE = "https://github.com/sqlmapproject/sqlmap/issues/new"
GIT_REPOSITORY = "https://github.com/sqlmapproject/sqlmap.git"
GIT_PAGE = "https://github.com/sqlmapproject/sqlmap"
ZIPBALL_PAGE = "https://github.com/sqlmapproject/sqlmap/zipball/master"
say = "There are plenty of fish in the sea"
# colorful banner
BANNER = """\033[01;33m\
        ___
       __H__
 ___ ___[.]_____ ___ ___  \033[01;37m{\033[01;%dm%s\033[01;37m}\033[01;33m
|_ -| . [.]     | .'| . |
|___|_  [.]_|_|_|__,|  _|
      |_|V...       |_|   \033[0m\033[4;37m%s\033[0m\n
""" % (TYPE_COLORS.get(TYPE, 31), VERSION_STRING.split('/')[-1], SITE)


def help_option():
    print("\t\033[01;32m")
    print("\tlisteners   : show default settings.")
    print("\thelp        : show default settings.")
    print("\tsessions    : show default settings.")
    print("\tclear       : clear screen.")
    print("\tquit        : quit.\033[00m")

def print_help_option(option):

    found = 0
    for opt in help_options.items():
        if opt[0] == option:
            found = 1
            printt(32, "%s - %s" %(option, opt[1]))
    if not found:
        printt(3, "Error: option \'%s\' not found." %option)


def tests_pyver():
    if sys.version[:3] == "3.6" or "3" in sys.version[:3]:
        pass # All good
    elif "2" in sys.version[:3]:
        print("vortus has no support for Python 2.")
    else:
        print("Your Python version is very old ..")