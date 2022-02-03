#!/bin/bash

# Functions
function doublebip()
{
  for n in {1..2}
  do
    gpio -g write $buzzer 1
    sleep 0.1
    gpio -g write $buzzer 0
    sleep 0.3
  done
}

function error()
{
  for n in {1..3}
  do
    gpio -g write $buzzer 1
    sleep 0.5
    gpio -g write $buzzer 0
    sleep 0.5
  done
}

# Consts
buzzer=4

CHANNELS=2
FREQUENCY=48000
STIME=10
FILETYPE=wav

homedir="/media/pi/"
#homedir="/home/pi/Desktop/prova"

# Set GPIO 7 out
gpio -g mode $buzzer out

# Check audio card
audiocard=$(arecord -l)
expected="snd_rpi_hifiberry_dacplusadcpro" # change with your audiocard
[[ $audiocard =~ $expected ]] && ( echo "Using $expected audio input" ) || { echo "Audio card: $expected not found" ; error ; exit ; }

# Settings
echo "Settings mic options:"

amixer sset "ADC Mic Bias" "Mic Bias On"
amixer sset "ADC Left Input" "{VIN1p, VIN1M}[DIFF]"
amixer sset "ADC Right Input" "{VIN2P, VIN2M}[DIFF]"
amixer sset ADC 40db

# Check USB device
usbdevices=$(ls -l $homedir | grep -c ^d)
while [ $usbdevices -eq 0 ]
do
  doublebip
  sleep 1
  usbdevices=$(ls -l $homedir | grep -c ^d)
done
gpio -g write $buzzer 1
sleep 0.8
gpio -g write $buzzer 0
sleep 0.3
doublebip

#if [ $usbdevices -eq 0 ]; then
#  echo "No USB devices detected"; exit 
#fi
usbdevices=$(ls $homedir)
echo "Using $homedir/${usbdevices[0]} as storage"

# Get counter of acquisition
usbdir="$homedir/$usbdevices"

COUNTER=$(ls -l $usbdir | grep -c ^d)
echo "Found $COUNTER folders"
echo "Creating folder: $COUNTER"
mkdir $usbdir/$COUNTER
SAVEDIR="$usbdir/$COUNTER"

# Start recording
#gpio -g mode $buzzer in
arecord --duration=$STIME --channels=$CHANNELS --file-type $FILETYPE --rate=$FREQUENCY -f S16_LE $SAVEDIR/acq.wav || error


