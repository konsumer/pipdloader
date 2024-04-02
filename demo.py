from  pyaudio import *
from pylibpd import *

p = PyAudio()

ch = 1
sr = 44100
tpb = 6
bs = libpd_blocksize()

stream = p.open(format = paInt16, channels = ch, rate = sr, input = True, output = True, frames_per_buffer = bs * tpb)

# in patch: send messages to _patch
def handle_list(name, command, *args):
  print(command, args)
libpd_set_message_callback(handle_list)
libpd_subscribe('_patch')

def handle_print(s):
  print(s)

libpd_set_print_callback(handle_print)

m = PdManager(ch, ch, sr, 1)
libpd_open_patch('dktest.pd')

# patch should receive _host
libpd_message('_host', 'rotary', 0, 0)
libpd_message('_host', 'button', 0, 0)
libpd_message('_host', 'switch', 0)

while 1:
    data = stream.read(bs)
    outp = m.process(data)
    stream.write(bytes(outp))
    

stream.close()
p.terminate()
libpd_release()
