# 3D-scanner-web-app
## Project Overview
This project aims to provide an alternative software solution for a 3D scanner that will allow the creation 3D models necessary for 3D printing via principles of photogrammetry. The solution will provide a relatively fast method of getting pictures of objects and people, compared to conventional 3D scanning technologies. This is beneficial for those who need to scan patients who may not be able to sit/stand still for long periods of time. The final product is portable and flexible to allow use from many devices and platforms. Raspberry Pis and their Pi cameras are used to take photos of the models, so the product is lightweight and portable, but still powerful enough to create detailed models. The Pi cameras will be approximately synchrononized using a parallel SSH library for Python. One of the Pis broadcasts a standalone network and web server to host the web app. 

## Installation
### Updating and enabling interfaces on Raspberry Pis
The following installations steps are to be performed on **_all_** Pis.

**1. Upgrade OS and firmware on Pi**

Connect the Pi to an Internet connection (direct Ethernet connection from Pi to router or through [Wi-Fi](https://www.raspberrypi.org/documentation/configuration/wireless/). Run the following commands:
```
sudo apt-get update
sudo apt-get dist-upgrade
```
**2. Enable interfaces for SSH and camera**

From the terminal, run the following command to open the Raspbian configuration menu:
```
sudo raspi-config
```

Enter the `Interfacing options` menu and enable SSH (should be enabled by default but check again) and camera utilities.

**3. Change hostnames**

While in Raspbian configuration menu (see command in previous step), go to the `Hostname` option. On each of the Pis, enter a hostname that is short, succint, and easy to identify one Pi from another (e.g. "RPi1", "RPi2", etc.)

**_The following installation sections should be performed on one Pi designated as the main Pi._**
### Creating a standalone network on main Raspberry Pi
The following steps are taken from [here](https://www.raspberrypi.org/documentation/configuration/wireless/access-point.md).

**1. Install required software**

Install DHCP server and access point software by running the following command in the terminal:
```
sudo apt-get install dnsmasq hostapd
```

**2. Turn off new software to make configuration changes**

Run the following command to turn off the newly installed software:
```
sudo systemctl stop dnsmasq
sudo systemctl stop hostapd
```

**3. Make changes to configuration files**

  - Open `/etc/dhcpcd.conf` by running `sudo nano /etc/dhcpcd.conf` and add `denyinterfaces wlan0` on a new line to the end of the file
  - Open `/etc/network/interfaces` (command similar to step above) and add the following lines (IP addresses can be adjusted to suit needs):
    ```
    allow-hotplug wlan0  
    iface wlan0 inet static  
      address 192.168.0.1
      netmask 255.255.255.0
      network 192.168.0.0
    ```
  - Restart DHCP software to apply changes by running the following commands:
    ```
    sudo service dhcpcd restart
    sudo ifdown wlan0
    sudo ifup wlan0
    ```
  - Save a copy of `dnsmasq.conf` by running `sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig`
  - Open a new version of `dnsmasq.conf` by running `sudo nano /etc/dnsmasq.conf` and add the following lines:
    ```
    interface=wlan0
    dhcp-range=192.168.0.2,192.168.0.20,255.255.255.0,24h
    ```
  - Open `/etc/hostapd/hostapd.conf` by running `sudo nano /etc/hostapd/hostapd.conf` and add the following lines (remember to replace `ssid` value with the name of network and `wpa_passphrase` with password for network):
    ```
    interface=wlan0
    driver=nl80211
    ssid=NameOfNetwork
    hw_mode=g
    channel=7
    wmm_enabled=0
    macaddr_acl=0
    auth_algs=1
    ignore_broadcast_ssid=0
    wpa=2
    wpa_passphrase=YourPasswordHere
    wpa_key_mgmt=WPA-PSK
    wpa_pairwise=TKIP
    rsn_pairwise=CCMP
    ```
  - Open `/etc/default/hostapd` by running `sudo nano /etc/default/hostapd`, find the line containing `#DAEMON_CONF`, and replace line with:
    ```
    DAEMON_CONF="/etc/hostapd/hostapd.conf"
    ```
  - Restart newly installed software by running the following commands:
    ```
    sudo service hostapd start  
    sudo service dnsmasq start 
    ```

All configuration files can be found in the repository.

### Setting up Apache web server on main Raspberry Pi

**1. Install software**

Run the following command to install software:
```
sudo apt-get install apache2 -y
```

**2. Test software**

Open web browser and go to `http://localhost` or the Pi's IP address. The *Apache2 Debian Default Page* should appear. 

**3. Change configuration file to allow Python CGI scripts to run on server**

The web app will be hosted in the `/var/www/html` directory. Open the Apache2 configuration file by running `sudo nano /etc/apache2/apache2.conf`. Find the *Security Model Section* (will have several directories listed) and change the `<Directory /var/www/>` section to look like the following:
```
<Directory /var/www/>
	Options Indexes FollowSymLinks ExecCGI
	AllowOverride None
	Require all granted
	AddHandler cgi-script .cgi .py
</Directory>
```
The Apache2 configuration file can be found in the repository.

### Setting up 3D scanner web app

**1. Create necessary folders**

Within `/var/www/html` (the `html` folder should exist already but create it if not), create a new folder called `img` (to store images) by running:
```
sudo mkdir /var/www/html/img
```

**2. Place web app files in web server directory**

Download `camera.py` and `index.html` files from repository and place them in `/var/www/html`. Make the Python file an executable by running:
```
sudo chmod +x /var/www/html/camera.py
```

### Connect all other Pis and test app
Have all other Pis save the network configuration for the standalone network (usually connecting once will save details). Connect them to the network. 

Get any device to connect to the network. Enter the main Pi's IP address in the device's browser (can find IP address by typing `hostname -I` in the main Pi's command line). The web app should appear.

## Usage
- Enter desired image parameters into their respective fields
- Give the project name
- Page will redirect to show images taken
  - Option to download zip file of images or go back to main page
- Images can be viewed again by going to `<IP address>/img`, where `<IP address>` is replaced by the main Pi's IP address
  - Select project folder to view images
  - Click on zip file with project name to download images again
