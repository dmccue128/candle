import board
import analogio
import digitalio
import time

led = digitalio.DigitalInOut(board.A4)
led.direction = digitalio.Direction.OUTPUT

led_sensor = analogio.AnalogIn(board.A3)

reed_switch = digitalio.DigitalInOut(board.D0)
reed_switch.direction = digitalio.Direction.INPUT
reed_switch.pull = digitalio.Pull.UP

tilt_switch = digitalio.DigitalInOut(board.D2)
tilt_switch.direction = digitalio.Direction.INPUT
tilt_switch.pull = digitalio.Pull.UP

# minimum change in LED reading to signal cooling
trigger_delta = 150
last_led_reading = 0
is_on = False


def switch_on():
    global led, is_on
    led.value = True
    is_on = True


def switch_off():
    global led, is_on
    led.value = False
    is_on = False


def match_detected():
    return not reed_switch.value


def sample_led():
    sum = 0
    for i in range(1, 256):
        sum += (led_sensor.value - sum) / i
    return sum


def tilted():
    return tilt_switch.value


def puff_detected():
    global last_led_reading
    # A puff of air on the LED will temporarily drop temperature,
    # which will drop voltage
    led_reading = sample_led()
    delta = led_reading - last_led_reading
    is_triggered = delta > trigger_delta
    print("delta=", delta)
    last_led_reading = led_reading
    return is_triggered


def set_threshold():
    global last_led_reading
    switch_on()
    for i in range(10):
        last_led_reading = sample_led()
    switch_off()


set_threshold()
while True:
    time.sleep(.15)
    if is_on:
        # Candle is lit
        if tilted() or puff_detected():
            switch_off()
    else:
        # Candle is dark
        if tilted() or match_detected():
            switch_on()
