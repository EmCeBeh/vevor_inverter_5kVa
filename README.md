# Vevor inverter 5kVa solar charge converter / inverter.

Simple python implementation of a 5kVa [Vevor](https://www.vevor.de/off-grid-solar-wechselrichter-c_10764/5kva-pwm-48v-solar-munltifunktionale-pwm-wechselrichter-reine-sinuswelle-p_010315127318?srsltid=AfmBOopH9QsMyPDpEv0_Cwvub3Y8v6hG3T7l9vC8orV8eV6z1LaPZDgI) (Voltronic rebrand).

Reads and writes basic values and published via MQTT to they can be read by e.g., Home Assistant. Written for readability, not efficiency.
Should even run on raspberry pi zero (W).
Currently running on Raspi3, which does not support a popular docker image.

Vevor uses almost the same commands as [Voltronic and AXPERT KS&MKS&V](https://ftps.voltronic.com.tw/E/Easunpower-93CB312922AC474787C6/RS232%20通訊協議(communication%20protocol)/Axpert%20KS&MKS&V%20RS232%20Protocol-C(20170821).pdf), but tiny differences may cause inital problems for the uniitiated.
Thus, i made my own.

Implementation:
![image](https://github.com/EmCeBeh/vevor_inverter_5kVa/blob/main/HA%20Implementation.png)

Possible dashboard
![image](https://github.com/EmCeBeh/vevor_inverter_5kVa/blob/main/HA%20Overview.png)
