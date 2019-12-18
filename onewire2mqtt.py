import ow
import paho.mqtt.client as mqtt
import time
from onewire2mqtt_config import *

dict_ids_names = {"28.AA13CA381401": "01",
                  "28.AAFAB1381401": "02",
                  "28.AA88AE381401": "03",
                  "28.AA6A95381401": "04",
                  "28.AAB698381401": "05",
                  "28.AA350B381401": "06",
                  "28.AAAA15381401": "07",
                  "28.AA7DD2381401": "08",
                  "28.AA86E0381401": "09",
                  "28.AAE39C381401": "10",
                  "28.AA16F0381401": "11",
                  "28.AA7ECD381401": "12",
                  "28.AAC586381401": "13",
                  "28.AA5BD3381401": "14",
                  "28.FF434F601705": "15",
                  "28.AA8C2A381401": "16",
                  "28.AA10B5381401": "17",
                  "28.AA1D32381401": "18",
                  "28.AA172D381401": "19",
                  "28.AA9337381401": "20",
                  "28.AAA4DA371401": "21",
                  "28.AA9C461A1302": "22",
                  "28.AA3C431A1302": "23",
                  "28.AAB2CD191302": "24",
                  "28.AA71DC191302": "25",
                  "28.AAC7471A1302": "26",
                  "28.45950C161301": "serverschrank",
                  }

# init MQTT Client
client = mqtt.Client(client_name )
client.username_pw_set(mqtt_user, password=mqtt_passwd)
client.connect(mqtt_host)

# init onewire
ow.init('localhost:4304')
sensorlist = ow.Sensor('/').sensorList()

def create_sensor_name(family, id_, dict_ids_names):
    # translage with dict_ids_name
    sensor_base_name = dict_ids_names.get(family + "." + id_,"id_" + family + "_" + id_)
    sensor_name = "onewire_" + sensor_base_name
    return sensor_name

for sensor in sensorlist:
    print('Device Found')
    print('Address: ' + sensor.address)
    print('Family: ' + sensor.family)
    print('ID: ' + sensor.id)
    print('Type: ' + sensor.type)
    print('Temp: ' + sensor.temperature11)
    sensor_name = create_sensor_name(sensor.family, sensor.id, dict_ids_names)
    print(sensor_name)
    config_topic = "homeassistant/sensor/" + sensor_name + "/config"
    state_topic = "homeassistant/sensor/" + sensor_name + "/state"
    device_class = "temperature"
    config_payload = '{"name": "' + sensor_name + '", "device_class": "' + device_class + '", "state_topic": "' + state_topic + '"}'
    client.publish(config_topic, payload=config_payload, qos=1, retain=False)
    time.sleep(0.1)

for sensor in sensorlist:
    print('Sending value for sensor id ' + sensor.id)
    sensor_name = create_sensor_name(sensor.family, sensor.id, dict_ids_names)
    state_topic = "homeassistant/sensor/" + sensor_name + "/state"
    client.publish(state_topic, payload=float(sensor.temperature11), qos=1, retain=False)
    time.sleep(0.1)
