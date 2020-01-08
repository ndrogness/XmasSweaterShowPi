# XmasSweaterShowPi
Christmas sweater with LED light show

This Python3 software performs all of the analysis of the music
and no manual sequencing/timing is required (its all done through a config file).

## Required Python3 Software modules
adafruit_blinka-> pip3 install adafruit-blinka

RPi GPIO -> pip3 install RPi

alsaaudio (preferrable, but not with bluetooth) -> pip3 install pyalsaaudio

pyaudio (if using bluetooth audio) -> pip3 install pyaudio

numpy -> pip3 install numpy

## Setup Config file
cp XmasSweaterShowPi-example.cfg XmasSweaterShowPi.cfg

Edit XmasSweaterShowPi.cfg

Define outputs (GPIO Pins, LEDs, Neopixels)

Define sequences - these are how defined leds turn on/off based on thresholds and other parameters

## Add music
Put all Wave file songs in a directory called 'songs' in the current directory (or whatever songs directory is 
specified in the config file)

## Run
Run XmasSweaterShowPi.py and the LEDs will turn on/off in sync with the song being played, based on the sequences defined

