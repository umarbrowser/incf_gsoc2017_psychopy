# Part of the PsychoPy library
# Copyright (C) 2015 Jonathan Peirce
# Distributed under the terms of the GNU General Public License (GPL).

from __future__ import division
from psychopy import prefs, exceptions
from sys import platform
from psychopy import core, logging
from psychopy.constants import (STARTED, PLAYING, PAUSED, FINISHED, STOPPED,
                                NOT_STARTED, FOREVER)
from ._base import _SoundBase

try:
    import pyo
except ImportError as err:
    # convert this import error to our own, pyo probably not installed
    raise exceptions.DependencyError(repr(err))

import sys
import threading
pyoSndServer = None

def _bestDriver(devNames, devIDs):
    """Find ASIO or Windows sound drivers
    """
    preferredDrivers = prefs.general['audioDriver']
    outputID = None
    audioDriver = None
    osEncoding = sys.getfilesystemencoding()
    for prefDriver in preferredDrivers:
        logging.info('Looking for {}'.format(prefDriver))
        if prefDriver.lower() == 'directsound':
            prefDriver = u'Primary Sound'
        # look for that driver in available devices
        for devN, devString in enumerate(devNames):
            logging.info('Examining for {}'.format(devString))
            try:
                ds = devString.decode(osEncoding).encode('utf-8').lower()
                if prefDriver.encode('utf-8').lower() in ds:
                    audioDriver = devString.decode(osEncoding).encode('utf-8')
                    outputID = devIDs[devN]
                    logging.info('Success: {}'.format(devString))
                    # we found a driver don't look for others
                    return audioDriver, outputID
            except (UnicodeDecodeError, UnicodeEncodeError):
                logging.info('Failed: {}'.format(devString))
                logging.warn('find best sound driver - could not '
                             'interpret unicode in driver name')
    else:
        return None, None

def getDevices(kind=None):
    """Returns a dict of dict of audio devices of sepcified `kind`

    The dict keys are names and items are dicts of properties
    """
    inputs, outputs = pyo.pa_get_devices_infos()
    if kind is None:
        allDevs = inputs.update(outputs)
    elif kind=='output':
        allDevs = outputs
    else:
        allDevs = inputs
    devs = {}
    for ii in allDevs:  # in pyo this is a dict but keys are ii ! :-/
        dev = allDevs[ii]
        devs[dev['name']] = dev
        dev['id'] = ii
    return devs

# these will be controlled by sound.__init__.py
defaultInput = None
defaultOutput = None


def init(rate=44100, stereo=True, buffer=128):
    """setup the pyo (sound) server
    """
    global pyoSndServer, Sound, audioDriver, duplex, maxChnls
    Sound = SoundPyo
    global pyo
    try:
        assert pyo
    except NameError:  # pragma: no cover
        import pyo
        # can be needed for microphone.switchOn(), which calls init even
        # if audioLib is something else

    # subclass the pyo.Server so that we can insert a __del__ function that
    # shuts it down skip coverage since the class is never used if we have
    # a recent version of pyo

    class _Server(pyo.Server):  # pragma: no cover
        # make libs class variables so they don't get deleted first
        core = core
        logging = logging

        def __del__(self):
            self.stop()
            # make sure enough time passes for the server to shutdown
            self.core.wait(0.5)
            self.shutdown()
            # make sure enough time passes for the server to shutdown
            self.core.wait(0.5)
            # this may never get printed
            self.logging.debug('pyo sound server shutdown')
    if '.'.join(map(str, pyo.getVersion())) < '0.6.4':
        Server = _Server
    else:
        Server = pyo.Server

    # if we already have a server, just re-initialize it
    if 'pyoSndServer' in globals() and hasattr(pyoSndServer, 'shutdown'):
        pyoSndServer.stop()
        # make sure enough time passes for the server to shutdown
        core.wait(0.5)
        pyoSndServer.shutdown()
        core.wait(0.5)
        pyoSndServer.reinit(sr=rate, nchnls=maxChnls,
                            buffersize=buffer, audio=audioDriver)
        pyoSndServer.boot()
    else:
        if platform == 'win32':
            # check for output device/driver
            devNames, devIDs = pyo.pa_get_output_devices()
            audioDriver, outputID = _bestDriver(devNames, devIDs)
            if outputID is None:
                # using the default output because we didn't find the one(s)
                # requested
                audioDriver = 'Windows Default Output'
                outputID = pyo.pa_get_default_output()
            if outputID is not None:
                logging.info('Using sound driver: %s (ID=%i)' %
                             (audioDriver, outputID))
                maxOutputChnls = pyo.pa_get_output_max_channels(outputID)
            else:
                logging.warning(
                    'No audio outputs found (no speakers connected?')
                return -1
            # check for valid input (mic)
            # If no input device is available, devNames and devIDs are empty
            # lists.
            devNames, devIDs = pyo.pa_get_input_devices()
            audioInputName, inputID = _bestDriver(devNames, devIDs)
            # Input devices were found, but requested devices were not found
            if len(devIDs) > 0 and inputID is None:
                defaultID = pyo.pa_get_default_input()
                if defaultID is not None and defaultID != -1:
                    # default input is found
                    # use the default input because we didn't find the one(s)
                    # requested
                    audioInputName = 'Windows Default Input'
                    inputID = defaultID
                else:
                    # default input is not available
                    inputID = None
            if inputID is not None:
                msg = 'Using sound-input driver: %s (ID=%i)'
                logging.info(msg % (audioInputName, inputID))
                maxInputChnls = pyo.pa_get_input_max_channels(inputID)
                duplex = bool(maxInputChnls > 0)
            else:
                maxInputChnls = 0
                duplex = False
        # for other platforms set duplex to True (if microphone is available)
        else:
            audioDriver = prefs.general['audioDriver'][0]
            maxInputChnls = pyo.pa_get_input_max_channels(
                pyo.pa_get_default_input())
            maxOutputChnls = pyo.pa_get_output_max_channels(
                pyo.pa_get_default_output())
            duplex = bool(maxInputChnls > 0)

        maxChnls = min(maxInputChnls, maxOutputChnls)
        if maxInputChnls < 1:  # pragma: no cover
            msg = ('%s.init could not find microphone hardware; '
                   'recording not available')
            logging.warning(msg % __name__)
            maxChnls = maxOutputChnls
        if maxOutputChnls < 1:  # pragma: no cover
            msg = ('%s.init could not find speaker hardware; '
                   'sound not available')
            logging.error(msg % __name__)
            return -1

        # create the instance of the server:
        if platform in ['darwin', 'linux2']:
            # for mac/linux we set the backend using the server audio param
            pyoSndServer = Server(sr=rate, nchnls=maxChnls,
                                  buffersize=buffer, audio=audioDriver)
        else:
            # with others we just use portaudio and then set the OutputDevice
            # below
            pyoSndServer = Server(sr=rate, nchnls=maxChnls, buffersize=buffer)

        pyoSndServer.setVerbosity(1)
        if platform == 'win32':
            pyoSndServer.setOutputDevice(outputID)
            if inputID is not None:
                pyoSndServer.setInputDevice(inputID)
        # do other config here as needed (setDuplex? setOutputDevice?)
        pyoSndServer.setDuplex(duplex)
        pyoSndServer.boot()
    core.wait(0.5)  # wait for server to boot before starting te sound stream
    pyoSndServer.start()
    try:
        Sound()  # test creation, no play
    except pyo.PyoServerStateException:
        msg = "Failed to start pyo sound Server"
        if platform == 'darwin' and audioDriver != 'portaudio':
            msg += "; maybe try prefs.general.audioDriver 'portaudio'?"
        logging.error(msg)
        core.quit()
    logging.debug('pyo sound server started')
    logging.flush()


class SoundPyo(_SoundBase):
    """Create a sound object, from one of MANY ways.
    """

    def __init__(self, value="C", secs=0.5, octave=4, stereo=True,
                 volume=1.0, loops=0, sampleRate=44100, bits=16,
                 hamming=True, start=0, stop=-1,
                 name='', autoLog=True):
        """
        value: can be a number, string or an array:
            * If it's a number between 37 and 32767 then a tone will be
              generated at that frequency in Hz.
            * It could be a string for a note ('A', 'Bfl', 'B', 'C',
              'Csh', ...). Then you may want to specify which octave as well
            * Or a string could represent a filename in the current location,
              or mediaLocation, or a full path combo
            * Or by giving an Nx2 numpy array of floats (-1:1) you can
              specify the sound yourself as a waveform

            By default, a Hamming window (5ms duration) will be applied to a
            generated tone, so that onset and offset are smoother (to avoid
            clicking). To disable the Hamming window, set `hamming=False`.

        secs:
            Duration of a tone. Not used for sounds from a file.

        start : float
            Where to start playing a sound file;
            default = 0s (start of the file).

        stop : float
            Where to stop playing a sound file; default = end of file.

        octave: is only relevant if the value is a note name.
            Middle octave of a piano is 4. Most computers won't
            output sounds in the bottom octave (1) and the top
            octave (8) is generally painful

        stereo: True (= default, two channels left and right),
            False (one channel)

        volume: loudness to play the sound, from 0.0 (silent) to 1.0 (max).
            Adjustments are not possible during playback, only before.

        loops : int
            How many times to repeat the sound after it plays once. If
            `loops` == -1, the sound will repeat indefinitely until stopped.

        sampleRate (= 44100): if the psychopy.sound.init() function has been
            called or if another sound has already been created then this
            argument will be ignored and the previous setting will be used

        bits: has no effect for the pyo backend

        hamming: whether to apply a Hamming window (5ms) for generated tones.
            Not applied to sounds from files.
        """
        global pyoSndServer
        if pyoSndServer is None or pyoSndServer.getIsBooted() == 0:
            init(rate=sampleRate)

        self.sampleRate = pyoSndServer.getSamplingRate()
        self.format = bits
        self.isStereo = stereo
        self.channels = 1 + int(stereo)
        self.secs = secs
        self.startTime = start
        self.stopTime = stop
        self.autoLog = autoLog
        self.name = name

        # try to create sound; set volume and loop before setSound (else
        # needsUpdate=True)
        self._snd = None
        self.volume = min(1.0, max(0.0, volume))
        # distinguish the loops requested from loops actual because of
        # infinite tones (which have many loops but none requested)
        # -1 for infinite or a number of loops
        self.requestedLoops = self.loops = int(loops)

        self.setSound(value=value, secs=secs, octave=octave, hamming=hamming)
        self.needsUpdate = False

    def play(self, loops=None, autoStop=True, log=True):
        """Starts playing the sound on an available channel.

        loops : int
            (same as above)

        For playing a sound file, you cannot specify the start and stop
        times when playing the sound, only when creating the sound initially.

        Playing a sound runs in a separate thread i.e. your code won't wait
        for the sound to finish before continuing. To pause while playing,
        you need to use a `psychopy.core.wait(mySound.getDuration())`.
        If you call `play()` while something is already playing the sounds
        will be played over each other.
        """
        if loops is not None and self.loops != loops:
            self.setLoops(loops)
        if self.needsUpdate:
            # ~0.00015s, regardless of the size of self._sndTable
            self._updateSnd()
        self._snd.out()
        self.status = STARTED
        if autoStop or self.loops != 0:
            # pyo looping is boolean: loop forever or not at all
            # so track requested loops using time; limitations: not
            # sample-accurate
            if self.loops >= 0:
                duration = self.getDuration() * (self.loops + 1)
            else:
                duration = FOREVER
            self.terminator = threading.Timer(duration, self._onEOS)
            self.terminator.start()
        if log and self.autoLog:
            logging.exp("Sound %s started" % (self.name), obj=self)
        return self

    def _onEOS(self):
        # call _onEOS from a thread based on time, enables loop termination
        if self.loops != 0:  # then its looping forever as a pyo object
            self._snd.stop()
        if self.status != NOT_STARTED:
            # in case of multiple successive trials
            self.status = FINISHED
        return True

    def stop(self, log=True):
        """Stops the sound immediately"""
        self._snd.stop()
        try:
            self.terminator.cancel()
        except Exception:  # pragma: no cover
            pass
        self.status = STOPPED
        if log and self.autoLog:
            logging.exp("Sound %s stopped" % (self.name), obj=self)

    def _updateSnd(self):
        self.needsUpdate = False
        doLoop = bool(self.loops != 0)  # if True, end it via threading.Timer
        self._snd = pyo.TableRead(self._sndTable,
                                  freq=self._sndTable.getRate(),
                                  loop=doLoop, mul=self.volume)

    def _setSndFromFile(self, fileName):
        # want mono sound file played to both speakers, not just left / 0
        self.fileName = fileName
        self._sndTable = pyo.SndTable(initchnls=self.channels)
        # in case a tone with inf loops had been used before
        self.loops = self.requestedLoops
        # mono file loaded to all chnls:
        try:
            self._sndTable.setSound(self.fileName,
                                    start=self.startTime, stop=self.stopTime)
        except Exception:
            msg = ('Could not open sound file `%s` using pyo; not found '
                   'or format not supported.')
            logging.error(msg % fileName)
            raise TypeError(msg % fileName)
        self._updateSnd()
        self.duration = self._sndTable.getDur()

    def _setSndFromArray(self, thisArray):
        self._sndTable = pyo.DataTable(size=len(thisArray),
                                       init=thisArray.T.tolist(),
                                       chnls=self.channels)
        self._updateSnd()
        # a DataTable has no .getDur() method, so just store the duration:
        self.duration = float(len(thisArray)) / self.sampleRate
