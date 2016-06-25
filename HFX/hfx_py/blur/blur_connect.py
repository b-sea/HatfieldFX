"""
Blur Connect
    Allows for dynamic development in python between software without needing to relaunch.
"""

# python imports
import os
import socket
import threading
import traceback

# package imports
from blur_talks import parse, registerBlurStatement, commands
import defaults

# message size limit
size = 999999999

# backlog
backlog = 5

# host
host = ''

# Store any already instanced servers
SERVER = None
CLIENT = None


class BlurConnection(threading.Thread):
    """
    Blur connection.
    """

    def __init__(self, application):
        """
        :return:
        """
        super(BlurConnection, self).__init__()

        port = 20000

        self._kill = False
        self.message = None
        self.application = application

        self.daemon = True

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        portCount = 10
        tries = 0
        while tries < portCount:
            try:
                self.socket.bind(('localhost', port))
                self.socket.listen(5)
                print "Server started on " + str(port)
                break
            except socket.error, e:
                port += 1
                tries += 1

    def kill(self):
        """
        Kill the running server.
        :return:
        """
        self._kill = True

    def run(self):
        while 1:
            client, address = self.socket.accept()
            data = client.recv(size)
            if data:
                result = parse(data)
                if result:
                    client.send(str(result))
            client.close()


class BlurTalk:
    """
    Gateway to communicating to the open blur application servers.
    """
    servers = {}

    def __init__(self):
        self.refreshServers()

    def serverNames(self):
        """
        Get the server names.
        :return:
        """
        return self.servers.keys()

    def communicate(self, command, port):
        """
        Communicate to an open blur server.
        :param command:
        :param port:
        :return:
        """
        if isinstance(port, int):
            s = self.connect(port)
        else:
            s = self.connect(self.servers[str(port)])
        s.settimeout(5)
        s.send(command)
        data = 'timed out'
        try:
            data = s.recv(size)
        except socket.timeout:
            pass
        s.close()
        try:
            return eval(data)
        except:
            return data

    @staticmethod
    def connect(port):
        """
        Connect to a Blur server.
        :param port:
        :return:
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect(('localhost', port))
        return s

    def refreshServers(self):
        """
        Refresh the server list.
        :return:
        """

        port = 20000
        portCount = 10
        while port < (port + portCount):
            try:
                openApplication = self.communicate('APP', port)
                self.servers[openApplication] = port
                port += 1

            except socket.error, e:
                break


if 'HFX_APP' in os.environ:
    # Create application communication server
    BlurConnection(os.environ['HFX_APP']).start()
