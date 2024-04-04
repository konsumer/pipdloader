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

In order to run it, you will need some dependencies. You can install themn with [setup.sh](setup.sh) or just have a look at what it installs, and do it however you like.



## usage

All messages are routed through `_host` and `_patch`, and the host program isn't even needed, so you can can dev with demo/emulator.pd open (use plugdata, as it has some extended stuff, like knobs/buttons in it) and no hardware or python is required.
