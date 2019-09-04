import random
import string

PURPLE = '\033[95m'
CYAN = '\033[96m'
DARKCYAN = '\033[36m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
END = '\033[0m'

def wrap_response(addr, msg):
    return  {"addr": addr, "msg": msg}

def randomString(length):
	letters = string.ascii_lowercase
	return ''.join(random.choice(letters) for i in range(length))

def print_status(string):
    print(BLUE + BOLD + '[*] ' + END + string)

def print_warning(string):
    print(YELLOW + BOLD + '[!] ' + END + string)

def print_good(string):
    print(GREEN + BOLD + '[+] ' + END + string)

def print_error(string):
    print(RED + BOLD + '[-] ' + END + string)




