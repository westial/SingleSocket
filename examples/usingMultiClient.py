"""Usage example of a SingleSocket talking with unlimited number of socket
clients.

What it does:

    * Starts socket server and opens a socket client on server waiting for
      clients.
    * When client connects, the server side client sends some messages.
    * If another client opens a communication, all clients receive the
      same messages

Requirements:

    * Python 2.7.x

Run the example:

    * Start the usingMultiClient.py script: `python usingMultiClient.py`
    * Open a shell and connect the netcat client: `nc 127.0.0.1 9999`
"""

import sys

sys.path.append('..')

import time
from SingleSocket.Output import Output

SOCKET_PORT = 9999
SOCKET_HOST = '127.0.0.1'

stream = Output(host=SOCKET_HOST,
                port=SOCKET_PORT,
                web=False)

port = stream.start()

print('Emitting port: {:d}'.format(port))

if not stream.running:
    exit(0)

# wait for me
time.sleep(5)

stream.append_msg("Hello World!\n")
time.sleep(1)

stream.append_msg("Hello Moon!\n")
time.sleep(1)

stream.append_msg("Hello Mars!\n")
time.sleep(1)

stream.append_msg("Hello Juneda!\n")
time.sleep(1)

stream.stop()
