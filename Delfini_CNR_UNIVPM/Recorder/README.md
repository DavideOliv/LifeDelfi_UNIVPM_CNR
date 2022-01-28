# Recorder script
This script will start recording using given audio card.
## Required
1) Modify /boot/config.txt
> comment out line dtparam=audio=on
reboot

### Test configuration
Type in shell:
> aplay -l
and
> arecord -l

expected result:
> **** List of PLAYBACK Hardware Devices **** card 0: sndrpihifiberry [snd_rpi_hifiberry_dac], device 0: HifiBerry DAC HiFi pcm5102a-hifi-0 []
> Subdevices: 1/1
> Subdevice #0: subdevice #0 

if not add to /boot/config.txt the device tree overlay conf for your hifiberry
> dtoverlay=hifiberry-dacplusadcpro
reboot again and test.

## Testing audio card
To test usage of SOX software is recommended.
Sox is a set of tools to create/modify/convert sound files. We often use it as a simple sine-wave generator.
> sudo apt install sox
Then play an 1kHz sine test tone using the command
> play -n synth sine 1000

