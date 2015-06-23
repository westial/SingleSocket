"""Usage example of a SingleSocket talking with only one socket client.

What it does:

    * Starts socket server and opens a socket client on server waiting for
      a client.
    * When client connects, the server side client sends some messages.
    * If another client opens a communication the first client will be
      disconnected.

Requirements:

    * Python 2.7.x

Run the example:

    * Start the usingSocket.py script: `python usingSocket.py`
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
                web=False,
                max_clients=1,
                welcome="Benvingut destraler!!\n")

port = stream.start()

print('Emitting port: {:d}'.format(port))

if not stream.running:
    exit(0)

# wait for me
time.sleep(5)

stream.send("Hello World!\n")
time.sleep(1)

stream.send("Hello Moon!\n")
time.sleep(1)

stream.send("Hello Mars!\n")
time.sleep(1)

stream.send("Hello Juneda!\n")
time.sleep(1)

stream.stop()