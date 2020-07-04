import argparse
import array as ar
import contextlib
import math
import os
import sys
import threading
import wave
import numpy as np
import pygame
from scipy.signal import resample_poly


# class that is used to place the keys at the right places
# Online source, credit @glicheur123 via Github
class Touche:
    pygame.time.delay(10)

    def __init__(self, img1, img2, coordinate, sound, clicked=False):
        self.img1 = img1
        self.img2 = img2
        self.coordinate = coordinate
        self.initialize()
        self.sound = sound
        self.clicked = clicked

    def getdata(self):
        return self.image

    def initialize(self):
        self.image = pygame.image.load(self.img1)

    def toucheclick(self):
        self.image = pygame.image.load(self.img2)

    def getImg(self):
        return self.img1

    def setco(self, cor):
        self.coordinate = cor

    def playsound(self):
        t = threading.Thread(target=self.soundThread)
        t.start()

    def soundThread(self):
        self.sound.play()

    def setclicked(self, stat):
        self.clicked = stat

    def getClicked(self):
        return self.clicked

    def getcoordonate(self):
        return self.coordinate


# Class end


# main function to show piano interface
def show_piano(folder="music"):
    # initialising PyGame and PyGame.mixer(for sound effects)
    pygame.mixer.pre_init(44100, -16, 2, 1024)
    pygame.init()
    pygame.mixer.init(44100, -16, 2, 1024)

    # get absolute path of current directory
    directory = os.path.split(os.path.abspath(__file__))[0]

    # set window size
    width = 1420
    height = 374

    # initialising window
    screen = pygame.display.set_mode((width, height))

    # fill back ground color
    screen.fill((89, 89, 89))

    # set title and logo
    pygame.display.set_caption("piano")
    piano = pygame.image.load("piano.jpg")
    pygame.display.set_icon(piano)

    # positioning all the white keys
    whitekeys = []
    for i in range(0, 15):
        whitekeys.append(Touche(os.path.join(directory, "keys", "{}.png".format(i + 1)),
                                os.path.join(directory, "keys", "{}a.png".format(i + 1)), (i * 95, 1),
                                pygame.mixer.Sound(os.path.join(directory, folder, "{}.wav".format(i + 1)))))

    # positioning each black key with position 0
    blackkeys = []
    for i in range(0, 10):
        blackkeys.append(
            Touche(os.path.join(directory, "keys", "a.png"), os.path.join(directory, "keys", "b.png"), (0, 0),
                   pygame.mixer.Sound(
                       os.path.join(directory, folder, "n{}.wav".format(i + 1)))))

    # move each black key to correct position
    blackkeys[0].setco((59, 0))
    blackkeys[1].setco((171, 0))
    blackkeys[2].setco((347, 0))
    blackkeys[3].setco((449, 0))
    blackkeys[4].setco((550, 0))
    blackkeys[5].setco((725, 0))
    blackkeys[6].setco((835, 0))
    blackkeys[7].setco((1010, 0))
    blackkeys[8].setco((1114, 0))
    blackkeys[9].setco((1219, 0))

    # map keyboard button to white keys
    white_wd = ["a", "s", "d", "f", "g", "h", "v", "b", "n", "m", "j", "k", "l", ";", "'"]
    num = range(15)
    key_white = dict(zip(white_wd, num))

    # map keyboard button to black keys
    black_wd = ["w", "e", "r", "t", "y", "u", "i", "o", "p", "["]
    num2 = range(10)
    key_black = dict(zip(black_wd, num2))

    # Main Loop
    playing = True
    while playing:
        # buffering time
        pygame.time.delay(0)

        # keyboard event
        for event in pygame.event.get():

            # quit command
            if event.type == pygame.QUIT:
                playing = False

            # key pressed down
            if event.type == pygame.KEYDOWN:
                # get key name
                key = pygame.key.name(event.key)
                # check if key is white key
                if key in key_white:
                    whitekeys[key_white[key]].playsound()
                    whitekeys[key_white[key]].toucheclick()
                # check if key is black key
                elif key in key_black:
                    blackkeys[key_black[key]].playsound()
                    blackkeys[key_black[key]].toucheclick()

            # key released
            if event.type == pygame.KEYUP:
                # get key name
                key = pygame.key.name(event.key)
                # check if key is white key
                if key in key_white:
                    whitekeys[key_white[key]].setclicked(False)
                    whitekeys[key_white[key]].initialize()
                # check if key is black key
                elif key in key_black:
                    blackkeys[key_black[key]].setclicked(False)
                    blackkeys[key_black[key]].initialize()

        # show white keys
        for key in whitekeys:
            screen.blit(key.getdata(), key.getcoordonate())

        # show black keys
        for key in blackkeys:
            screen.blit(key.getdata(), key.getcoordonate())

        # refresh
        pygame.display.flip()


# Basic parameters for reading and writing mono wave files

numChannels = 1  # mono
sampleWidth = 2  # in bytes, a 16-bit short
SR = 44100  # sample rate
MAX_AMP = (2 ** (8 * sampleWidth - 1) - 1)  # maximum amplitude is 2**15 - 1  = 32767
MIN_AMP = -(2 ** (8 * sampleWidth - 1))  # min amp is -2**15


# Clip a signal or a scalar to upper and lower bounds, if not specified, us
# bounds provided above; will change the array in place and return it.
# Does NOT make a new copy.

def clip(X, lb=MIN_AMP, ub=MAX_AMP):
    if type(X) != list and type(X) != np.ndarray:
        return max(min(X, MAX_AMP), MIN_AMP)

    for k in range(len(X)):
        X[k] = max(min(X[k], MAX_AMP), MIN_AMP)
    return X


# To prevent clipping, this function takes a signal and rescales the amplitude
# (which must be given in relative units, in range 0 .. 1) so that
#
#           max(X) = A * MAX_AMP
#

def scaleSignal(X, A=1.0):
    s = MAX_AMP * A / max(X)
    return np.array([x * s for x in X]).astype(int)


# I/O for Wave files

# Read a mono wave file from a local file and return the entire file as a 1-D numpy array

def readWaveFile(infile, withParams=False, asNumpy=True):
    with contextlib.closing(wave.open(infile)) as f:
        params = f.getparams()
        frames = f.readframes(params[3])
        if (params[0] != 1):
            print("Warning in reading file: must be a mono file!")
        if (params[1] != 2):
            print("Warning in reading file: must be 16-bit sample type!")
        if (params[2] != 44100):
            print("Warning in reading file: must be 44100 sample rate!")
    if asNumpy:
        X = ar.array('h', frames)
        X = np.array(X, dtype='int64')
    else:
        X = ar.array('h', frames)
    if withParams:
        return X, params
    else:
        return X


# Write out an array as a wave file to the local directory

def writeWaveFile(X, fname):
    X = clip(X)
    params = [1, 2, SR, len(X), "NONE", None]
    data = ar.array("h", X)
    with contextlib.closing(wave.open(fname, "w")) as f:
        f.setparams(params)
        f.writeframes(data.tobytes())
    print(fname + " written.")


# Convert a float factor P to a fraction N/M which is as close as possible to P.
# You may assume that P has at most 1 significant digit after the decimal point

def timeStretch(X, P):
    return resample_poly(X, math.floor(100 * P), 100)


# Stretches or shortens a sound
def stretch(sound, factor, window_size, h):
    phase = np.zeros(window_size)
    hanning_window = np.hanning(window_size)
    result = np.zeros(int(len(sound) / factor + window_size))

    for i in np.arange(0, len(sound) - (window_size + h), h * factor):
        i = int(i)

        # Two potentially overlapping sub-arrays
        a1 = sound[i: i + window_size]
        a2 = sound[i + h: i + window_size + h]

        # find the spectra of arrays by Fast Fourier transform
        s1 = np.fft.fft(hanning_window * a1)
        s2 = np.fft.fft(hanning_window * a2)

        # Rephrase all frequencies
        phase = (phase + np.angle(s2 / s1)) % 2 * np.pi

        rephase = np.fft.ifft(np.abs(s2) * np.exp(1j * phase))
        i2 = int(i / factor)
        result[i2: i2 + window_size] += hanning_window * rephase.real

    # normalize (16bit)
    result = ((2 ** (16 - 4)) * result / result.max())

    return result.astype('int16')


# Changes the pitch of a sound by n semitones.
def pitchshift(sound, n, window_size=2 ** 13, h=2 ** 11):
    # convert n to the frequency factor
    factor = 2 ** (1.0 * n / 12.0)

    # stretch to change the pitch
    stretched = stretch(sound, 1.0 / factor, window_size, h)

    # stretch the duration without changing the pitch by re-sample
    return timeStretch(stretched[window_size:], 1 / factor)


def process(filePath='bowl.wav'):
    original = readWaveFile(filePath)
    original = scaleSignal(original, MAX_AMP)
    filename = ['1', 'n1', '2', 'n2', '3', '4', 'n3', '5', 'n4', '6', 'n5', '7', '8', 'n6', '9', 'n7', '10', '11', 'n8',
                '12', 'n9', '13', 'n10', '14', '15']
    for i in range(-12, 13):
        x = pitchshift(original, i)
        writeWaveFile(np.rint(x).astype(int), 'default/' + filename[i + 12] + '.wav')
    print("Finished")


# command line promotion
def parse_arguments():
    description = 'play "piano" with your keyboard'

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        '-w',
        metavar='FILE',
        type=argparse.FileType('r'),
        help='WAV file (try: bowl.wav)')

    return parser.parse_args(), parser


if __name__ == '__main__':

    # Parse command line arguments
    (args, parser) = parse_arguments()

    # No input from user, run display mode
    if args.w is None:
        sys.stdout.write('*** Real Piano mode, no transform used ***\n')
        sys.stdout.write('*** Only for GUI display *** \n')
        sys.stdout.write('*** For Pitch Shift demo, try "python piano.py -w bowl.wav" ***\n')
        sys.stdout.flush()
        show_piano()
    # input detected, run main program
    else:
        sys.stdout.write('Transforming sound files ... ')
        sys.stdout.flush()

        # generate audio files, stored in folder "default"
        process(args.w.name)

        sys.stdout.write('Opening Program ... ')
        sys.stdout.flush()

        # run GUI
        show_piano("default")
