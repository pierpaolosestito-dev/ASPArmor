#!/usr/bin/bash

cat /var/log/my_confined_app/$USER.log
cat /etc/my_confined_app.conf  >> /var/log/my_confined_app/$USER.log

