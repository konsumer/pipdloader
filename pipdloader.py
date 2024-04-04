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

def list_of_ints(arg):
  return list(map(int, arg.split(',')))

args.add_argument('file', help='Puredata file to load', default='MAIN.pnd')
args.add_argument('-i', '--input', help='GPIO inputs', type=list_of_ints)
args.add_argument('-o', '--output', help='GPIO outputs', type=list_of_ints)
args.add_argument('-s', '--oled', action='store_true', help='Enable i2c ssd1306 128x64 OLED')
args.add_argument('-r', '--rotary', type=int, help='Enable i2c 4/8-encoder', choices=[4,8])

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

if a.rotary:
  rotary = M58Encoder(i2c)
  rotary_values = numpy.zeros(a.rotary)


def hook_message(name, command, *args):
  print(command, args)
  # TODO handle commands

def hook_print(s):
  o = s.strip()
  if len(o):
    print(o)

"""
TODO

noteon(int channel, int pitch, int velocity);
controlchange(int channel, int controller, int value);
programchange(int channel, int value);
pitchbend(int channel, int value);
aftertouch(int channel, int value);
polyaftertouch(int channel, int pitch, int value);
midibyte(int port, int byte);
sysex(int port, int byte);
sysrealtime(int port, int byte);
"""

libpd_set_print_callback(hook_print)
libpd_set_message_callback(hook_message)
libpd_subscribe('_patch')
libpd_add_to_search_path(dirname(__file__) + "/lib")

screen = pygame.display.set_mode((640, 480), DOUBLEBUF|HWSURFACE, 16)
# screen = pygame.display.set_mode((640, 480), FULLSCREEN | DOUBLEBUF, 16)
surface = pygame.Surface(screen.get_size())
surface = surface.convert()
surface.fill((0,0,0))
pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])
pygame.display.set_caption('BellaSynth')

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
i = 0
while(1):
  for event in pygame.event.get():
    if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
      libpd_release()
      pygame.quit()
      sys.exit()

  # TODO: put UI here
  # TODO: check hardware and send messages to _host on changes

  screen.blit(surface, (0,0))
  pygame.display.flip()
  pygame.display.update()

  i = i + 1
  if i % 10 == 1:
    libpd_message('_host', 'rotary', 0, int(random() * 255))
  
  libpd_message('_host', 'button', 0, i % 2)
  
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

