import pyownet
import paho.mqtt.client as mqtt
import time
from onewire2mqtt_config import *

dict_ids_names = {"28.AA13CA381401": "01",
                  "28.AAFAB1381401": "02",
                  "28.AA88AE381401": "03",
                  "28.AA6A95381401": "04",
                  "28.AAB698381401": "05",
                  "28.AA350B381401": "06_estrich_bad_og",
                  "28.AAAA15381401": "07_estrich_kueche",
                  "28.AA7DD2381401": "08",
                  "28.AA86E0381401": "09",
                  "28.AAE39C381401": "10",
                  "28.AA16F0381401": "11",
                  "28.AA7ECD381401": "12",
                  "28.AAC586381401": "13",
                  "28.AA5BD3381401": "14_estrich_wohnzimmer",
                  "28.FF434F601705": "15_estrich_wc_1",
                  "28.AA8C2A381401": "16_estrich_esszimmer",
                  "28.AA10B5381401": "17",
                  "28.AA1D32381401": "18",
                  "28.AA172D381401": "19",
                  "28.AA9337381401": "20_estrich_bad_eg",
                  "28.AAA4DA371401": "21_estrich_wc_2",
                  "28.AA9C461A1302": "22",
                  "28.AA3C431A1302": "23",
                  "28.AAB2CD191302": "24",
                  "28.AA71DC191302": "25_estrich_schlafzimmer",
                  "28.AAC7471A1302": "26",
                  "28.45950C161301": "serverschrank"
                  }

# init MQTT Client
client = mqtt.Client(client_name )
client.username_pw_set(mqtt_user, password=mqtt_passwd)

# init onewire
owproxy = pyownet.protocol.proxy(host="localhost", port=4304)
sensorlist = owproxy.dir()
print(sensorlist)

# delete old sensor entry from tesing phase. Case Sensitive => Capital Hex Letters!
#client.publish("homeassistant/sensor/onewire_28_45950C161301/config", payload='', qos=1, retain=False)

def create_sensor_name(sensor, dict_ids_names):
    # translate with dict_ids_name
    sensor_base_name = dict_ids_names.get(sensor.replace("/",""),sensor.replace("/","").replace(".","_"))
    sensor_name = "onewire_" + sensor_base_name
    return sensor_name

def create_config_topic(sensor_name):
    return "homeassistant/sensor/" + sensor_name + "/config"

def create_state_topic(sensor_name):
    return "homeassistant/sensor/" + sensor_name + "/state"

# delete sensors in home assistant via MQTT Discovery
client.connect(mqtt_host)
# onewire sensors
for sensor in sensorlist:
    try:
        print('Device Found')
        print('Address: ' + sensor.replace("/",""))
        value = owproxy.read(sensor + 'temperature12')
        if float(value) > 80.0:
            time.sleep(0.1)
            value = owproxy.read(sensor + 'temperature12')
            if float(value) > 80.0:
                print('value not feasable, above 80C')
                time.sleep(0.1)
                continue
        sensor_name = create_sensor_name(sensor, dict_ids_names)
        print('Sensor Name: ' + sensor_name)
        print('Value: {}'.format(float(value)))
        print('----------')
        config_topic = create_config_topic(sensor_name)
        config_payload = ''
        client.publish(config_topic, payload=config_payload, qos=1, retain=False)
    except Exception as e:
        print('Error during config of sensor ' + sensor.replace("/",""))
        print(e)
    time.sleep(1)

# close mqtt connection
client.disconnect()

print('finished')
