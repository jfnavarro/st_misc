#!/bin/sh

# This script updates the instance and also configure its time settings.

export DEBIAN_FRONTEND=noninteractive
export LC_ALL=C

apt-get update
apt-get dist-upgrade -y

apt-get install ntp awscli -y

# We choose time zone

echo "Europe/Stockholm" > /etc/timezone

echo "tzdata/Zones/Etc select UTC" | debconf-set-selections
echo "tzdata tzdata/Zones/Europe select Stockholm"  \
 | debconf-set-selections

echo "locales locales/locales_to_be_generated multiselect " \
 "sv_SE.UTF-8 UTF-8,  en_US.UTF-8 UTF-8 | debconf-set-selections" | debconf-set-selections
echo locales locales/default_environment_locale select en_US.UTF-8 | debconf-set-selections

dpkg-reconfigure -fnoninteractive locales

dpkg-reconfigure -fnoninteractive tzdata

service ntp stop
# We force the time to be set
ntpd -gq

# We will reboot later so we can skip starting the ntp
# sudo service ntp start


