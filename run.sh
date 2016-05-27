#!/bin/bash

# Install dependencies
sudo add-apt-repository -y ppa:fkrull/deadsnakes
sudo apt-get update
sudo apt-get install -y git python3.5 python3.5-dev python-pip python-dev build-essential gfortran libopenblas-dev liblapack-dev
# sudo apt-get install git gcc python34 python34-devel gcc-gfortran lapack lapack-devel blas blas-devel gcc-c++ -y

# Enable swap
sudo /bin/dd if=/dev/zero of=/var/swap.1 bs=1M count=1024
sudo /sbin/mkswap /var/swap.1
sudo /sbin/swapon /var/swap.1

# Get server source
git clone https://github.com/agajews/Music-Rec-Server.git
cd Music-Rec-Server

# Setup virtualenvwrapper
sudo pip install virtualenvwrapper
source /usr/local/bin/virtualenvwrapper.sh
export WORKON_HOME=~/envs

# Enter virtualenv
mkvirtualenv -p python3.5 music-rec-server
workon music-rec-server

# Install python dependencies
pip install numpy
pip install -r requirements.txt --upgrade

# Disable swap
sudo swapoff /var/swap.1
sudo rm /var/swap.1

# Run server
# python3.5 api.py
~/envs/music-rec-server/bin/gunicorn api:app -p api.pid -b 0.0.0.0:8000  # -D
