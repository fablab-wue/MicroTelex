import socket
import select
import network

# Based on https://github.com/cpopp/MicroTelnetServer

RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
DEFAULT_PORT = 23

_run = False
_server_socket = None

# Attach new clients and 
# send telnet control characters to disable line mode
# and stop local echoing
def _accept_telnet_connect(server):
    global _run

    client, remote_addr = server.accept()
    print("Telnet connection from:", remote_addr)
    client.setblocking(False)
    
    client.send(bytes([255, 252, 34])) # dont allow line mode
    client.send(bytes([255, 251, 1])) # turn off local echo
    client.send('Hallo'.encode())

    _run = True
    while _run:
        # Get the list sockets which are ready to be read through select
        read_sockets, write_sockets, error_sockets = select.select([client],[],[], 3)
 
        for sock in read_sockets:
            try:
                #In Windows, sometimes when a TCP program closes abruptly,
                # a "Connection reset by peer" exception will be thrown
                data = sock.recv(RECV_BUFFER)

                if not data: # connection closed by client
                    _run = False
                    break

                print('U:', data)
                if b'\xFF' in data:
                    break

                print('F:', data)
                try:
                    cmd_str = data.decode('utf-8', 'backslashreplace')   # bytes -> str
                except:
                    cmd_str = '{?}'
                print('A:', cmd_str)
                #ret = Cmd.excecute(cmd_str, source)
                #    ret_str = json.dumps(ret) + '\r\n\r\n'   # object -> json-str
                ret_str = cmd_str.upper()
                data = ret_str.encode()   # str -> bytes
                sock.sendall(data)

            # client disconnected
            except Exception as e:
                print ('Telnet - Exception:', str(e))
                _run = False
                break

        if error_sockets:
            print('Telnet - error_sockets')
            break

        print('.', end='')
        # end while

    print('Telnet - clinet {} disconnected'.format(remote_addr))
    client.close()


def stop():
    global _server_socket, _run
    
    _run = False
    if _server_socket:
        _server_socket.close()
    _server_socket = None


# start listening for telnet connections on port 23
def run(port=DEFAULT_PORT):
    global _server_socket
    
    stop()
    _server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    _server_socket.bind(("0.0.0.0", port))
    _server_socket.listen(1)
    _server_socket.setsockopt(socket.SOL_SOCKET, 20, _accept_telnet_connect)
    
    for i in (network.AP_IF, network.STA_IF):
        wlan = network.WLAN(i)
        if wlan.active():
            print("Telnet server started on {}:{}".format(wlan.ifconfig()[0], port))
