class Slave(object):
    def __init__(self, mac_addr=None, username=None, ip=None, port=None):
        self._mac_addr = mac_addr
        self._username = username
        self._ip = ip
        self._port = port

    @property
    def mac_addr(self):
        return self._mac_addr
    
    @property
    def username(self):
        return self._username

    @property
    def ip(self):
        return self._ip

    @property
    def port(self):
        return self._port

    def __hash__(self):
        return self.mac_addr.__hash__()

    def __eq__(self, obj):
        return self.mac_addr == obj or self.mac_addr == obj.mac_addr