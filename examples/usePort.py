"""Use a port during a period of time for testing purposes.
"""


import sys
sys.path.append('..')

from sys import argv
import time
from SingleSocket.Output import Output

SOCKET_HOST = '127.0.0.1'
STEP_WAIT = 10

if len(argv) < 2:
    print 'use_port# Port number argument is required.'
    exit(1)

port = int(argv[1])

stream = Output(host=SOCKET_HOST,
                port=port,
                web=False,
                welcome="connected on port {:d}\n".format(port))

stream.start()

print('Emitting port: {:d}'.format(port))

if not stream.running:
    print 'use_port# socket is not working'
    exit(1)

for sec in range(0, 10):
    time.sleep(STEP_WAIT)

stream.stop()
