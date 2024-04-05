#!/usr/bin/env python3

from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

from random import random
from argparse import ArgumentParser
from pylibpd import *
from struct import unpack
import array
import pygame
from pygame.locals import *
import numpy
import sys
from os.path import dirname, basename

args = ArgumentParser(description='Run puredata patch headless, and interact with hardware')
args.add_argument('file', metavar="FILE", help='Puredata file to load', default='MAIN.pnd')
args.add_argument('-i', '--input', help='GPIO inputs', action='append', type=int)
args.add_argument('-o', '--output', help='GPIO outputs', action='append',  type=int)
args.add_argument('-s', '--oled', help='Enable i2c ssd1306 128x64 OLED', action='store_true')
args.add_argument('-r', '--rotary', help='Enable i2c 4/8-encoder', choices=[4,8], type=int)
args.add_argument('-l', '--lib', help='Include other dirs in puredata path', action='append')
args.add_argument('-f', '--fullscreen', help='Show Fullscreen SDL GUI', action='store_true')

# TODO: OLED/LCD splash option?
# TODO: options for allowing pd gui command
# TODO: options for enabling/disabling pygame interface
# TODO: fullscreen option for pygame stuff 

a = args.parse_args()

if a.rotary or a.oled:
  import board
  import busio
  i2c = busio.I2C(board.SCL, board.SDA)

if a.input or a.output:
  import board
  import digitalio

if (a.rotary == 8):
  from M58Encoder import M58Encoder

if a.rotary == 4:
  # TODO: build same interface as M58Encoder
  print("4 rotary not implemented yet.")
  sys.exit()

rotary = None
oled = None
midi_in = []
midi_out = []

if a.rotary:
  rotary = M58Encoder(i2c)
  rotary_values = numpy.zeros(a.rotary)
  rotary_old_values = numpy.zeros(a.rotary)
  button_values = numpy.zeros(a.rotary)
  button_old_values = numpy.zeros(a.rotary)
  old_switch = 0
  # set initial to something else, so it will trigger initial send
  switch = -1
  for i in range(len(rotary_values)):
    rotary_values[i] = -1
    button_values[i] = -1


def hook_message(name, command, *args):
  if rotary != None:
    if command == 'rgb':
      rotary.set_led_color_rgb(int(args[0]), int(args[1]), int(args[2]), int(args[3]))
    if command == 'hsv':
      rotary.set_led_color_hsv(int(args[0]), args[1], args[2], args[3])
    if command == 'rotary':
      rotary.set_encoder_value(int(args[0]), int(args[1]))
  if oled != None:
    # TODO handle OLED commands
    pass


def hook_print(s):
  o = s.strip()
  if len(o):
    print(o)

# TODO: handle midi in/out (with auto-reconnecting and stuff)
# TODO: handle new patch load
# TODO: watch for file-changes, reload patch


libpd_set_print_callback(hook_print)
libpd_set_message_callback(hook_message)
libpd_subscribe('_patch')

# add to lib-path
libpd_add_to_search_path(dirname(__file__) + "/lib")
if a.lib != None:
  for l in a.lib:
    libpd_add_to_search_path(l)

screen = pygame.display.set_mode((640, 480), DOUBLEBUF|HWSURFACE, 16)
# screen = pygame.display.set_mode((640, 480), FULLSCREEN | DOUBLEBUF, 16)
surface = pygame.Surface(screen.get_size())
surface = surface.convert()
surface.fill((0,0,0))
pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])
pygame.display.set_caption('BellaSynth')
pygame.mouse.set_visible(False)

BUFFERSIZE = 4096
SAMPLERATE = 44100
BLOCKSIZE = 64

pygame.mixer.init(frequency=SAMPLERATE)
m = PdManager(1, 2, SAMPLERATE, 1)
patch = libpd_open_patch(basename(a.file), dirname(a.file))

inbuf = array.array('h', range(BLOCKSIZE))
ch = pygame.mixer.Channel(0)
sounds = [pygame.mixer.Sound(numpy.zeros((BUFFERSIZE, 2), numpy.int16)) for s in range(2)]
samples = [pygame.sndarray.samples(s) for s in sounds]

selector = 0
clock = pygame.time.Clock()
while(1):
  for event in pygame.event.get():
    if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
      libpd_release()
      pygame.quit()
      sys.exit()
  
  if rotary != None:
    if a.rotary == 8:
      old_switch = switch
      switch = rotary.get_switch_value()
      if old_switch != switch:
        libpd_message('_host', 'switch', switch)
    for i in range(len(rotary_values)):
      rotary_old_values[i] = rotary_values[i]
      b = rotary.is_button_down(i)
      if b:
        rotary_values[i] = 1
      else:
        rotary_values[i] = 0
      if rotary_old_values[i] != rotary_values[i]:
        libpd_message('_host', 'rotary', i, rotary_values[i])
      button_old_values[i] = button_values[i]
      button_values[i] = rotary.get_encoder_value(i)
      if button_old_values[i] != button_values[i]:
        libpd_message('_host', 'button', i, button_values[i])

  # TODO: put UI here

  screen.blit(surface, (0,0))
  pygame.display.flip()
  pygame.display.update()
  
  if not ch.get_queue():
    for x in range(BUFFERSIZE):
      if x % BLOCKSIZE == 0:
        barray = m.process(inbuf)
        outbuf = unpack('h'*(len(barray)//2),barray)
      samples[selector][x][0] = outbuf[(x % BLOCKSIZE) * 2]
      samples[selector][x][1] = outbuf[(x % BLOCKSIZE) * 2 + 1]
    ch.queue(sounds[selector])
    selector = int(not selector)
  clock.tick(40)

