# Part of the PsychoPy library
# Copyright (C) 2015 Jonathan Peirce
# Distributed under the terms of the GNU General Public License (GPL).

from os import path
from .._base import BaseVisualComponent, Param, getInitVals, _translate

# the absolute path to the folder containing this path
thisFolder = path.abspath(path.dirname(__file__))
iconFile = path.join(thisFolder, 'movie.png')
tooltip = _translate('Movie: play movie files')

# only use _localized values for label values, nothing functional:
_localized = {'movie': _translate('Movie file'),
              'forceEndRoutine': _translate('Force end of Routine'),
              'backend': _translate('backend')}


class MovieComponent(BaseVisualComponent):
    """An event class for presenting movie-based stimuli"""

    def __init__(self, exp, parentName, name='movie', movie='',
                 units='from exp settings',
                 pos=(0, 0), size='', ori=0,
                 startType='time (s)', startVal=0.0,
                 stopType='duration (s)', stopVal=1.0,
                 startEstim='', durationEstim='',
                 forceEndRoutine=False, backend='moviepy',
                 noAudio=False):
        super(MovieComponent, self).__init__(
            exp, parentName, name=name, units=units,
            pos=pos, size=size, ori=ori,
            startType=startType, startVal=startVal,
            stopType=stopType, stopVal=stopVal,
            startEstim=startEstim, durationEstim=durationEstim)

        self.type = 'Movie'
        self.url = "http://www.psychopy.org/builder/components/movie.html"
        # comes immediately after name and timing params
        self.order = ['forceEndRoutine']

        # params
        self.params['stopVal'].hint = _translate(
            "When does the component end? (blank to use the duration of "
            "the media)")

        msg = _translate("A filename for the movie (including path)")
        self.params['movie'] = Param(
            movie, valType='str', allowedTypes=[],
            updates='constant', allowedUpdates=['constant', 'set every repeat'],
            hint=msg,
            label=_localized['movie'])

        msg = _translate("What underlying lib to use for loading movies")
        self.params['backend'] = Param(
            backend, valType='str',
            allowedVals=['moviepy', 'avbin', 'opencv'],
            hint=msg,
            label=_localized['backend'])

        # todo: msg = _translate(...)
        msg = ("Prevent the audio stream from being loaded/processed "
               "(moviepy and opencv only)")
        self.params["No audio"] = Param(
            noAudio, valType='bool',
            hint=msg,
            label='No audio')

        msg = _translate("Should the end of the movie cause the end of "
                         "the routine (e.g. trial)?")
        self.params['forceEndRoutine'] = Param(
            forceEndRoutine, valType='bool', allowedTypes=[],
            updates='constant', allowedUpdates=[],
            hint=msg,
            label=_localized['forceEndRoutine'])

        # these are normally added but we don't want them for a movie
        del self.params['color']
        del self.params['colorSpace']

    def _writeCreationCode(self, buff, useInits):
        # This will be called by either self.writeInitCode() or
        # self.writeRoutineStartCode()
        #
        # The reason for this is that moviestim is actually created fresh each
        # time the movie is loaded.
        #
        # leave units blank if not needed
        if self.params['units'].val == 'from exp settings':
            unitsStr = ""
        else:
            unitsStr = "units=%(units)s, " % self.params

        # If we're in writeInitCode then we need to convert params to initVals
        # because some (variable) params haven't been created yet.
        if useInits:
            params = getInitVals(self.params)
        else:
            params = self.params

        if self.params['backend'].val == 'moviepy':
            code = ("%s = visual.MovieStim3(\n" % params['name'] +
                    "    win=win, name='%s',%s\n" % (params['name'], unitsStr) +
                    "    noAudio = %(No audio)s,\n" % params)
        elif self.params['backend'].val == 'avbin':
            code = ("%s = visual.MovieStim(\n" % params['name'] +
                    "    win=win, name='%s',%s\n" % (params['name'], unitsStr))
        else:
            code = ("%s = visual.MovieStim2(\n" % params['name'] +
                    "    win=win, name='%s',%s\n" % (params['name'], unitsStr) +
                    "    noAudio = %(No audio)s,\n" % params)

        code += ("    filename=%(movie)s,\n"
                 "    ori=%(ori)s, pos=%(pos)s, opacity=%(opacity)s,\n"
                 % params)

        buff.writeIndentedLines(code)

        if self.params['size'].val != '':
            buff.writeIndented("    size=%(size)s,\n" % params)

        depth = -self.getPosInRoutine()
        code = ("    depth=%.1f,\n"
                "    )\n")
        buff.writeIndentedLines(code % depth)

    def writeInitCode(self, buff):
        # If needed then use _writeCreationCode()
        # Movie could be created here or in writeRoutineStart()
        if self.params['movie'].updates == 'constant':
            # create the code using init vals
            self._writeCreationCode(buff, useInits=True)

    def writeRoutineStartCode(self, buff):
        # If needed then use _writeCreationCode()
        # Movie could be created here or in writeInitCode()
        if self.params['movie'].updates != 'constant':
            # create the code using params, not vals
            self._writeCreationCode(buff, useInits=False)

    def writeFrameCode(self, buff):
        """Write the code that will be called every frame
        """
        buff.writeIndented("\n")
        buff.writeIndented("# *%s* updates\n" % self.params['name'])
        # writes an if statement to determine whether to draw etc
        self.writeStartTestCode(buff)
        # buff.writeIndented(
        #     "%s.seek(0.00001)  # make sure we're at the start\n"
        #     % (self.params['name']))
        buff.writeIndented("%s.setAutoDraw(True)\n" % self.params['name'])
        # because of the 'if' statement of the time test
        buff.setIndentLevel(-1, relative=True)
        if self.params['stopVal'].val not in ['', None, -1, 'None']:
            # writes an if statement to determine whether to draw etc
            self.writeStopTestCode(buff)
            buff.writeIndented("%(name)s.setAutoDraw(False)\n" % self.params)
            # to get out of the if statement
            buff.setIndentLevel(-1, relative=True)
        # set parameters that need updating every frame
        # do any params need updating? (this method inherited from _base)
        if self.checkNeedToUpdate('set every frame'):
            code = "if %(name)s.status == STARTED:  # only update if being drawn\n" % self.params
            buff.writeIndented(code)

            buff.setIndentLevel(+1, relative=True)  # to enter the if block
            self.writeParamUpdates(buff, 'set every frame')
            buff.setIndentLevel(-1, relative=True)  # to exit the if block
        # do force end of trial code
        if self.params['forceEndRoutine'].val is True:
            code = ("if %s.status == FINISHED:  # force-end the routine\n"
                    "    continueRoutine = False\n" %
                    self.params['name'])
            buff.writeIndentedLines(code)
