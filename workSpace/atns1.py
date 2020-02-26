# userver.py Demo of simple uasyncio-based echo server

# Released under the MIT licence
# Copyright (c) Peter Hinch 2019

import usocket as socket
import uasyncio as asyncio
import uselect as select
import ujson
#from heartbeat import heartbeat  # Optional LED flash

class Server:
    MSG_WELCOME = '-=TELEX=-\r\n'

    async def run(self, loop, port=23):
        addr = socket.getaddrinfo('0.0.0.0', port, 0, socket.SOCK_STREAM)[0][-1]
        s_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # server socket
        s_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s_sock.setblocking(False)
        s_sock.bind(addr)
        s_sock.listen(5)
        self.socks = [s_sock]  # List of current sockets for .close()
        self.swriters = []
        print('Awaiting connection on port', port)
        poller = select.poll()
        poller.register(s_sock, select.POLLIN)
        while True:
            res = poller.poll(1)  # 1ms block
            if res:  # Only s_sock is polled
                c_sock, c_addr = s_sock.accept()  # get client socket
                print('Client connected', c_addr)
                loop.create_task(self.run_client(c_sock, c_addr))
            await asyncio.sleep_ms(200)


    async def run_client(self, c_sock, c_addr):
        self.socks.append(c_sock)
        c_sock.setblocking(False)
        sreader = asyncio.StreamReader(c_sock)
        swriter = asyncio.StreamWriter(c_sock, {'addr': c_addr})
        self.swriters.append(swriter)
        
        print('Client connected', c_addr)
        await swriter.awrite(bytes([255, 252, 34]))
        await swriter.awrite(bytes([255, 251, 1]))
        await swriter.awrite(bytes(self.MSG_WELCOME, "utf8"))

        try:
            while True:
                data = await sreader.read()
                if data == b'': # connection closed by client
                    raise OSError
                if b'\xFF' in data: # eat telnet command sequences
                    continue
                if data == b'\r\x00':
                    data = b'\r\n'
                print('Data', c_addr, data)
                #await swriter.awrite(res)  # Echo back
                await self.broadcast(data)

        except OSError:
            pass
        
        print('Client disconnect', c_addr)
        c_sock.close()
        self.socks.remove(c_sock)
        self.swriters.remove(swriter)


    async def broadcast(self, data):
        for swriter in self.swriters:
            await swriter.awrite(data)


    def close(self):
        print('Closing {} sockets.'.format(len(self.socks)))
        for sock in self.socks:
            sock.close()

loop = asyncio.get_event_loop()
# Optional fast heartbeat to confirm nonblocking operation
#loop.create_task(heartbeat(100))
server = Server()
try:
    loop.run_until_complete(server.run(loop))
except KeyboardInterrupt:
    print('Interrupted')  # This mechanism doesn't work on Unix build.
finally:
    server.close()
