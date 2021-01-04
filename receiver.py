from microbit import Image, button_a, display, sleep
import math
import radio
import utime

# 3-dimensional vector operations


class Vec3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def length2(self):
        return self.x * self.x + self.y * self.y + self.z * self.z

    def length(self):
        return math.sqrt(self.length2())

    def __str__(self):
        return "[{}, {}, {}]".format(self.x, self.y, self.z)


def vec3_avg(vecs):
    return Vec3(sum(v.x for v in vecs), sum(v.y for v in vecs), sum(v.z for v in vecs))


def vec3_dot(vec_a, vec_b):
    return vec_a.x * vec_b.x + vec_a.y * vec_b.y + vec_a.z * vec_b.z


def vec3_angle(vec_a, vec_b):
    return math.acos(
        vec3_dot(vec_a, vec_b) / math.sqrt(vec_a.length2() * vec_b.length2())
    )


# Time helpers


def now():
    return utime.ticks_ms()


def since(ms):
    return utime.ticks_diff(now(), ms)


# Display helpers


def clear():
    display.clear()


def dots(count):
    for y in range(5):
        for x in range(5):
            if count > 0:
                display.set_pixel(x, y, 6)
                count -= 1
            else:
                display.set_pixel(x, y, 0)


def blink():
    if display.get_pixel(0, 0):
        # Turn all leds off
        value = 0
    else:
        # Set all leds to max
        value = 9

    for y in range(5):
        for x in range(5):
            display.set_pixel(x, y, value)


def point_to_a():
    display.show(Image.ARROW_W)


# Radio data handling


def parse_acceleration(data):
    packet_prefix = "xyz:"
    if not data:
        return

    if not data.startswith(packet_prefix):
        return

    value = data[len(packet_prefix) :].split(",")
    if len(value) != 3:
        return

    try:
        result = [int(x) for x in value]
    except ValueError:
        return

    return Vec3(*result)


def clear_receive_queue():
    while radio.receive():
        pass


def receive(timeout=10000):
    start = now()
    while since(start) < timeout:
        value = parse_acceleration(radio.receive())
        if value:
            return value
        sleep(100)

    raise TimeoutError()


def maybe_receive():
    return parse_acceleration(radio.receive())


# Program states


class TimeoutError(Exception):
    pass


def start():
    point_to_a()
    while not button_a.was_pressed():
        sleep(100)


def calibrate():
    clear_receive_queue()
    values = []
    for i in range(5):
        dots(5 - i)
        values.append(receive(timeout=8000))
    clear()

    # use the last 3 measurements for calibration
    return vec3_avg(values[-3:])


ANGLE_THRESHOLD = 3
HUNCHES_THRESHOLD = 3


def run(down):
    last_seen = now()
    hunches = 0

    while True:
        value = maybe_receive()
        if value:
            last_seen = now()
            angle = round(abs(math.degrees(vec3_angle(down, value))))
            if angle >= ANGLE_THRESHOLD:
                hunches += 1
            else:
                hunches = 0
            dots(angle)

        if hunches >= HUNCHES_THRESHOLD:
            blink()

        if since(last_seen) > 10000:
            raise TimeoutError()

        sleep(300)


def main():
    radio.config(channel=43, address=0xA654BB27, power=3, data_rate=radio.RATE_250KBIT)
    radio.on()

    while True:
        try:
            start()
            down = calibrate()
            run(down)
        except TimeoutError:
            pass


main()
