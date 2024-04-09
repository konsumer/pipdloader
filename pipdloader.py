#!/usr/bin/env python3

from argparse import ArgumentParser

args = ArgumentParser(description='Run puredata patch headless, and interact with hardware')
args.add_argument('file', metavar="FILE", help='Puredata file to load', default='./MAIN.pd')
args.add_argument('-i', '--input', help='GPIO inputs', action='append', type=int)
args.add_argument('-o', '--output', help='GPIO outputs', action='append',  type=int)
args.add_argument('-s', '--oled', help='Enable i2c ssd1306 128x64 OLED', action='store_true')
args.add_argument('-r', '--rotary', help='Enable i2c 4/8-encoder', choices=[4,8], type=int)
args.add_argument('-l', '--lib', help='Include other dirs in puredata path', action='append')

# TODO: options for allowing pd gui command (show gui for running patch) - see https://github.com/libpd/libpd/pull/97

a = args.parse_args()

from threading import Thread

# params are 0-1
def hsv_to_rgb( h, s, v, a ):
    if s:
        if h == 1.0: h = 0.0
        i = int(h*6.0); f = h*6.0 - i
        
        w = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        
        if i==0: return (v, t, w, a)
        if i==1: return (q, v, w, a)
        if i==2: return (w, v, t, a)
        if i==3: return (w, q, v, a)
        if i==4: return (t, w, v, a)
        if i==5: return (v, w, q, a)
    else: return (v, v, v, a)

class RotaryHardwareThread(Thread):
  def __init__(self, pdsend, size=4):
    Thread.__init__(self)
    self.pdsend = pdsend
    self.size = size
    self.rotaries = [0] * size
    self.buttons = [0] * size

  def run(self):
    while True:
      try:
        v = self.get_switch()
        if v != self.switch:
          self.pdsend('switch', v)
          self.switch = v
      except AttributeError:
        pass
      for index in range(self.size):
        v = self.get_rotary(index)
        if v != self.rotaries[index]:
          self.pdsend('rotary', index, v)
          self.rotaries[index] = v
        v = self.get_button(index)
        if v != self.buttons[index]:
          self.pdsend('button', index, v)
          self.buttons[index] = v
  
  # implement these in sub-class

  def set_rgb(self, index, r, g, b):
    pass

  def set_hsv(self, index, h, s, v):
    pass

  def set_rotary(self, index, value):
    pass

  def get_rotary(self, index):
    pass

  def get_button(self, index):
    pass

# TODO: fill these in with real hardware things

class Rotary8Handler(RotaryHardwareThread):
  def __init__(self, pdsend):
    RotaryHardwareThread.__init__(self, pdsend, 8)
    self.switch = 0

  def get_switch(self):
    pass

  def set_rgb(self, index, r, g, b):
    if index > 7 or index < 0:
      print(f"set_rgb: {index} is not in range: 0-7")
      return
    pass

  def set_hsv(self, index, h, s, v):
    if index > 7 or index < 0:
      print(f"set_hsv: {index} is not in range: 0-7")
      return
    pass

  def set_rotary(self, index, value):
    if index > 7 or index < 0:
      print(f"set_rotary: {index} is not in range: 0-7")
      return
    pass

  def get_rotary(self, index):
    if index > 7 or index < 0:
      print(f"get_rotary: {index} is not in range: 0-7")
      return
    pass

  def get_button(self, index):
    if index > 7 or index < 0:
      print(f"get_button: {index} is not in range: 0-7")
      return
    pass


import board
import busio

import digitalio
import adafruit_seesaw.seesaw
import adafruit_seesaw.neopixel
import adafruit_seesaw.rotaryio
import adafruit_seesaw.digitalio


class Rotary4Handler(RotaryHardwareThread):
  def __init__(self, pdsend):
    RotaryHardwareThread.__init__(self, pdsend, 8)
    self.i2c = busio.I2C(board.SCL, board.SDA)
    self.seesaw = adafruit_seesaw.seesaw.Seesaw(self.i2c, 0x49)
    self.encoders = [adafruit_seesaw.rotaryio.IncrementalEncoder(self.seesaw, n) for n in range(4)]
    self.switches = [adafruit_seesaw.digitalio.DigitalIO(self.seesaw, pin) for pin in (12, 14, 17, 9)]
    for switch in self.switches:
        switch.switch_to_input(digitalio.Pull.UP)
    self.pixels = adafruit_seesaw.neopixel.NeoPixel(self.seesaw, 18, 4)
    self.pixels.brightness = 1

  def set_rgb(self, index, r, g, b):
    if index > 3 or index < 0:
      print(f"set_rgb: {index} is not in range: 0-3")
      return
    self.pixels[index] = (r, g, b)

  def set_hsv(self, index, h, s, v):
    if index > 3 or index < 0:
      print(f"set_hsv: {index} is not in range: 0-3")
      return
    pass
    (r,g,b,a) = hsv_to_rgb(h, s, v, 1)
    self.pixels[index] = (r, g, b)

  def set_rotary(self, index, value):
    if index > 3 or index < 0:
      print(f"set_rotary: {index} is not in range: 0-3")
      return
    pass

  def get_rotary(self, index):
    if index > 3 or index < 0:
      print(f"get_rotary: {index} is not in range: 0-3")
      return
    pass

  def get_button(self, index):
    if index > 3 or index < 0:
      print(f"get_button: {index} is not in range: 0-3")
      return
    pass


class OledHandler(Thread):
  def __init__(self):
    Thread.__init__(self)
  
  def run(self):
    pass

  def text(self, color, x, y, text):
    pass

  def rectangle(self, color, x, y, w, h):
    pass

  def graph(self, color, x, y, w, h, data):
    # map data to bounds, then draw like this: https://stackoverflow.com/questions/46614294/faster-way-to-plot-an-image-with-pil
    pass

  def draw(self):
    pass


class GpioHandler(Thread):
  def __init__(self, pdsend, inputs=[], outputs=[]):
    Thread.__init__(self)
    self.pdsend = pdsend
    self.inputs = inputs
    self.outputs = outputs
    #TODO: set mode for input/outputs
    #TODO: setup some change-interrupts for inputs


  def set(self, index, value):
    if index not in self.outputs:
      print(f"gpio: {index} pin was not in output option. Add it, if you want that.")
      return
    pass

  def get(self, index):
    if index not in self.inputs:
      print(f"gpio: {index} pin was not in input option. Add it, if you want that.")
      return
    pass

  def run(self):
    pass


# begin actual runtime

import pyaudio
from pylibpd import *
from os.path import dirname, basename

# simplewrapper around sending messages to patch for rotary
def send_message_to_pd(name, *args):
  libpd_message('_host', name, *args)

p = pyaudio.PyAudio()

ch = 1
sr = 44100
tpb = 6
bs = libpd_blocksize()

stream = p.open(format = pyaudio.paInt16, channels = ch, rate = sr, input = True, output = True, frames_per_buffer = bs * tpb)

m = PdManager(ch, ch, sr, 1)
libpd_open_patch(basename(a.file), dirname(a.file))

rotary = None
if a.rotary:
  if a.rotary == 4:
    rotary = Rotary4Handler(send_message_to_pd)
  else:
    rotary = Rotary8Handler(send_message_to_pd)
  rotary.start()

oled = None
if a.oled:
  oled = OledHandler()
  oled.start()

gpio = None
if a.input or a.output:
  gpio = GpioHandler(send_message_to_pd, a.input, a.output)
  gpio.start()

def hook_message(name, command, *args):
  if rotary != None:
    if command == 'rgb':
      rotary.set_rgb(int(args[0]), int(args[1]), int(args[2]), int(args[3]))
    if command == 'hsv':
      rotary.set_hsv(int(args[0]), float(args[1]), float(args[2]), float(args[3]))
    if command == 'rotary':
      rotary.set_rotary(int(args[0]), int(args[1]))
  if oled != None:
    if command == 'text':
      oled.text(int(args[0]), int(args[1]), int(args[2]), " ".join(args[3:]))
    if command == 'rectangle':
      oled.rectangle(int(args[0]), int(args[1]), int(args[2]), int(args[3]), int(args[4]))
    if command == "graph":
      oled.graph(int(args[0]), int(args[1]), int(args[2]), int(args[3]), int(args[4]), args[5:])
    if command == "draw":
      oled.draw()
  if gpio != None:
    if command == "gpio":
      gpio.set(int(args[0]), int(args[1]))

def hook_print(s):
  o = s.strip()
  if len(o):
    print(o)

libpd_set_print_callback(hook_print)
libpd_set_message_callback(hook_message)
libpd_subscribe('_patch')
libpd_add_to_search_path(dirname(__file__) + "/lib")

if a.lib != None:
  for l in a.lib:
    libpd_add_to_search_path(l)

while 1:
  data = stream.read(bs)
  outp = m.process(data)
  stream.write(bytes(outp))

stream.close()
p.terminate()
libpd_release()
