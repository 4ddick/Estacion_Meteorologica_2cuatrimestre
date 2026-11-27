import dht, time
from machine import Pin

sensor = dht.DHT11(Pin(4))

for i in range(10):
    try:
        sensor.measure()
        print("Temp:", sensor.temperature(), "Humedad:", sensor.humidity())
    except Exception as e:
        print("Error:", e)
    time.sleep(2)