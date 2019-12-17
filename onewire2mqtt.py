import ow
import paho.mqtt.client as mqtt
import time

# init MQTT Client
client = mqtt.Client("onewirepi")
client.username_pw_set("majo", password="")
client.connect("nuc1")

# init onewire
ow.init('localhost:4304')
sensorlist = ow.Sensor('/').sensorList()

for sensor in sensorlist:
    print('Device Found')
    print('Address: ' + sensor.address)
    print('Family: ' + sensor.family)
    print('ID: ' + sensor.id)
    print('Type: ' + sensor.type)
    print('Temp: ' + sensor.temperature11)
    sensor_name = "onewire_" + sensor.family + "_" + sensor.id
    config_topic = "homeassistant/sensor/" + sensor_name + "/config"
    state_topic = "homeassistant/sensor/" + sensor_name + "/state"
    device_class = "temperature"
    config_payload = '{"name": "' + sensor_name + '", "device_class": "' + device_class + '", "state_topic": "' + state_topic + '"}'
    client.publish(config_topic, payload=config_payload, qos=1, retain=False)
    time.sleep(0.1)

for sensor in sensorlist:
    print('Sending value for sensor id ' + sensor.id)
    sensor_name = "onewire_" + sensor.family + "_" + sensor.id
    state_topic = "homeassistant/sensor/" + sensor_name + "/state"
    client.publish(state_topic, payload=float(sensor.temperature11), qos=1, retain=False)
    time.sleep(0.1)
