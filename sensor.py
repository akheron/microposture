from microbit import display, accelerometer, sleep
import radio

TX_INTERVAL = 3000


def fade_out():
    running = True
    while running:
        running = False
        for y in range(5):
            for x in range(5):
                value = display.get_pixel(x, y)
                if value > 0:
                    running = True
                    display.set_pixel(x, y, value - 1)
        sleep(200)


def sleep_with_dot(delay=1000, x=2, y=2, brightness=2):
    display.set_pixel(x, y, 0 if display.get_pixel(x, y) else brightness)
    sleep(delay)


def main():
    display.show("S")
    sleep(2000)
    fade_out()

    # Adjust radio parameters:
    # - Change channel and address for potentially less conflicts with other
    #   micro:bits
    # - Hope for a lower power consumption by adjustin power and data rate
    radio.config(channel=43, address=0xA654BB27, power=3, data_rate=radio.RATE_250KBIT)

    # Furthermore, the the radio is turned off between sends in the following
    # main loop to avoid receiving data. I hope turning radio on/off consumes
    # less power than receiving all the time...

    while True:
        x, y, z = accelerometer.get_values()
        radio.on()
        radio.send("xyz:{},{},{}".format(x, y, z))
        radio.off()
        sleep_with_dot(TX_INTERVAL)


main()
