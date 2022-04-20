# receiver.py for ESPNow range testing.

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
from machine import Pin, WDT, SoftI2C
import ssd1306_peter_hinch


i2c = SoftI2C(scl=Pin(5), sda=Pin(4), freq=100000)
display = ssd1306_peter_hinch.SSD1306_I2C(128, 64, i2c)
CYCLE_TIME = 60             #  seconds
REBOOT_DELAY = 5            #  seconds
remote_mac = b'x!\x84{\xde\x80'


def reboot(delay = REBOOT_DELAY):
 #  print a message and give time for user to pre-empt reboot
 #  in case we are in a (battery consuming) boot loop
    print (f'Rebooting device in {delay} seconds (Ctrl-C to escape).')
 #  or just machine.deepsleep(delay) or lightsleep()
    utime.sleep(delay)
    machine.reset()


try:
    print ('you have 5 seconds to do Ctrl-C if you want to edit the program')
    utime.sleep(5)

    wdt = WDT(timeout = (CYCLE_TIME + 10)  * 1000)  # enable it with a timeout
    wdt.feed()

    w0 = network.WLAN(network.STA_IF)
    print (w0.config('mac'))
    e0 = espnow.ESPNow()

 #  these functions generate exceptions on error - always return None
    e0.init()
 #  so that we wake up and reset the wdt before it times out
    e0.config(timeout = (CYCLE_TIME) * 1000)
    e0.add_peer(remote_mac)
except KeyboardInterrupt as err:
    raise err #  use Ctrl-C to exit to micropython repl
except Exception as err:
    print ('Error initialising espnow:', err)
    reboot()


while True:
    try:
        w0.active(True) # the radio is left going

        print ('waiting for a msg from the remote')

        for mac, msg in e0:
            wdt.feed()

            if mac == remote_mac:
                msg = msg.decode('utf-8')

                print (msg)

                break #  out of the for loop!!
            elif mac == None:
                print ('no peers found')
                utime.sleep(5)
                break
            else:
                print ('Recv from {}: "{}"'.format(mac, msg))
                utime.sleep(5)
                break

        rssi_time_ms =  (e0.peers[b'x!\x84{\xde\x80'])
        rssi = (rssi_time_ms[0])
        print (rssi)

#        w0.active(False) #  the radio is left going

     #  display the RSSI
        display.fill(0)
        display.text(f'RSSI = {rssi:.0f}' + 'dBm', 0, 24)
        display.show()

    except KeyboardInterrupt as err:
        raise err #  use Ctrl-C to exit to micropython repl
    except Exception as err:
     #  all other exceptions cause a reboot
        print ('Error during execution:', err)
        reboot()
