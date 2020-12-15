# Raspberry installation #

This doc is intended for labo maintainers: it provides instructions on how to
install and set up the Raspberry Pi units used for the labo.

Legend:

* command prompts ending with
  - `#`: run as *root* user. It means you either open a root shell with `sudo
    -i` or you prefix your commands with `sudo`
  - `$`: run as *normal* user

## MAC address list ##

The Wi-Fi/LAN router to which the Pi's are to be connected must be configured
with the following information for *address reservation* over DHCP. A
NetworkManager template is available in file
`labo-setup/net1-IoT-labo.nmconnection`.

Legend:

* `rbpiwX`: Wi-Fi
* `rbpieX`: Ethernet
* `X`: raspberry ID

In the table below, for any ID, the *first* line refers to the **ethernet** card,
the *second* line refers to the **wireless** card.

| ID | MAC               |
|---:|-------------------|
|  1 | DC:A6:32:2F:87:0C |
|    | DC:A6:32:2F:87:0E |
|  2 | DC:A6:32:2F:87:6F |
|    | DC:A6:32:2F:87:70 |
|  3 | DC:A6:32:2F:86:DC |
|    | DC:A6:32:2F:86:DD |
|  4 | DC:A6:32:2F:87:00 |
|    | DC:A6:32:2F:87:01 |
|  5 | DC:A6:32:2F:86:A6 |
|    | DC:A6:32:2F:86:A7 |
|  6 | DC:A6:32:2F:87:03 |
|    | DC:A6:32:2F:87:05 |
|  7 | DC:A6:32:2F:86:82 |
|    | DC:A6:32:2F:86:83 |
|  8 | DC:A6:32:2F:86:F7 |
|    | DC:A6:32:2F:86:F8 |
|  9 | DC:A6:32:16:FD:19 |
|    | DC:A6:32:16:FD:1A |
| 10 | DC:A6:32:2F:87:2A |
|    | DC:A6:32:2F:87:2B |
| 11 | DC:A6:32:16:46:36 |
|    | DC:A6:32:16:46:37 |
| 12 | DC:A6:32:6F:CF:76 |
|    | DC:A6:32:6F:CF:78 |
| 13 | DC:A6:32:6F:CE:F3 |
|    | DC:A6:32:6F:CE:F4 |
| 14 | DC:A6:32:6F:C9:56 |
|    | DC:A6:32:6F:C9:57 |
| 15 | DC:A6:32:6F:CE:D8 |
|    | DC:A6:32:6F:CE:D9 |
| 16 | DC:A6:32:6F:D1:93 |
|    | DC:A6:32:6F:D1:94 |
| 17 | DC:A6:32:6F:D1:EA |
|    | DC:A6:32:6F:D1:EB |
| 18 | DC:A6:32:6F:D1:D2 |
|    | DC:A6:32:6F:D1:D3 |


THE association ID (`X`) => {name, IP addresses} follows this simple rule:
* hostnames
  - base: `rbpiX`
  - ethernet: `rbpieX`
  - wireless: `rbpiwX`
* IP addresses:
  - ethernet: `192.168.1.1X`
  - wireless: `192.168.1.2X`

You can verify on a console with the command

    rpbiX$ ip addr | perl -ne '/link\/ether\s+(\S+)/g && print "$1\n"'

To release an old DHCP lease, do the following

    rpbiX# dhclient -r -v eth0

To access the different Raspberries via host aliases, set up your SSH
configuration (file `~/.ssh/config`) with a snippet like:

    Host rbpieX
      StrictHostKeyChecking no
      HostName 192.168.1.1X
      User pi

    Host rbpiwX
      StrictHostKeyChecking no
      HostName 192.168.1.2X
      User pi


## OS master image preparation ##

Whichever way and Raspberry Pi OS (RPiOS) image you chose, there are some
configuration options to fix and a bunch of extra packages to install. The
original reference OS version is `Raspbian GNU/Linux 10` and is supposed to be
installed on your SD card; if not, download the [latest image
here](https://www.raspberrypi.org/downloads/raspberry-pi-os/ "latest Raspberry
Pi OS") (avoid NOOBS variants, of course -- are we *noobs*, bah!?), prefer a
light one possibly with a desktop GUI (the one of intermediate size).

Mount and tweak the unzipped RPiOS image (boot partition only).

    # unzip raspbian.zip
    # losetup -P /dev/loop0 raspbian.img
    # mkdir -p /mnt/raspbian/{boot,sys}
    # mount /dev/loop0p1 /mnt/raspbian/boot
    # mount /dev/loop0p2 /mnt/raspbian/sys
    # touch /mnt/raspbian/boot/ssh

Apply customized files (you should have already cloned the whole lab's Git
repository) from directory `LAB_GIT_CLONE/labo-setup/master-image/files`:

    # for f in "hostname hosts default/locale default/keyboard"; do \
        echo cp LAB_GIT_CLONE/labo-setup/master-image/files/etc/${f} \
            /mnt/raspbian/sys/etc/${f}
    done

Deploy some user's handy configuration files:

    $ for f in ".ssh/authorized_keys .bashrc .tmux.conf"; do \
        echo cp LAB_GIT_CLONE/labo-setup/master-image/files/home/pi/${f} \
            /mnt/raspbian/sys/home/pi/${f}
    done

Optionally, authorize extra admin public SSH key(s) (`id_rsa.pub`):

    $ mkdir /mnt/raspbian/sys/home/pi/.ssh
    $ cat YOUR/ADMIN/id_rsa.pub >> /mnt/raspbian/sys/home/pi/.ssh/authorized_keys


Unmount the image:

    # umount /mnt/raspbian/boot
    # umount /mnt/raspbian/sys
    # losetup -D

Your image is now ready to be flashed on an SD card. Plug in a reader and
retrieve the device name (replace `Z` with the right letter):

    $ lsblk -f
    NAME   MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT
    ...
    sdZ      8:64   1  14.8G  0 disk
    # dd if=raspbian.img of=/dev/sdZ status=progress conv=fsync bs=256M


## System installation ##

Insert the newly flashed SD card into your Raspberry, connect an Ethernet
cable to a router/switch on your LAN and start the Raspberry. If you
configured correctly the lab's Wi-Fi router and deployed correctly your admin
SSH pub key, you should be able to connect by SSH without password.

    $ ssh rpbieX

Do some configuration. We set the same user `pi`'s password and let the
student change it in the classroom:

    rpbiX# locale-gen
    rpbiX$ passwd
    ...

Enable boot into GUI with auto-login:

    rpbiX# raspi-config nonint do_boot_behaviour B4

Upgrade and reboot:

    rpbiX# apt update
    rpbiX# apt upgrade
    rpbiX# reboot

## Labo installation ##

System libs and utilities:

    rpbiX# apt install openzwave cython tmux virtualenvwrapper

User Python libs:

    rpbiX$ pip3 install --user python_openzwave cython wheel six pyserial 'PyDispatcher>=2.0.5' louie watchdog Flask

Plug the Z-Wave controller into a Raspberry's USB port and test the PyOZW installation:

    rpbiX$ mkdir -p ~/tmp/OZW
    rpbiX$ pyozw_check --config_path /etc/openzwave/ -i -d /dev/ttyACM0 --user_path ~/tmp/OZW
    rpbiX$ pyozw_check --config_path /etc/openzwave/ -l -d /dev/ttyACM0 --user_path ~/tmp/OZW


If everything goes well, shut down the Raspberry:

    rpbiX# shutdown -h now


## Finalization ##

Your system is ready for deployment onto other Raspberry Pi's. Thus dump a
copy of the OS image on your HD (replace the timestamp `YYYY-MM-DD` with a
real date):

    # dd of=raspios_Labo-IoT.YYYY-MM-DD.img if=/dev/sdZ status=progress bs=256M


## Deployment onto Raspberry Pi 'X' ##

Flash the final OS image onto a new SD card:

    # dd if=raspios_Labo-IoT.YYYY-MM-DD.img of=/dev/sdZ status=progress conv=fsync bs=256M

Then, insert the new SD into the Raspberry Pi labeled 'X' and boot it up.

Apply the basic network set-up via the helper script `pi-setup` (replace `X`
with the correct kit's ID):

    $ cd LAB_GIT_CLONE/labo-setup
    $ ./pi-setup        # for help
    $ ./pi-setup X

Hereafter, you will be able to connect to the Raspberry 'X' with its real ID,
e.g., via Ethernet:

    $ ssh rbpie1

or Wi-Fi

    $ ssh rbpiw1


## Ansible provisioning ##

**[Work in progress]**

https://www.dinofizzotti.com/blog/2020-04-10-raspberry-pi-cluster-part-1-provisioning-with-ansible-and-temperature-monitoring-using-prometheus-and-grafana/

https://epcced.github.io/wee_archlet/

https://github.com/TranceCat/Raspberry-Pi-orchestration


## Docker provisioning **

To be investigated...
