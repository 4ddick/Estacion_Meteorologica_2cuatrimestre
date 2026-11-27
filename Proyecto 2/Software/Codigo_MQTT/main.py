import network, time, math
import dht
from machine import Pin
from umqtt.simple import MQTTClient
import config

PIN_DHT = 4
INTERVALO = 60          # segundos entre mediciones (versión final: 25 * 60)

sensor = dht.DHT11(Pin(PIN_DHT))


def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        return wlan
    wlan.active(False)
    time.sleep(1)
    wlan.active(True)
    wlan.config(txpower=8.5)
    time.sleep(1)
    wlan.connect(config.WIFI_SSID, config.WIFI_PASS)
    intentos = 0
    while not wlan.isconnected() and intentos < 30:
        time.sleep(0.5)
        intentos += 1
    return wlan


def leer_dht():
    for intento in range(3):
        try:
            sensor.measure()
            return sensor.temperature(), sensor.humidity()
        except OSError:
            time.sleep(2)
    return None, None


def calcular_sensacion(temp, hum):
    # Temperatura aparente (Steadman, sin viento)
    e = (hum / 100) * 6.105 * math.exp(17.27 * temp / (237.7 + temp))
    return temp + 0.33 * e - 4.0


def publicar(temp, hum, sens):
    client = MQTTClient("estacion-c3", config.MQTT_BROKER, port=config.MQTT_PORT)
    client.connect()
    client.publish(b"estacion/temperatura", str(temp).encode(), retain=True)
    client.publish(b"estacion/humedad", str(hum).encode(), retain=True)
    client.publish(b"estacion/sensacion", str(sens).encode(), retain=True)
    client.disconnect()


time.sleep(2)   # el DHT11 necesita unos segundos al encender

while True:
    # 1) primero el sensor, con el WiFi sin usar
    temp, hum = leer_dht()

    if temp is None:
        print("Error al leer el DHT11")
    else:
        sens = round(calcular_sensacion(temp, hum), 1)
        print("Temp:", temp, "C  Humedad:", hum, "%  Sensacion:", sens, "C")

        # 2) después el WiFi y MQTT
        wlan = conectar_wifi()
        if wlan.isconnected():
            try:
                publicar(temp, hum, sens)
                print("publicado")
            except Exception as e:
                print("Error MQTT:", e)
        else:
            print("Sin WiFi")

    time.sleep(INTERVALO)