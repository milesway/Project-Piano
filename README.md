# Project-Piano
A piano controlled by your keyboard made by PyGame

This program has two main part. A GUI that show a piano that allows you to control it using your keyboard. And a phase vocoder that changes the pitch of your input file and maps different pitches to each piano key.
 
To play you need to install the flowing:
 > Python 3, Numpy, Scipy, and Pygame
  
## Install
Please console the offical page to install the dependencies.

My recommendation is to instll **pip**  if your python version is older than Python 3.4. [Use this link to install pip.](https://pip.pypa.io/en/stable/installing/)

Then we can install all dependencies with pip:

```sh
$ python3 -m pip install numpy
$ python3 -m pip install scipy
$ python3 -m pip install pygame
```
or the following code, if you only has one version of python installed on your computer

```sh
$ python -m pip install numpy
$ python -m pip install scipy
$ python -m pip install pygame
```
## Run

The program has two models, a GUI demo model and a main program.
To run GUI demo model, simply type following in your commond line in the directory of the program folder
```sh
$ python3 piano.py
```
or 
```sh
$ python piano.py
```

For the main function, you need provide a 44100Hz, mono wave file through the commond line, or you can try the two sample included in the project folder.
The **bowl.wav** is the recording of knock a bowl and **crash.wav** is a recoding of a singal hit of Clash Cymbal.
To tun, input the following:
```sh
$ python3 piano.py -w bowl.wav
$ python3 piano.py -w crash.wav
```
or 
```sh
$ python piano.py -w bowl.wav
$ python piano.py -w crash.wav
```
Note: if you want to use a whole sound, please understand this may need a long time to process the file and the outcome maybe unsatisfied.

## Techniques
The main function of GUI is provided by PyGame, an open-source Python model. However, the process of using it is hard. First, we need to create a pygame object, then draw the basic interface windows and fill the content with pictures of piano keys. I creat the keys using Photoshop, with 93 pixels width and 374 pixels height. Then, for each key, I map a music file to it and assign a keyboard key. Therefore, when the user presses a key, a function will be called inside that key object and output through pygame mixer. 

In order to change the pitch of a wav file, the program has a phase vocoder built inside. The operation process is as follows:
1. user input a wav file
2. **readWaveFile** takes the file and transfers it into a numpy array
3. the audio array have been sent to **pitchshift**
4. the audio first been stretched, so that its pitch change
5. the audio then been stretched the duration without changing the pitch by re-sample
6. **writeWaveFile** takes the audio and output to the default folder
7. repeat this process with different factor to get 25 files with different pitch

