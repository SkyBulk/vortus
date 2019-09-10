class Slave(object):
    def __init__(self, mac_addr=None, username=None, ip=None, port=None,beacon=None):
        self.mac_addr = mac_addr
        self.username = username
        self.ip = ip
        self.port = port
        self.beacon = beacon

    def __hash__(self):
        return self.mac_addr.__hash__()

    def __eq__(self, obj):
        return self.mac_addr == obj or self.mac_addr == obj.mac_addr

    def __str__(self):
        return self.username + "@" + self.ip + ":" + str(self.port)