#!python3
"""
Telex Device - Telnet Server
"""
__author__      = "Jochen Krapf"
__email__       = "jk@nerd2nerd.org"
__copyright__   = "Copyright 2018, JK"
__license__     = "GPL3"
__version__     = "0.0.1"

#from threading import Thread
from _thread import start_new_thread
from socket import socket, AF_INET, SOCK_STREAM

#######

class TelnetSrv():
    RECV_BUFFER = 1024
    MSG_WELCOME = '-=TELEX=-\r\n'

    def __init__(self, port=23):
        super().__init__()

        self._port = port

        self.run = True
        self.clients = []


        self.SERVER = socket(AF_INET, SOCK_STREAM)
        self.SERVER.bind(('', self._port))

        self.SERVER.listen(10)
        #print("Waiting for connection...")
        #self.ACCEPT_THREAD = Thread(target=self.accept_incoming_connections, name='TelnetSaic')
        #self.ACCEPT_THREAD.start()
        self.ACCEPT_THREAD = start_new_thread(self.accept_incoming_connections, ())
        pass


    def __del__(self):
        self.run = False
        #print('__del__ in TelexWebSrv')
        self.SERVER.close()
        #super().__del__()
    
    # =====


    # =====

    def accept_incoming_connections(self):
        """Sets up handling for incoming clients."""
        while self.run:
            client, client_address = self.SERVER.accept()
            print("Telnet - client connected %s:%s" % client_address)
            #self.clients[client] = client_address
            self.clients.append(client)
            #Thread(target=self.handle_client, name='TelnetShc', args=(client,)).start()
            start_new_thread(self.handle_client, (client,))


    def handle_client(self, client):  # Takes client socket as argument.
        """Handles a single client connection."""
        client.send(bytes([255, 252, 34]))
        client.send(bytes([255, 251, 1]))
        client.send(bytes(self.MSG_WELCOME, "utf8"))
        #msg = "%s has joined the chat!" % name
        #self.broadcast(bytes(msg, "utf8"))

        while self.run:
            msg = client.recv(self.RECV_BUFFER)
            if not msg:   # client has been terminated
                client.close()
                #del self.clients[client]
                self.clients.remove(client)
                print('Telnet - client disconnected')
                #self.broadcast(bytes("%s has left the chat." % name, "utf8"))
                break

            if b'\xFF' in msg:
                continue

            # echo back to all clients
            self.broadcast(msg)
            #print(msg)
            try:
                aa = msg.decode('UTF8')
            except:
                aa = '?'
            print(aa, end='')
            #aa = txCode.BaudotMurrayCode.translate(aa)

            #for a in aa:
            #    self._rx_buffer.append(a)


    def broadcast(self, msg:bytes):
        """Broadcasts a message to all the clients."""
        for client in self.clients:
            client.send(msg)

#######

