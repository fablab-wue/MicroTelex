# userver.py Demo of simple uasyncio-based echo server

# Released under the MIT licence
# Copyright (c) Peter Hinch 2019

#import usocket as socket
import uasyncio as asyncio
#import uselect as select
#import ujson
#from heartbeat import heartbeat  # Optional LED flash

class Server:
    MSG_WELCOME = '-=TELEX=-\r\n'

    def __init__(self, host='', port=23, max_clients=10):
        self.host = host
        self.port = port
        self.max_clients = max_clients
        self.swriters = []


    async def start_server(self):
        await asyncio.start_server(self.handle_client, self.host, self.port, backlog=self.max_clients)

        
    async def handle_client(self, sreader:asyncio.StreamReader, swriter:asyncio.StreamWriter):
        self.swriters.append(swriter)
        addr = swriter.get_extra_info('peername')
        
        print('Client connected', addr)
        await swriter.awrite(bytes([255, 252, 34]))
        await swriter.awrite(bytes([255, 251, 1]))
        await swriter.awrite(bytes(self.MSG_WELCOME, "utf8"))

        try:
            while True:
                data = await sreader.read()
                print('Data', addr, data)
                if data == b'': # connection closed by client
                    raise OSError
                if b'\xFF' in data: # eat telnet command sequences
                    continue
                if data == b'\r\x00':
                    data = b'\r\n'
                #await swriter.awrite(data)  # echo back
                await self.broadcast(data) # echo to all clients

        except OSError:
            pass
        
        print('Client disconnect', addr)
        await swriter.aclose()
        self.swriters.remove(swriter)


    async def broadcast(self, data):
        for swriter in self.swriters:
            await swriter.awrite(data)


loop = asyncio.get_event_loop()
# Optional fast heartbeat to confirm nonblocking operation
#loop.create_task(heartbeat(100))
server = Server()
try:
    loop.call_soon(server.start_server())
    loop.run_forever()
    #loop.run_until_complete(server.run(loop))
except KeyboardInterrupt:
    print('Interrupted')  # This mechanism doesn't work on Unix build.
finally:
    #server.close()
    pass
