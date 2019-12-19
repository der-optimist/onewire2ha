import pyownet
import paho.mqtt.client as mqtt
import time
from onewire2mqtt_config import *
# knx stuff
import asyncio
from xknx import XKNX
from xknx.io import GatewayScanner, Tunnel
from xknx.knx import DPTArray, DPTTemperature, GroupAddress, PhysicalAddress, Telegram
#from xknx.devices import Sensor
import random

dict_ids_names = {"28.AA13CA381401": "01",
                  "28.AAFAB1381401": "02",
                  "28.AA88AE381401": "03",
                  "28.AA6A95381401": "04",
                  "28.AAB698381401": "05",
                  "28.AA350B381401": ["06_estrich_bad_og","12/0/12"],
                  "28.AAAA15381401": ["07_estrich_kueche","12/0/0"],
                  "28.AA7DD2381401": "08",
                  "28.AA86E0381401": "09",
                  "28.AAE39C381401": "10",
                  "28.AA16F0381401": "11",
                  "28.AA7ECD381401": "12",
                  "28.AAC586381401": "13",
                  "28.AA5BD3381401": ["14_estrich_wohnzimmer","12/0/2"],
                  "28.FF434F601705": ["15_estrich_wc_1","12/0/6"],
                  "28.AA8C2A381401": ["16_estrich_esszimmer","12/0/1"],
                  "28.AA10B5381401": "17",
                  "28.AA1D32381401": "18",
                  "28.AA172D381401": "19",
                  "28.AA9337381401": ["20_estrich_bad_eg","12/0/4"],
                  "28.AAA4DA371401": "21_estrich_wc_2",
                  "28.AA9C461A1302": "22",
                  "28.AA3C431A1302": "23",
                  "28.AAB2CD191302": "24",
                  "28.AA71DC191302": ["25_estrich_schlafzimmer","12/0/3"],
                  "28.AAC7471A1302": "26",
                  "28.45950C161301": "serverschrank"
                  }


# wait for OWFS and MQTT, especially after reboot or 
print('Will sleep to give OWFS and MQTT some time...')
#time.sleep(60)

# init MQTT Client
client = mqtt.Client(client_name )
client.username_pw_set(mqtt_user, password=mqtt_passwd)

# init onewire
owproxy = pyownet.protocol.proxy(host="localhost", port=4304)
sensorlist = owproxy.dir()
print(sensorlist)

# init knx
xknx = XKNX()

# delete old sensor entry from tesing phase. Case Sensitive => Capital Hex Letters!
#client.publish("homeassistant/sensor/onewire_28_45950C161301/config", payload='', qos=1, retain=False)

def create_sensor_name_and_ga(sensor, dict_ids_names):
    # translage with dict_ids_name
    ga = None
    sensor_base_name = dict_ids_names.get(sensor.replace("/",""),sensor.replace("/","").replace(".","_"))
    if type(sensor_base_name) == list:
        sensor_base_name = sensor_base_name[0]
        ga = sensor_base_name[1]
    sensor_name = "onewire_" + sensor_base_name
    return sensor_name, ga

def create_config_topic(sensor_name):
    return "homeassistant/sensor/" + sensor_name + "/config"

def create_state_topic(sensor_name):
    return "homeassistant/sensor/" + sensor_name + "/state"

# define sensors in home assistant via MQTT Discovery
client.connect(mqtt_host)
for sensor in sensorlist:
    try:
        print('Device Found')
        print('Address: ' + sensor.replace("/",""))
        value = owproxy.read(sensor + 'temperature11')
        sensor_name, ga = create_sensor_name_and_ga(sensor, dict_ids_names)
        print('Sensor Name: ' + sensor_name)
        print('Value: {}'.format(float(value)))
        print('----------')
        config_topic = create_config_topic(sensor_name)
        state_topic = create_state_topic(sensor_name)
        device_class = "temperature"
        config_payload = '{"name": "' + sensor_name + '", "device_class": "' + device_class + '", "state_topic": "' + state_topic + '"}'
        client.publish(config_topic, payload=config_payload, qos=1, retain=False)
    except Exception as e:
        print('Error during config of sensor ' + sensor.replace("/",""))
        print(e)
    time.sleep(0.1)
time.sleep(2)


# read and send values to mqtt and knx
async def main():
    xknx = XKNX()
    gatewayscanner = GatewayScanner(xknx)
    gateways = await gatewayscanner.scan()

    if not gateways:
        print("No Gateways found")
        return

    gateway = gateways[0]
    src_address = PhysicalAddress("15.15.249")

    print("Connecting to {}:{} from {}".format(
        gateway.ip_addr,
        gateway.port,
        gateway.local_ip))

    tunnel = Tunnel(
        xknx,
        src_address,
        local_ip=gateway.local_ip,
        gateway_ip=gateway.ip_addr,
        gateway_port=gateway.port)

    await tunnel.connect_udp()
    await tunnel.connect()

    
    
    

    for sensor in sensorlist:
        try:
            sensor_name, ga = create_sensor_name_and_ga(sensor, dict_ids_names)
            state_topic = create_state_topic(sensor_name)
            value = owproxy.read(sensor + 'temperature11')
            print('Sending value for sensor ' + sensor.replace("/","") + " ({}): {}".format(sensor_name,float(value)))
            await tunnel.send_telegram(Telegram(GroupAddress(ga), payload=DPTArray(DPTTemperature().to_knx(float(value)))))
            client.publish(state_topic, payload=float(value), qos=1, retain=False)
        except Exception as e:
            print('Error during sending value of sensor ' + sensor.replace("/","") + ":")
            print(e) 
        time.sleep(0.1)
    
    # close mqtt connection
    client.disconnect()
    
    # close knx tunnel
    #await tunnel.connectionstate()
    await tunnel.disconnect()
    print('finished')

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()