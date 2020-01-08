#!/usr/bin/env python3

import os
import sys
import time
import random
import RPi.GPIO as GPIO
import RogyAudio
import RogySequencer

GPIO.setmode(GPIO.BCM)

# Ack...globals...yeah, I know
CAN_PLAY = False
SONG_PAUSED = False
NEXT_SONG = False


def pause_callback(channel):
    '''
    Call back function when PAUSE button is pressed
    :param channel:
    :return:
    '''
    global CAN_PLAY
    global SONG_PAUSED
    global NEXT_SONG

    print("Pause Pressed", "Can Play:", CAN_PLAY, "Paused:", SONG_PAUSED, "Next Song:", NEXT_SONG)
    if CAN_PLAY is False:
        CAN_PLAY = False

    elif SONG_PAUSED is True:
        SONG_PAUSED = False
        CAN_PLAY = True

    elif SONG_PAUSED is False:
        SONG_PAUSED = True
    else:
        CAN_PLAY = False
        SONG_PAUSED = False


def play_callback(channel):
    '''
    Call back function when PLAY button is pressed
    :param channel: GPIO channel
    :return:
    '''
    global CAN_PLAY
    global SONG_PAUSED
    global NEXT_SONG

    print("Play Pressed", "Can Play:", CAN_PLAY, "Paused:", SONG_PAUSED, "Next Song:", NEXT_SONG)
    if CAN_PLAY is False:
        CAN_PLAY = True
    elif NEXT_SONG is False:
        NEXT_SONG = True
    else:
        NEXT_SONG = False

    SONG_PAUSED = False


def setup_buttons(pause_gpio_pin, play_gpio_pin):
    """
    Setup configured Play and Pause buttons with call backs
    :param pause_pin: GPIO pin for pause button
    :param play_pin: GPIO pin for play button
    :return:
    """
    GPIO.setup(int(pause_gpio_pin), GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(int(pause_gpio_pin), GPIO.FALLING, callback=pause_callback, bouncetime=300)

    GPIO.setup(int(play_gpio_pin), GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(int(play_gpio_pin), GPIO.FALLING, callback=play_callback, bouncetime=300)


def read_config(cfgfile='XmasSweaterShowPi.cfg', debug=False):
    '''
    Read Configuration File
    :param cfgfile: filename of config file, default: XmasShowPi-example.cfg
    :param debug: print debugging
    :return: config dictionary
    '''

    # Defaults
    config_data = {'songs_dir': 'songs',
                   'pause_gpio_pin': 5,
                   'play_gpio_pin': 6,
                   'outputs_idle_status': False,
                   'outputs_enable': True,
                   'debug': False
                   }

    num_tokens = 0
    # valid_tokens = ['RF_FREQ', 'SONGS_DIR', 'LIGHTS_ON_AT_HOUR', 'LIGHTS_OFF_AT_HOUR', 'SHOW_START_TIME_HOUR']

    if not os.path.isfile(cfgfile):
        print('WARNING: Missing config file:', cfgfile, ', using default config values')
        return config_data

    with open(cfgfile, mode='r') as f:
        configlines = f.read().splitlines()
    f.close()

    for i in range(0, len(configlines)):
        if debug is True:
            print('Processing config file line {0}: {1}'.format(i, configlines[i]))

        cline = configlines[i].split("=")

        if cline[0] == 'SONGS_DIR':
            config_data['songs_dir'] = cline[1]
            num_tokens += 1

        if cline[0] == 'PAUSE_GPIO_PIN':
            config_data['pause_gpio_pin'] = int(cline[1])
            num_tokens += 1

        if cline[0] == 'PLAY_GPIO_PIN':
            config_data['play_gpio_pin'] = int(cline[1])
            num_tokens += 1

        if cline[0] == 'OUTPUTS_STATUS_WHEN_IDLE':
            if cline[1] == 'ON':
                config_data['output_idle_status'] = True
            num_tokens += 1

        if cline[0] == 'OUTPUTS_ENABLE':
            if cline[1] == 'OFF':
                config_data['outputs_enable'] = False

        if cline[0] == 'DEBUG':
            if cline[1] == 'ON':
                config_data['debug'] = True

    if debug is True:
        print('Final config data: ', config_data)

    return config_data



def build_playlist(songs_dir, randomize=True, debug=False):
    '''
    Build a playlist from the songs directory
    :param songs_dir: Directory of wavefile songs
    :param randomize: Randomize the list of songs
    :param debug: print debugging
    :return: list of songs to process
    '''

    songs = []

    # Check to make sure we have a songs directory
    if not os.path.exists(songs_dir):
        print('WARNING: No songs directory:', songs_dir)
        return songs

    # Loop through songs dir to generate list of songs
    for dfile in os.listdir(songs_dir):
        pfile = "%s/%s" % (songs_dir, dfile)
        if os.path.isfile(pfile):
            songs.append(pfile)
            if debug is True:
                print('Found valid song to add to playlist:', pfile)

    if randomize is True:
        random.shuffle(songs)

    if debug is True:
        print('Final playlist:', songs)

    return songs


def xmas_sweater_show_start():
    '''
    Start the show (one pass through the songs directory)
    :return: Null
    '''

    global CAN_PLAY
    global SONG_PAUSED
    global NEXT_SONG

    # Loop through the playlist and play each song
    for song_index in range(0, len(playlist)):

        # Reset the sequencer before each song
        sr.reset()

        if CAN_PLAY is True:
            NEXT_SONG = False

            # init Audio File object
            audio_file = RogyAudio.AudioFile(playlist[song_index])
            print("Playing:", playlist[song_index], "->", audio_file.nframes,
                  audio_file.nchannels, audio_file.frame_rate,
                  audio_file.sample_width)

            # Run Audio analysis on it, i.e. FFT
            audio_data = audio_file.read_analyze_chunk(frqs=freqs, wghts=weights)
            chunk_counter = 1
            # print(sys.getsizeof(audio_data))
            while sys.getsizeof(audio_data) > 16000:

                if audio_file.write_chunk(audio_data) is True:
                    sr.check(audio_file.chunk_levels)
                else:
                    raise IOError

                audio_data = audio_file.read_analyze_chunk(frqs=freqs, wghts=weights)
                chunk_counter += 1
                while SONG_PAUSED is True:
                    time.sleep(1)

                if NEXT_SONG is True:
                    break

            audio_file.stop()

        # Can't play next song in playlist (show is over folks!)
        else:
            # Stop the sequencer status
            sr.stop()


def clean_exit():
    '''
    Clean things up on exit
    :return: null
    '''
    sr.deinit()
    GPIO.cleanup()
    exit(0)


if __name__ == '__main__':
    '''
    Main context
    '''

    try:

        # Load in config
        cfg = read_config()

        # Get some control of the buttons
        setup_buttons(pause_gpio_pin=cfg['pause_gpio_pin'], play_gpio_pin=cfg['play_gpio_pin'])

        # Load in sequencer
        sr = RogySequencer.Sequencer(cfgfile='XmasSweaterShowPi.cfg', outputs_enable=cfg['outputs_enable'],
                                     debug=cfg['debug'])

        # Frequencies we're interested in
        signals = RogyAudio.Signals()
        freqs = signals.frequencies
        weights = signals.weights
        fidelities = signals.fidelities

        print("Using Frequencies:", freqs)
        print("Using Weights:", weights)
        print("Using Fidelities:", fidelities)

        # Build a playlist of songs
        playlist = build_playlist('/home/pi/RogySweater/songs')

        loop_counter = 0
        while True:
            xmas_sweater_show_start()

            time.sleep(2)
            loop_counter += 1

    except KeyboardInterrupt:
        clean_exit()

    except Exception as e:
        print("Exception:", sys.exc_info()[0], "Argument:", str(e))
        clean_exit()

