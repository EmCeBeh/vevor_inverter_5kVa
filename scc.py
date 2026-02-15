import paho.mqtt.client as mqtt
import json
from time import sleep
import serial
import threading
serial_lock = threading.Lock()


debug = False
ttyusbname = "/dev/ttyUSB0"
broker = "192.168.178.100"
port = 1883
username = "mqttuser"
password = "mqttpasswort"

client = mqtt.Client()
client.username_pw_set(username, password)
client.connect(broker, port)

# Device info
device_info = {
    "identifiers": ["solar_charge_controller_vevor_5kVa"],
    "name": "Solar Charge Controller",
    "manufacturer": "Vevor",
    "model": "5kVa"
}

# Sensor definition
sensors = [
    {"name": "AC Input Voltage",       "state_topic": "home/scc/ac/input/voltage",         "unit": "V",  "device_class": "voltage", "unique_id": "scc_ac_input_voltage"},
    {"name": "AC Input Frequency",     "state_topic": "home/scc/ac/input/frequency",     "unit": "Hz", "device_class": "frequency", "unique_id": "scc_ac_input_frequency"},
    {"name": "AC Output Voltage",      "state_topic": "home/scc/ac/output/voltage",       "unit": "V",  "device_class": "voltage", "unique_id": "scc_ac_output_voltage"},
    {"name": "AC Output Frequency",    "state_topic": "home/scc/ac/output/frequency",     "unit": "Hz", "device_class": "frequency", "unique_id": "scc_ac_output_frequency"},
    {"name": "AC Output Apparent Power","state_topic":"home/scc/ac/output/apparent_power", "unit": "VA", "device_class": "apparent_power", "unique_id": "scc_ac_output_apparent_power"},
    {"name": "AC Output Power",        "state_topic": "home/scc/ac/output/power",         "unit": "W",  "device_class": "power", "unique_id": "scc_ac_output_power"},
    {"name": "AC Output Relative Power","state_topic":"home/scc/ac/output/power_relative", "unit": "%",  "device_class": None, "unique_id": "scc_ac_output_power_relative"},
    {"name": "AC Bus Voltage",         "state_topic": "home/scc/ac/bus/voltage",          "unit": "V",  "device_class": "voltage", "unique_id": "scc_ac_bus_voltage"},
    {"name": "Battery Voltage",        "state_topic": "home/scc/battery/voltage",         "unit": "V",  "device_class": "voltage", "unique_id": "scc_battery_voltage"},
    {"name": "Battery Charge Current", "state_topic": "home/scc/battery/charge/current",   "unit": "A",  "device_class": "current", "unique_id": "scc_battery_charge_current"},
    {"name": "Battery Capacity",       "state_topic": "home/scc/battery/capacity",        "unit": "%", "device_class": "battery", "unique_id": "scc_battery_capacity"},
    {"name": "Inverter Temperature",   "state_topic": "home/scc/inverter/temperature",   "unit": "°C", "device_class": "temperature", "unique_id": "scc_inverter_temperature"},
    {"name": "Battery PV Current",     "state_topic": "home/scc/battery/pv/current",      "unit": "A",  "device_class": "current", "unique_id": "scc_battery_pv_current"},
    {"name": "PV Voltage",             "state_topic": "home/scc/pv/voltage",             "unit": "V",  "device_class": "voltage", "unique_id": "scc_pv_voltage"},
    {"name": "Battery SCC Voltage",    "state_topic": "home/scc/battery/scc/voltage",    "unit": "V",  "device_class": "voltage", "unique_id": "scc_battery_scc_voltage"},
    {"name": "Battery Discharge Current","state_topic":"home/scc/battery/discharge/current","unit": "A", "device_class": "current","unique_id": "scc_battery_discharge_current"},
    #{"name": "Inverter Status 1",      "state_topic": "home/scc/inverter/status_1",      "unit": None,"device_class": None, "unique_id": "scc_inverter_status_1"},
    {"name": "Battery Offset for Fans Voltage","state_topic":"home/scc/battery/offset_for_fans/voltage","unit":"V","device_class":"voltage","unique_id":"scc_battery_offset_for_fans_voltage"},
    {"name": "Inverter EEPROM Version","state_topic":"home/scc/eeprom_version",          "unit": None,"device_class": None, "unique_id":"scc_inverter_eeprom_version"},
    {"name": "Solar Charge Power",     "state_topic": "home/scc/solar/charge/power",     "unit": "W",  "device_class": "power", "unique_id": "scc_solar_charge_power"},
    #{"name": "Inverter Status 2",      "state_topic": "home/scc/inverter/status_2",      "unit": None,"device_class": None, "unique_id": "scc_inverter_status_2"},
]

# Binary sensor definition
binary_sensors = [
    {"name": "AC charging"           ,  "state_topic": "home/scc/state/ac_charging",            "device_class": "battery_charging", "unique_id": "scc_state_ac_charging",           "attribute": "b0"},
    {"name": "Solar charging"        ,  "state_topic": "home/scc/state/solar_charging",         "device_class": "battery_charging", "unique_id": "scc_state_solar_charging",        "attribute": "b1"},
    {"name": "Charging"              ,  "state_topic": "home/scc/state/charging",               "device_class": "battery_charging", "unique_id": "scc_state_charging",              "attribute": "b2"},
    {"name": "Battery voltage steady",  "state_topic": "home/scc/state/battery_voltage_steady", "device_class": "lock",             "unique_id": "scc_state_battery_voltage_steady","attribute": "b3"},
    {"name": "Load status"           ,  "state_topic": "home/scc/state/load_status",            "device_class": "running",          "unique_id": "scc_state_load_status",           "attribute": "b4"},
    {"name": "Firmware updated"      ,  "state_topic": "home/scc/state/firmware_updated",       "device_class": "update",           "unique_id": "scc_state_firmware_updated",      "attribute": "b5"},
    {"name": "Configuration changed" ,  "state_topic": "home/scc/state/configuration_changed",  "device_class": "update",           "unique_id": "scc_state_configuration_changed", "attribute": "b6"},
    {"name": "SBU priority"          ,  "state_topic": "home/scc/state/sbu_priority",           "device_class": None,               "unique_id": "scc_state_sbu_priority",          "attribute": "b7"},
    {"name": "Dustproof installed"   ,  "state_topic": "home/scc/state/dustproof_installed",    "device_class": "plug",             "unique_id": "scc_state_dustproof_installed",   "attribute": "b8"},
    {"name": "Switched on"           ,  "state_topic": "home/scc/state/switched_on",            "device_class": None,               "unique_id": "scc_state_switched_on",           "attribute": "b9"},
    {"name": "Floating mode"         ,  "state_topic": "home/scc/state/floating_mode",          "device_class": "running",          "unique_id": "scc_state_floating_mode",         "attribute": "b10"}
]

availability_topic = "home/scc/status"
payload_available = "on"
payload_not_available = "off"

# Publish HA discovery config
for sensor in sensors:
    config_topic = f"homeassistant/sensor/{sensor['unique_id']}/config"
    payload = {
    "name": sensor["name"],
    "state_topic": sensor["state_topic"],
    "unit_of_measurement": sensor["unit"],
    "device_class": sensor["device_class"],
    "unique_id": sensor["unique_id"],
    "device": device_info,
    "availability_topic": availability_topic,
    "payload_available": payload_available,
    "payload_not_available": payload_not_available,
}
    client.publish(config_topic, json.dumps(payload), retain=True)

for binary_sensor in binary_sensors:
    config_topic = f"homeassistant/binary_sensor/{binary_sensor['unique_id']}/config"
    payload = {
    "name": binary_sensor["name"],
    "state_topic": binary_sensor["state_topic"],
    "device_class": binary_sensor["device_class"],
    "unique_id": binary_sensor["unique_id"],
    "device": device_info,
    "availability_topic": availability_topic,
    "payload_available": payload_available,
    "payload_not_available": payload_not_available,
    "payload_off": "0",  # vevor reoprts 0s and 1s for status
    "payload_on": "1"
    }
    client.publish(config_topic, json.dumps(payload), retain=True)


{
  "name": "AC Frequency",
  "state_topic": "home/scc/ac/output/frequency",
  "command_topic": "home/scc/ac/set/frequency",
  "unit_of_measurement": "Hz",
  "unique_id": "scc_ac_output_frequency",
  "device": { ... }
}

def crc16_xmodem(data: bytes):
    crc = 0
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else crc << 1
            crc &= 0xFFFF
    return crc.to_bytes(2, "big")


def query(ser, cmd):
    with serial_lock:
        cmd_encoded = cmd.encode()
        print("sending:", cmd_encoded)
        ser.write(cmd_encoded + crc16_xmodem(cmd_encoded) + b"\r")
        #res = ser.read(200)
        res = ser.read_until(b'\r')
        return res.lstrip(b'(').rstrip(b'\r')[:-2]  # remove (, the two checksum bytes, and the \r

def query_all(ser):
    cmds = ["QVFW",        # Main CPU firmware version inquiry
            "QVFW2",       # Another CPU firmware version inquiry
            "QVFW3",       # ???
            "QPI",         # ???
            "QPIGS",       # Inverter general status parameters inquiry
            "QMOD",        # Inverter Mode inquiry
            "QSID",        # The inverter serial number inquiry
            "QPIWS",       # Inverter Warning Status inquiry
            "QPIRI",       # Inverter rated information inquiry
            "QBEQI",       # Battery equalization status parameters inquiry
            "QT",          # ???
            "QDI",         # The default setting value information
            "QFLAG",       # Inverter flag status inquiry
            "QMUCHGCR",    # Enquiry selectable value about max charging current
            "QMCHGCR",     # Enquiry selectable value about max utility charging current
            "QMN",         # Query model name
            "QGMN",        # Query general model name
            "QID"          # The inverter serial number inquiry
            ]

    for cmd in cmds:
        print(cmd)
        res = query(ser, cmd)
        print(res.decode(errors="ignore"))

if not debug:
    ser = serial.Serial(ttyusbname, 2400, timeout=3)
    print(ser.is_open)

alphabet = "abcdefghijklmnopqrstuvxyz" # might be useful as manual groups by letter. Note: sometimes letters missing in manual!

allowed_currents = ["2A (100W)", "10A (500W)", "20A (1000W)"]
AC_current_payload = {
    "name": "Max. AC current",
    "unique_id": "scc_ac_input_current",
    "command_topic": "home/scc/ac/input/current/set",
    "state_topic": "home/scc/ac/input/current",
    "options": allowed_currents,
    "device": device_info,
    "availability_topic": availability_topic,
    "payload_available": payload_available,
    "payload_not_available": payload_not_available
}
client.publish("homeassistant/select/scc_ac_input_current/config", json.dumps(AC_current_payload), retain=True)

allowed_modes = ["Solar first (0)", "Utility first (1)", "Solar & Utility (2)", "Solar only(3)"]   # Cut 0, CSO 1, SNU 2, OSO 3
SCC_mode_payload = {
    "name": "SCC Mode",
    "unique_id": "scc_mode",
    "command_topic": "home/scc/mode/set",
    "state_topic": "home/scc/mode",
    "options": allowed_modes,
    "device": device_info,
    "availability_topic": availability_topic,
    "payload_available": payload_available,
    "payload_not_available": payload_not_available
}

client.publish("homeassistant/select/scc_mode/config", json.dumps(SCC_mode_payload), retain=True)

def on_message(client, userdata, msg):
    if debug:
        print("Message received:", msg.topic, msg.payload)
    if msg.topic == "home/scc/ac/input/current/set":
        message = msg.payload.decode()
        if message in allowed_currents:
            current = message.split("A")[0]
            ack = query(ser, "MUCHGC"+"%0.3d"%int(current)) # send command to inverter
            print("Inverter ack:", ack)
            res = int(query(ser, "QPIRI").decode().split()[13])  # parameter query
            client.publish("home/scc/ac/input/current", '%dA (%dW)'%(res, res*50), retain=True)     #[14] would be max total

    if msg.topic == "home/scc/mode/set":
        message = msg.payload.decode()
        if message in allowed_modes:
            num = allowed_modes.index(message)
            print(num)
            ack = query(ser, "PCP" + "%0.2d" %num)  # send command to inverter
            print("Inverter ack:", ack)
            res = int(query(ser, "QCP").decode())  # parameter query
            print(res)
            mode = allowed_modes[res]
            client.publish("home/scc/mode", mode, retain=True)  # [14] would be max total

client.on_message = on_message
client.subscribe("home/scc/ac/input/current/set")
client.subscribe("home/scc/mode/set")
client.loop_start()


while True:

    if debug:
        print("================ Faking data ===============")
        qpigs_string = b'(000.0 00.0 012.4 50.0 0002 0002 000 382 47.80 000 021 0022 0000 000.0 00.00 00000 01010000 00 00 00000 010' #already removed checksum bytes and \r:   3E\r
    else:
        print("================ READING ===============")
        qpigs_string = query(ser, "QPIGS")

    print('qpigs raw repsonse:', qpigs_string)
    if qpigs_string == b'':
        client.publish(availability_topic, payload_not_available, retain=True)
        print("!ATTENTION! Device NOT available!")
    else:
        client.publish(availability_topic, payload_available, retain=True)
        print("Device Available.")
        qpigs_str = qpigs_string.decode("latin-1")
        data = qpigs_str.split()
        if debug:
            print("Data:", data)
        client.publish("home/scc/ac/input/voltage", data[0])
        client.publish("home/scc/ac/input/frequency", data[1])
        client.publish("home/scc/ac/output/voltage", data[2])
        client.publish("home/scc/ac/output/frequency", data[3])
        client.publish("home/scc/ac/output/apparent_power", data[4])
        client.publish("home/scc/ac/output/power", data[5])
        client.publish("home/scc/ac/output/power_relative", data[6])
        client.publish("home/scc/ac/bus/voltage", data[7])
        client.publish("home/scc/battery/voltage", data[8])
        client.publish("home/scc/battery/charge/current", data[9])
        client.publish("home/scc/battery/capacity", data[10])
        client.publish("home/scc/inverter/temperature", data[11])
        client.publish("home/scc/battery/pv/current", data[12])
        client.publish("home/scc/pv/voltage", data[13])
        client.publish("home/scc/battery/scc/voltage", data[14])
        client.publish("home/scc/battery/discharge/current", data[15])
        #client.publish("home/scc/inverter/status_1", data[16])
        client.publish("home/scc/battery/offset_for_fans/voltage", data[17])
        client.publish("home/scc/inverter/eeprom_version", data[18])
        client.publish("home/scc/solar/charge/power", data[19])
        #client.publish("home/scc/inverter/status_2", data[20])

        b7, b6, b5, b4, b3, b2, b1, b0 = data[16]
        b10, b9, b8 = data[20]

        client.publish("home/scc/state/ac_charging",           b0)
        client.publish("home/scc/state/solar_charging",       b1)
        client.publish("home/scc/state/charging",              b2)
        client.publish("home/scc/state/battery_voltage_steady",b3)
        client.publish("home/scc/state/load_status",           b4)
        client.publish("home/scc/state/firmware_updated",      b5)
        client.publish("home/scc/state/configuration_changed", b6)
        client.publish("home/scc/state/sbu_priority",          b7)
        client.publish("home/scc/state/dustproof_installed",   b8)
        client.publish("home/scc/state/switched_on",           b9)
        client.publish("home/scc/state/floating_mode",         b10)

        if debug:
            print()
            print("Debug info:")
            print("There are %d sensors."%len(sensors))
            print(sensors)
            offs = 0
            for i,dat in enumerate(data[:-1]):
                if i == 16:
                    offs = 1
                else:
                    print(i,i-offs)
                    print(i, sensors[i-offs]['name'], "%s"%dat, sensors[i-offs]['unit'])
            print("==================================================")
    sleep(5)













