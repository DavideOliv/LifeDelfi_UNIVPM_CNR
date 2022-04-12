#!/bin/bash

# Check audio card
audiocard=$(arecord -l)
expected="snd_rpi_hifiberry_dacplusadcpro" # change with your audiocard
[[ $audiocard =~ $expected ]] && echo "Using $expected audio input" || ( echo "Audio card: $expected not found" ; exit )

# Check USB device
homedir="/media/pi/"
usbdevices=$(ls -l $homedir | grep -c ^d)

if [ $usbdevices -eq 0 ]; then
  echo "No USB devices detected"; exit 
fi
usbdevices=$(ls $homedir)
echo "Using $homedir/${usbdevices[0]} as storage"

# Get counter of acquisition
usbdir="$homedir/$usbdevices"

COUNTER=$(ls -l $usbdir | grep -c ^d)
echo "Found $COUNTER folders"
echo "Creating folder: $COUNTER"
mkdir $usbdir/$COUNTER

# Start recording
CHANNELS=1
FREQUENCY=192000
SAVEDIR="$usbdir/$COUNTER"
STIME=10
FILETYPE=wav

arecord --duration=$STIME --channels=$CHANNELS --file-type $FILETYPE --rate=$FREQUENCY $SAVEDIR/acq.wav


