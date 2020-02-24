"""
Socket server for Configuration the IoT-Device
"""
import socket
import select

#https://github.com/cpopp/MicroTelnetServer


#######
# Globals:

CONNECTION_LIST = []    # list of socket clients
CONNECTION_SOURCE = {}    # list of socket prop
RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
PORT = 23

#######

def init(port):
    """ Prepare module vars and load plugins """
    global PORT
    
    PORT = port

# =====

def run(port:int=None):
    global CONNECTION_LIST, RECV_BUFFER, PORT
         
    if port:
        PORT = port

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this has no effect, why ?
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)
 
    # Add server socket to the list of readable connections
    CONNECTION_LIST.append(server_socket)
 
    #log (LOG_INFO, 'Telnet server listen on port {}', PORT)
    print('Telnet server listen on port {}'.format(PORT))

    while 1:
        # Get the list sockets which are ready to be read through select
        read_sockets, write_sockets, error_sockets = select.select(CONNECTION_LIST,[],[])
 
        for sock in read_sockets:
             
            #New connection
            if sock == server_socket:
                # Handle the case in which there is a new connection recieved through server_socket
                sockfd, addr = server_socket.accept()
                #print (str(addr))
                #print (addr)

                CONNECTION_LIST.append(sockfd)
                source = addr[0] + ':' + str(addr[1])
                print (source)
                #print(sockfd.fileno())
                CONNECTION_SOURCE[sockfd.fileno()] = source
                #log (LOG_DEBUG, 'Telnet - client {} connected', source)
                print('Telnet - client {} connected'.format(source))
                #print("Telnet server started on {}:{}".format(wlan.ifconfig()[0], port))

                sockfd.send(bytes([255, 252, 34]))
                sockfd.send(bytes([255, 251, 1]))
                sockfd.send('Hallo'.encode())

            #Some incoming message from a client
            else:
                # Data recieved from client, process it
                try:
                    #In Windows, sometimes when a TCP program closes abruptly,
                    # a "Connection reset by peer" exception will be thrown
                    data = sock.recv(RECV_BUFFER)
                    # echo back the client message
                    if data:
                        print('U:', data)
                        if b'\xFF' not in data:
                            print('F:', data)
                            try:
                                cmd_str = data.decode('utf-8', 'backslashreplace')   # bytes -> str
                            except:
                                cmd_str = '{?}'
                            print('A:', cmd_str)
                            #print (cmd_str, end='')
                            #print(sock.fileno())
                            #source = CONNECTION_SOURCE[sock.fileno()]   # hash for sock
                            #log (LOG_DEBUG, 'Command: {}', cmd_str)
                            #ret = Cmd.excecute(cmd_str, source)
                            #if MICROPYTHON:
                            #    ret_str = json.dumps(ret) + '\r\n\r\n'   # object -> json-str
                            #else:
                            #    ret_str = json.dumps(ret, indent=2) + '\n\n'   # object -> json-str
                            #    ret_str = ret_str.replace('\n', '\r\n')
                            ret_str = '+'
                            #log (LOG_DEBUG, ' - Answer: {}', ret_str)
                            #print (ret_str)
                            data = ret_str.encode()   # str -> bytes
                            #print (data)
                            sock.send(data)
                 
                # client disconnected, so remove from socket list
                except Exception as e:
                    #print (str(e))
                    #broadcast_data(sock, "Client (%s, %s) is offline" % addr)
                    #print ("Client (%s, %s) is offline" % addr)
                    #log (LOG_DEBUG, 'Telnet - clinet {} disconnected', addr)
                    print('Telnet - clinet {} disconnected'.format(addr))
                    sock.close()
                    CONNECTION_LIST.remove(sock)
                    continue
         
    server_socket.close()
    #log (LOG_INFO, 'Telnet server closed')
    print('Telnet server closed')
 
#######
