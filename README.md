The idea with this is that you can load puredata patches, headless, that can interact with pi GPIO using simple messages.

You can set your hardware interface, by using CLI flags (run `pipdloader --help`.)

The options stack, so if you wanted lots of IO and to add to the lib-dir:

```
pipdloader -l lib -l ~/pd  -i 6 -i 7 -i 8 -o 9 -o 10 demo/demo.pd
```

results in:

```
file='demo/demo.pd'
input=[6, 7, 8]
output=[9, 10]
lib=['lib', 'demo']
```


## dependencies

In order to run it, you will need `pylibpd`:


```
git clone --recursive https://github.com/libpd/libpd.git
cd libpd/python
make
sudo make install
```

You will also need these libs for various supported hardware:


```
sudo apt-get install -y puredata python3-pip python3-setuptools python3-pygame python3-pil
sudo pip3 install python-osc Adafruit-Blinka adafruit-circuitpython-ssd1306
```

## usage

All messages are routed through `_host` and `_patch`, and the host program isn't even needed, so you can can dev with demo/emulator.pd open (use plugdata, as it has some extended stuff, like knobs/buttons in it) and no hardware or python is required.
