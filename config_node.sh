#!/bin/sh
# RHUM INSTALLER
# WARNING: This software makes significant changes to the system behavior
# DISCLAIMER: This software is distributed with no warranty.

INSTALL_PATH="$PWD"
CONFIG_PATH="$PWD/conf"
BIN_PATH="$PWD/bin"
BUILD_PATH="$PWD/build"

# Update Apt
cp $CONFIG_PATH/sources.list /etc/apt/
apt-get update

# Update Kernel
read -p "Update kernel? [y/n] " ans
if [ $ans = y -o $ans = Y -o $ans = yes -o $ans = Yes -o $ans = YES ]
    then
        dpkg -i $CONFIG_PATH/kernel/linux-headers-4.2.0*.deb
		dpkg -i $CONFIG_PATH/kernel/linux-image-4.2.0*.deb
fi
if [ $ans = n -o $ans = N -o $ans = no -o $ans = No -o $ans = NO ]
    then
        echo "Aborting..."
fi

# GUI
read -p "Do you want to setup GUI? [y/n] " ans
if [ $ans = y -o $ans = Y -o $ans = yes -o $ans = Yes -o $ans = YES ]
    then
        echo "Removing LightDM..."
        update-rc.d -f lightdm remove || service lightdm remove
        echo "Disabling Mouse ..."
        apt-get install unclutter
        cp $CONFIG_PATH/unclutter /etc/default/
        echo "Configuring Autostart ..."
	cp configs/RHUM.desktop /root/.config/autostart
fi
if [ $ans = n -o $ans = N -o $ans = no -o $ans = No -o $ans = NO ]
    then
        echo "Aborting..."
fi

read -p "Setup as daemon? [y/n] " ans
if [ $ans = y -o $ans = Y -o $ans = yes -o $ans = Yes -o $ans = YES ]
    then
        echo "Configuring daemon (will run in background without GUI) ..."
	cd $BIN_PATH
        cp agcv /etc/init.d/
        chmod +x /etc/init.d/rhum
        update-rc.d rhum defaults
        cd $INSTALL_PATH
fi
if [ $ans = n -o $ans = N -o $ans = no -o $ans = No -o $ans = NO ]
    then
        echo "Aborting ..."
fi

# GRUB
read -p "Enable fast GRUB? [y/n] " ans
if [ $ans = y -o $ans = Y -o $ans = yes -o $ans = Yes -o $ans = YES ]
    then
        echo "Updating Custom Grub..."
        cp $CONFIG_PATH/grub /etc/default
        update-grub
fi
if [ $ans = n -o $ans = N -o $ans = no -o $ans = No -o $ans = NO ]
    then
        echo "Aborting..."
fi

# Network Setup (AP)
read -p "Setup AP network (STABLE)? [y/n] " ans
if [ $ans = y -o $ans = Y -o $ans = yes -o $ans = Yes -o $ans = YES ]
    then
        echo "Reconfiguring Network Interfaces..."
        apt-get install dnsmasq hostapd -y -qq
	apt-get install firmware-iwlwifi firmware-realtek -y -qq
        cp $CONFIG_PATH/iwlwifi-3160-14.ucode /lib/firmware/iwlwifi
        cp $CONFIG_PATH/rtl8723befw.bin /lib/firmware/rtlwifi
	apt-get install wireless-tools -y -qq
        cp $CONFIG_PATH/interfaces /etc/network/interfaces
	cp $CONFIG_PATH/hostapd.conf /etc/hostapd/
	cp $CONFIG_PATH/dnsmasq.conf /etc/
        cp $CONFIG_PATH/dhclient.conf /etc/dhcp/
fi
if [ $ans = n -o $ans = N -o $ans = no -o $ans = No -o $ans = NO ]
    then
        echo "Aborting..."
fi

# APT Packages
read -p "Update APT dependencies? [y/n] " ans
if [ $ans = y -o $ans = Y -o $ans = yes -o $ans = Yes -o $ans = YES ]
    then
        echo "Installing dependencies via mirror ..."
        apt-get upgrade -y -qq
        apt-get install unzip -y -qq
        apt-get install build-essential -y -qq
        apt-get install python-dev -y -qq
        apt-get install cmake -y -qq
        apt-get install python-serial -y -qq
        apt-get install python-pip -y -qq
        apt-get install python-gps -y -qq # python dependencies
        apt-get install gpsd -y -qq
        apt-get install gpsd-clients -y -qq
        apt-get install python-gps -y  -qq # GPS
        apt-get install python-matplotlib -y -qq
        apt-get install libgtk2.0-dev -y -qq
        apt-get install python-numpy -y -qq
        apt-get install libqt4-dev -y -qq
        apt-get install libopencv-dev -y -qq
        apt-get install build-essential -y -qq
        apt-get install checkinstall -y -qq
        apt-get install pkg-config -y -qq
        apt-get install yasm -y -qq
        apt-get install libjpeg-dev -y -qq
        apt-get install libjasper-dev -y -qq
        apt-get install libavcodec-dev -y -qq
        apt-get install libavformat-dev -y -qq
        apt-get install libswscale-dev -y -qq
        apt-get install libdc1394-22-dev -y -qq
        apt-get install libxine-dev -y -qq
        apt-get install libgstreamer0.10-dev -y -qq
        apt-get install libgstreamer-plugins-base0.10-dev -y -qq
        apt-get install libv4l-dev -y -qq
        apt-get install python-numpy -y -qq
        apt-get install libtbb-dev -y -qq
        apt-get install libqt4-dev -y -qq
        apt-get install libgtk2.0-dev -y -qq
        apt-get install libmp3lame-dev -y -qq
        apt-get install libopencore-amrnb-dev -y -qq
        apt-get install libopencore-amrwb-dev -y -qq
        apt-get install libtheora-dev -y -qq
        apt-get install libvorbis-dev -y -qq
        apt-get install libxvidcore-dev -y -qq
        apt-get install x264 -y -qq
        apt-get install v4l-utils -y -qq
        apt-get install arduino arduino-mk -qq
        apt-get install x11-xserver-utils -y -qq
        apt-get install gcc -y -qq
        apt-get install gfortran -y -qq
        apt-get install libblas-dev -y -qq
        apt-get install liblapack-dev -y -qq
        apt-get install cython -y  -qq
fi
if [ $ans = n -o $ans = N -o $ans = no -o $ans = No -o $ans = NO ]
    then
        echo "Aborting..."
fi

# Pip Packages
read -p "Update Pip modules? [y/n] " ans
if [ $ans = y -o $ans = Y -o $ans = yes -o $ans = Yes -o $ans = YES ]
    then
        echo "Installing Python modules..."
        pip install -r requirements.txt
fi
if [ $ans = n -o $ans = N -o $ans = no -o $ans = No -o $ans = NO ]
    then
        echo "Aborting..."
fi

# OpenCV
read -p "Recompile OpenCV? [y/n] " ans
if [ $ans = y -o $ans = Y -o $ans = yes -o $ans = Yes -o $ans = YES ]
    then
        echo "Running fix for AVformat ..."
        cd /usr/include/linux
        ln -s ../libv4l1-videodev.h videodev.h
        ln -s ../libavformat/avformat.h avformat.h
        echo "Installing OpenCV ..."
        mkdir $BUILD_PATH && cd $BUILD_PATH
        wget http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/2.4.9/opencv-2.4.9.zip
        unzip -qq opencv-2.4.9.zip && cd opencv-2.4.9
        mkdir release && cd release
        cmake -D CMAKE_BUILD_TYPE=RELEASE CMAKE_INSTALL_PREFIX=/usr/local ..
        make -j4
        make install
fi
if [ $ans = n -o $ans = N -o $ans = no -o $ans = No -o $ans = NO ]
    then
        echo "Aborting..."
fi

# Done Message
read -p "Installation Complete! Reboot now? [y/n] " ans
if [ $ans = y -o $ans = Y -o $ans = yes -o $ans = Yes -o $ans = YES ]
    then
    echo "Rebooting..."
    reboot
fi
if [ $ans = n -o $ans = N -o $ans = no -o $ans = No -o $ans = NO ]
    then
        echo "Aborting..."
fi

