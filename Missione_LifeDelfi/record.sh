#!/bin/bash
amixer sset "ADC Right Input" "VINR1[SE]"
amixer sset "ADC Left Input" "VINL1[SE]"
amixer sset "ADC 40db"

while test 1
do
	filename=`date +'%Y%m%d_%H%M%S'`
        echo "Recording $filename.wav"
	arecord -r192000 -fS16_LE -c1 -d300 $filename.wav
done
