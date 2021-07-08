# Sigfox Monarch Beacon Generator
This repository contains a simple python script to generate Sigfox Monarch beacons and to transmit them with any SoapySDR-compatible and transmit-capable software defined radio.

![Spectrogram of RC1 Monarch Beacon](img/monarch_specgram_rc1.png)

Using the script, you can easily check if your Sigfox end device is capable of detecting Monarch beacons.
The signal generation was developed based on the official [Monarch physical interface description and hardware device requirements](https://www.disk91.com/wp-content/uploads/2019/09/Monarch_physical_interface_description_and_device_HW_requirements_v1.2_external.pdf) document by Sigfox and was confirmed to work with Sigfox Monarch-capable end devices.

## Example
Transmit Sigfox RC3 Monarch beacon every 10 seconds:
```
./transmit.py -r rc3 -i 10
```