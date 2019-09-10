import threading
import time
import queue
import json
import socket

from core.utils import wrap_response
from core import logger
from data.state import VortusState

logger = logger.get_logger(__name__)


class ServerConnectionThread(threading.Thread):
    def __init__(self, conn, client_address, slave2beacon, mqs, rq):
        threading.Thread.__init__(self)
        self.conn = conn
        self.client_address = client_address
        self.ip = client_address[0]
        self.port = client_address[1]
        self.message_queues = mqs
        self.response_queue = rq
        self.slave2beacon = slave2beacon
        self.subscribed_topics = ["all", client_address]
        self.conn.setblocking(0)

    def connection_closed(self):
        logger.debug("Beacon {0}:{1} - Socket: Connection Closed".format(self.ip, self.port))
        self.response_queue.put(wrap_response("SYSTEM", "[+] Connection from {0} has been closed".format(self.client_address)))
        self.cleanup_state()

    def cleanup_state(self):
        del self.message_queues[self.client_address]
        # Copying such that the dict is not mutated during iteration
        for k, v in self.slave2beacon.copy().items():
            if v == self.client_address:
                del self.slave2beacon[k]
        # Delete from global stte
        VortusState.delete_by_criteria("slaves", lambda s: s.beacon == self.client_address)

    def run(self):
        name = threading.current_thread().getName()

        logger.debug("Beacon {0}:{1} connected".format(self.ip, str(self.port)))
        self.response_queue.put(wrap_response("SYSTEM", "[+] Beacon {0}:{1} connected".format(self.ip, str(self.port))))
        
        # Start loop for commands
        is_success = True
        while is_success:
            ## Check if there is anything to receive
            try:
                message  = self.conn.recv(1024).decode("utf-8").strip()
                if message is not "":
                    logger.debug("Beacon {0}:{1} received message: {2}".format(self.ip, str(self.port), message))
                    self.response_queue.put(wrap_response(self.client_address, message))
                else:
                    self.connection_closed()
                    break
            except socket.error as e:
                # Nothing to receive... just pass
                pass
            
            ## Check if there is anything to send
            for topic in self.subscribed_topics:
                try:
                    cmd = self.message_queues[topic].get(block=False)
                except queue.Empty:
                    continue

                logger.debug("Thread {0} received command: \"{1}\",  on subscribed topic: \"{2}\"".format(name, cmd, topic))
                try:
                    logger.debug("Thread {0} sending command: {1}".format(name, cmd))
                    self.conn.send(cmd.encode('utf-8'))
                except Exception as ex:
                    is_success = False
                    logger.error("Thread {0} command failed: {1}:".format(name, ex))
                    print(ex)
            time.sleep(0.1)