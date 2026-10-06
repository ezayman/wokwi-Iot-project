from machine import Pin, PWM
import network
import time
from umqtt.simple import MQTTClient

# Hardware
pir = Pin(27, Pin.IN)

red_led = Pin(23, Pin.OUT)      # Motion detected
green_led = Pin(22, Pin.OUT)    # No motion

buzzer = PWM(Pin(21))
buzzer.duty(0)

motion_count = 0
previous_motion = 0

# WiFi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)

print("Connecting to WiFi", end="")
wifi.connect("Wokwi-GUEST", "")

while not wifi.isconnected():
    print(".", end="")
    time.sleep(0.5)

print("\nConnected!")
print("IP:", wifi.ifconfig()[0])

# -------------------------
# ThingSpeak MQTT setup
# -------------------------
BROKER = "mqtt3.thingspeak.com"
PORT = 1883

CLIENT_ID = "NAY2Ny8oChcqIBAZBCkGEQM"
USERNAME = "NAY2Ny8oChcqIBAZBCkGEQM"
PASSWORD = "ejQ6Dz1cjhjXzznTCsUdRxZh"

CHANNEL_ID = "3516883"

TOPIC = "channels/{}/publish/fields/field1".format(CHANNEL_ID)

client = MQTTClient(
    CLIENT_ID,
    BROKER,
    port=PORT,
    user=USERNAME,
    password=PASSWORD
)

print("Connecting to ThingSpeak MQTT...")
client.connect()
print("MQTT connected")

# Timer for ThingSpeak
last_send = time.ticks_ms()

while True:

    # -------------------------
    # Read sensor frequently
    # -------------------------

    motion = pir.value()

    if motion == 1:

        red_led.on()
        green_led.off()
        
        print("Motion detected -> LED ON")
        print("No motion - Total events:", motion_count)

        # Count only when motion starts
        if previous_motion == 0:

            motion_count += 1

            print("Motion detected!")
            print("Motion event #", motion_count)

            # Short buzzer sound
            buzzer.freq(1000)
            buzzer.duty(512)
            time.sleep(0.3)
            buzzer.duty(0)

        # -------------------------------------
        # Publish to ThingSpeak MQTT every 16 s
        # -------------------------------------

        if time.ticks_diff(time.ticks_ms(), last_send) >= 16000:

            print("ThingSpeak MQTT - Ready to publish the Event")

            try:
                payload = str(motion)
                client.publish(TOPIC, payload)
                print("ThingSpeak MQTT - Published Event:", payload)
            except OSError as e:
                print("ThingSpeak Error - local system still running")
                print("MQTT connection lost:", e)

            last_send = time.ticks_ms()

    else:
        red_led.off()
        green_led.on()
        print("No motion -> LED OFF")


    previous_motion = motion

    # Local sensor sampling
    time.sleep(3)