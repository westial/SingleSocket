"""Usage example of a SingleSocket talking with unlimited number of socket
clients but only the client who sends the valid password can be listening.

What it does:

    * Starts socket server and opens a socket client on server waiting for
      clients.
    * When client connects, the server side client waits for the password.
    * If client sends the valid password the server provides the messages.
    * If client sends a wrong password the server disconnects client.
    * If another clients open a communication and the server validates them,
      all valid clients receive the same messages.

Requirements:

    * Python 2.7.x

Run the example:

    * Start the usingKeyPass.py script: `python usingKeyPass.py`
    * Open a Terminal and connect the netcat client: `nc 127.0.0.1 9999`
    * Write 1234 and send it by clicking Intro or Enter in the Terminal.
"""

import sys

sys.path.append('..')

import time
from SingleSocket.Output import Output

SOCKET_PORT = 9999
SOCKET_HOST = '127.0.0.1'

stream = Output(host=SOCKET_HOST,
                port=SOCKET_PORT,
                password='1234',
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
