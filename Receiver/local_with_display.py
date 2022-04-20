import network
from esp import espnow
import utime
import machine
from machine import Pin, WDT, SoftI2C
import ssd1306_peter_hinch


i2c = SoftI2C(scl=Pin(5), sda=Pin(4), freq=100000)
display = ssd1306_peter_hinch.SSD1306_I2C(128, 64, i2c)
CYCLE_TIME = 70             # make cycle time 5 seconds longer than the repeater
REBOOT_DELAY = 5            # seconds
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

     #  display the battery voltage
        display.fill(0)
        display.text('{:^16s}'.format(''), 0, 0)
        display.text('{:^16s}'.format('RSSI:'), 0, 16)
        display.text('{:^16s}'.format(str(rssi)), 0, 32)
        display.show()

#        utime.sleep(10) #  so that you see the battery voltage

    except KeyboardInterrupt as err:
        raise err #  use Ctrl-C to exit to micropython repl
    except Exception as err:
     #  all other exceptions cause a reboot
        print ('Error during execution:', err)
        reboot()
