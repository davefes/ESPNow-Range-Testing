# sender.py for ESPNow range testing.

# The MIT License (MIT)
#
# Copyright (c) 2022 David Festing
# Copyright (c) 2022 Glenn Moloney https://github.com/glenn20/micropython-espnow-images
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


# V1 20 April 2022


import network
from esp import espnow
import utime
import machine
from machine import Pin, WDT


CYCLE_TIME = 60             #  seconds
REBOOT_DELAY = 5            #  seconds
local_mac = b'\x08:\xf2\xab\xe2\x0c'
pin33 = Pin(33, Pin.OUT)
pin33.off()


def reboot(delay = REBOOT_DELAY):
 #  print a message and give time for user to pre-empt reboot
 #  in case we are in a (battery consuming) boot loop
    print (f'Rebooting device in {delay} seconds (CTRL-C to escape).')
 #  or just machine.deepsleep(delay) or lightsleep()
    utime.sleep(delay)
    machine.reset()


try:
    print ('you have 5 seconds to do Ctrl C if you want to edit the program')
    utime.sleep(5)

    wdt = WDT(timeout = (CYCLE_TIME + 10) * 1000)  # enable it with a timeout
    wdt.feed()

    w0 = network.WLAN(network.STA_IF)
    print (w0.config('mac'))
    e0 = espnow.ESPNow()
#    print (e0)

 #  these functions generate exceptions on error - always return None
    e0.init()

 #  so that we wake up and reset the wdt before it times out
    e0.config(timeout = CYCLE_TIME * 1000)

    e0.add_peer(local_mac)
except KeyboardInterrupt as err:
    raise err #  use Ctrl-C to exit to micropython repl
except Exception as err:
    print ('Error initialising espnow:', err)
    reboot()

try:
    while True:

     #  heartbeat, this also slows the loop down
        pin33.on()
        utime.sleep_ms(150)
        pin33.off()
        utime.sleep_ms(150)
        pin33.on()
        utime.sleep_ms(150)
        pin33.off()

        status = 'we have a link'

        w0.active(True) #  turn on radio only when needed
     #  if you want to save more battery, set sync=False
     #  at cost of not knowing if message was received.
        retval = e0.send(local_mac, status, True)
        w0.active(False)

        wdt.feed()

        utime.sleep(10)
except KeyboardInterrupt as err:
    raise err #  use Ctrl-C to exit to micropython repl
except Exception as err:
    print ('Error during execution:', err)
    reboot()
