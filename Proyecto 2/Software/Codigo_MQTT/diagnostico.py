import network, time
import config

wlan = network.WLAN(network.STA_IF)
wlan.active(False)
time.sleep(1)
wlan.active(True)
time.sleep(1)

print("Nombre en config:", repr(config.WIFI_SSID), "largo:", len(config.WIFI_SSID))
print("Largo de la clave:", len(config.WIFI_PASS))

print("--- Redes que ve la placa ---")
for r in wlan.scan():
    print(r[0], "canal:", r[2], "señal:", r[3], "seguridad:", r[4])

print("--- Conectando ---")
wlan.config(txpower=8.5)
wlan.connect(config.WIFI_SSID, config.WIFI_PASS)
for i in range(20):
    print(i * 2, "s  estado:", wlan.status())
    if wlan.isconnected():
        break
    time.sleep(2)
print(wlan.ifconfig())