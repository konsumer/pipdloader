#!/usr/bin/env python3

from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
import socket

class BiDirectionalClient(udp_client.SimpleUDPClient):
  def __init__(self, address: str, port: int, allow_broadcast: bool = False) -> None:
    super().__init__(address, port, allow_broadcast)
    self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self._sock.bind(('', 0))
    self.client_port = self._sock.getsockname()[1]
    self.address = address

client = BiDirectionalClient("127.0.0.1", 8000)

# test client
client.send_message("/sw", 1)
client.send_message("/sw", 0)

def h_default(*a):
  print("from pd", a)

dispatcher = Dispatcher()
dispatcher.map("/rgb", h_default)
dispatcher.map("/hsv", h_default)
dispatcher.map("/rot", h_default)
dispatcher.map("/text", h_default)
dispatcher.map("/rect", h_default)
dispatcher.map("/graph", h_default)
dispatcher.set_default_handler(h_default)

ThreadingOSCUDPServer.allow_reuse_address = True
server = ThreadingOSCUDPServer((client.address, client.client_port), dispatcher)
server.serve_forever() 