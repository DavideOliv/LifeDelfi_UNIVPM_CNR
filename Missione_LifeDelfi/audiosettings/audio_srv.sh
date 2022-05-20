#!/bin/bash

mode=$1
dbamp=$2

amixer sset "ADC Mic Bias" "Mic Bias off"

if [ ${mode} -eq diff ];
then
	amixer sset "ADC Left Input" "{VIN1P, VIN1M}[DIFF]"
	amixer sset "ADC Right Input" "{VIN2P, VIN2M}[DIFF]"
else
	amixer sset "ADC Left Input" "VINL1[SE]"
	amixer sset "ADC Right Input" "VINR1[SE]"
fi

amixer sset ADC ${dbamp}db
