import sys
import os
import time
import core

from core.autocomplete import complete
from core.settings import VERSION
from core.settings import help_option
from core.helpers import version
from core.listener import Listeners
from core.sessions import sessions


class Shell:
    array = ["listeners", "sessions", "help", "clear", "quit"]

    def __init__(self):
        print("\033[H\033[J") # Clear the screen
        print("\033[01;31m")
        print("Vortus")
        print("\033[00m")
        sys.stdout.write("\t  .:[ Vortus {}]:.\n\033[00m".format(VERSION))
        version()
    
    def shell(self):
        while True:
            try:
                complete(self.array)
                an = input("Vortus > ") or "help"
                prompt = an.split()
                if not prompt:
                    continue
                elif prompt[0] == ";" or prompt[0] == "clear":
                    print("\033[H\033[J")
                elif prompt[0] == "q" or prompt[0] == "quit":
                    print("[%s]\033[01;32m %s\033[00m" %(time.strftime("%H:%M:%S"),"bye bye!"))
                    sys.exit(1)
                elif prompt[0] == "help" or prompt[0] == "?":
                    help_option()
                elif prompt[0] == "listeners":
                   a = Listeners()
                   a.shell()
                elif prompt[0] == "sessions":
                    sessions()
                else:
                    print("Error: No such command \'%s\'." %prompt[0])
                    
            except KeyboardInterrupt:
                print("\b\b  \nThere are plenty of fish in the sea")

            except Exception as e:
                raise e
