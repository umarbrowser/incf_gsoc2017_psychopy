import os
import wx
from .._base import BaseComponent, Param, _translate
import psychopy
from psychopy import logging
from psychopy.tools.versionchooser import versionOptions, availableVersions
from psychopy.app.builder.experiment import _numpyImports, _numpyRandomImports
from psychopy.app.projects import projectCatalog
try:
    from pyosf import remote
except ImportError:
    pass


# for creating html output folders:
import shutil
import hashlib
import zipfile

def readTextFile(relPath):
    fullPath = os.path.join(thisFolder, relPath)
    with open(fullPath, "r") as f:
        txt = f.read()
    return txt

# this is not a standard component - it will appear on toolbar not in
# components panel

# only use _localized values for label values, nothing functional:
_localized = {'expName': _translate("Experiment name"),
              'Show info dlg':  _translate("Show info dialog"),
              'Enable Escape':  _translate("Enable Escape key"),
              'Experiment info':  _translate("Experiment info"),
              'Data filename':  _translate("Data filename"),
              'Full-screen window':  _translate("Full-screen window"),
              'Window size (pixels)':  _translate("Window size (pixels)"),
              'Screen': _translate('Screen'),
              'Monitor':  _translate("Monitor"),
              'color': _translate("Color"),
              'colorSpace':  _translate("Color space"),
              'Units':  _translate("Units"),
              'blendMode':   _translate("Blend mode"),
              'Show mouse':  _translate("Show mouse"),
              'Save log file':  _translate("Save log file"),
              'Save wide csv file':
                  _translate("Save csv file (trial-by-trial)"),
              'Save csv file': _translate("Save csv file (summaries)"),
              'Save excel file':  _translate("Save excel file"),
              'Save psydat file':  _translate("Save psydat file"),
              'logging level': _translate("Logging level"),
              'Use version': _translate("Use PsychoPy version")}

thisFolder = os.path.split(__file__)[0]


# customize the Proj ID Param class to
class ProjIDParam(Param):
    @property
    def allowedVals(self):
        allowed = projectCatalog.keys()
        # always allow the current val!
        if self.val not in allowed:
            allowed.append(self.val)
        # always allow blank (None)
        if '' not in allowed:
            allowed.append('')
        return allowed
    @allowedVals.setter
    def allowedVals(self, allowed):
        pass

class SettingsComponent(object):
    """This component stores general info about how to run the experiment
    """

    def __init__(self, parentName, exp, expName='', fullScr=True,
                 winSize=(1024, 768), screen=1, monitor='testMonitor',
                 showMouse=False, saveLogFile=True, showExpInfo=True,
                 expInfo="{'participant':'', 'session':'001'}",
                 units='use prefs', logging='exp',
                 color='$[0,0,0]', colorSpace='rgb', enableEscape=True,
                 blendMode='avg',
                 saveXLSXFile=False, saveCSVFile=False,
                 saveWideCSVFile=True, savePsydatFile=True,
                 savedDataFolder='',
                 useVersion='',
                 filename=None):
        self.type = 'Settings'
        self.exp = exp  # so we can access the experiment if necess
        self.exp.requirePsychopyLibs(['visual', 'gui'])
        self.parentName = parentName
        self.url = "http://www.psychopy.org/builder/settings.html"

        # if filename is the default value fetch the builder pref for the
        # folder instead
        if filename is None:
            filename = ("u'xxxx/%s_%s_%s' % (expInfo['participant'], expName,"
                        " expInfo['date'])")
        if filename.startswith("u'xxxx"):
            folder = self.exp.prefsBuilder['savedDataFolder'].strip()
            filename = filename.replace("xxxx", folder)

        # params
        self.params = {}
        self.order = ['expName', 'Show info dlg', 'Experiment info',
                      'Data filename',
                      'Save excel file', 'Save csv file',
                      'Save wide csv file', 'Save psydat file',
                      'Save log file', 'logging level',
                      'Monitor', 'Screen', 'Full-screen window',
                      'Window size (pixels)',
                      'color', 'colorSpace', 'Units', ]
        # basic params
        self.params['expName'] = Param(
            expName, valType='str', allowedTypes=[],
            hint=_translate("Name of the entire experiment (taken by default"
                            " from the filename on save)"),
            label=_localized["expName"])
        self.params['Show info dlg'] = Param(
            showExpInfo, valType='bool', allowedTypes=[],
            hint=_translate("Start the experiment with a dialog to set info"
                            " (e.g.participant or condition)"),
            label=_localized["Show info dlg"], categ='Basic')
        self.params['Enable Escape'] = Param(
            enableEscape, valType='bool', allowedTypes=[],
            hint=_translate("Enable the <esc> key, to allow subjects to quit"
                            " / break out of the experiment"),
            label=_localized["Enable Escape"])
        self.params['Experiment info'] = Param(
            expInfo, valType='code', allowedTypes=[],
            hint=_translate("The info to present in a dialog box. Right-click"
                            " to check syntax and preview the dialog box."),
            label=_localized["Experiment info"], categ='Basic')
        self.params['Use version'] = Param(
            useVersion, valType='str',
            # search for options locally only by default, otherwise sluggish
            allowedVals=versionOptions() + [''] + availableVersions(),
            hint=_translate("The version of PsychoPy to use when running "
                            "the experiment."),
            label=_localized["Use version"], categ='Basic')

        # screen params
        self.params['Full-screen window'] = Param(
            fullScr, valType='bool', allowedTypes=[],
            hint=_translate("Run the experiment full-screen (recommended)"),
            label=_localized["Full-screen window"], categ='Screen')
        self.params['Window size (pixels)'] = Param(
            winSize, valType='code', allowedTypes=[],
            hint=_translate("Size of window (if not fullscreen)"),
            label=_localized["Window size (pixels)"], categ='Screen')
        self.params['Screen'] = Param(
            screen, valType='num', allowedTypes=[],
            hint=_translate("Which physical screen to run on (1 or 2)"),
            label=_localized["Screen"], categ='Screen')
        self.params['Monitor'] = Param(
            monitor, valType='str', allowedTypes=[],
            hint=_translate("Name of the monitor (from Monitor Center). Right"
                            "-click to go there, then copy & paste a monitor "
                            "name here."),
            label=_localized["Monitor"], categ="Screen")
        self.params['color'] = Param(
            color, valType='str', allowedTypes=[],
            hint=_translate("Color of the screen (e.g. black, $[1.0,1.0,1.0],"
                            " $variable. Right-click to bring up a "
                            "color-picker.)"),
            label=_localized["color"], categ='Screen')
        self.params['colorSpace'] = Param(
            colorSpace, valType='str',
            hint=_translate("Needed if color is defined numerically (see "
                            "PsychoPy documentation on color spaces)"),
            allowedVals=['rgb', 'dkl', 'lms', 'hsv'],
            label=_localized["colorSpace"], categ="Screen")
        self.params['Units'] = Param(
            units, valType='str', allowedTypes=[],
            allowedVals=['use prefs', 'deg', 'pix', 'cm', 'norm', 'height',
                         'degFlatPos', 'degFlat'],
            hint=_translate("Units to use for window/stimulus coordinates "
                            "(e.g. cm, pix, deg)"),
            label=_localized["Units"], categ='Screen')
        self.params['blendMode'] = Param(
            blendMode, valType='str',
            allowedTypes=[], allowedVals=['add', 'avg'],
            hint=_translate("Should new stimuli be added or averaged with "
                            "the stimuli that have been drawn already"),
            label=_localized["blendMode"], categ='Screen')
        self.params['Show mouse'] = Param(
            showMouse, valType='bool', allowedTypes=[],
            hint=_translate("Should the mouse be visible on screen?"),
            label=_localized["Show mouse"], categ='Screen')

        # data params
        self.params['Data filename'] = Param(
            filename, valType='code', allowedTypes=[],
            hint=_translate("Code to create your custom file name base. Don"
                            "'t give a file extension - this will be added."),
            label=_localized["Data filename"], categ='Data')
        self.params['Save log file'] = Param(
            saveLogFile, valType='bool', allowedTypes=[],
            hint=_translate("Save a detailed log (more detailed than the "
                            "excel/csv files) of the entire experiment"),
            label=_localized["Save log file"], categ='Data')
        self.params['Save wide csv file'] = Param(
            saveWideCSVFile, valType='bool', allowedTypes=[],
            hint=_translate("Save data from loops in comma-separated-value "
                            "(.csv) format for maximum portability"),
            label=_localized["Save wide csv file"], categ='Data')
        self.params['Save csv file'] = Param(
            saveCSVFile, valType='bool', allowedTypes=[],
            hint=_translate("Save data from loops in comma-separated-value "
                            "(.csv) format for maximum portability"),
            label=_localized["Save csv file"], categ='Data')
        self.params['Save excel file'] = Param(
            saveXLSXFile, valType='bool', allowedTypes=[],
            hint=_translate("Save data from loops in Excel (.xlsx) format"),
            label=_localized["Save excel file"], categ='Data')
        self.params['Save psydat file'] = Param(
            savePsydatFile, valType='bool', allowedVals=[True],
            hint=_translate("Save data from loops in psydat format. This is "
                            "useful for python programmers to generate "
                            "analysis scripts."),
            label=_localized["Save psydat file"], categ='Data')
        self.params['logging level'] = Param(
            logging, valType='code',
            allowedVals=['error', 'warning', 'data', 'exp', 'info', 'debug'],
            hint=_translate("How much output do you want in the log files? "
                            "('error' is fewest messages, 'debug' is most)"),
            label=_localized["logging level"], categ='Data')

        # HTML output params
        self.params['OSF Project ID'] = ProjIDParam(
            '', valType='str', # automatically updates to allow choices
            hint=_translate("The ID of this project (e.g. 5bqpc)"),
            label="OSF Project ID", categ='Online')
        self.params['HTML path'] = Param(
            'html', valType='str', allowedTypes=[],
            hint=_translate("Place the HTML files will be saved locally "),
            label="Output path", categ='Online')
        self.params['JS libs'] = Param(
            'packaged', valType='str', allowedVals=['packaged'],
            hint=_translate("Should we package a copy of the JS libs or use"
                            "remote copies (http:/www.psychopy.org/js)?"),
            label="JS libs", categ='Online')

    def getType(self):
        return self.__class__.__name__

    def getShortType(self):
        return self.getType().replace('Component', '')

    def getSaveDataDir(self):
        if 'Saved data folder' in self.params:
            # we have a param for the folder (deprecated since 1.80)
            saveToDir = self.params['Saved data folder'].val.strip()
            if not saveToDir:  # it was blank so try preferences
                saveToDir = self.exp.prefsBuilder['savedDataFolder'].strip()
        else:
            saveToDir = os.path.dirname(self.params['Data filename'].val)
        return saveToDir or u'data'

    def writeUseVersion(self, buff):
        if self.params['Use version'].val:
            code = ('\nimport psychopy\n'
                    'psychopy.useVersion({})\n\n')
            val = repr(self.params['Use version'].val)
            buff.writeIndentedLines(code.format(val))

    def writeInitCode(self, buff, version, localDateTime):

        buff.write(
            '#!/usr/bin/env python2\n'
            '# -*- coding: utf-8 -*-\n'
            '"""\nThis experiment was created using PsychoPy2 Experiment '
            'Builder (v%s),\n'
            '    on %s\n' % (version, localDateTime) +
            'If you publish work using this script please cite the PsychoPy '
            'publications:\n'
            '    Peirce, JW (2007) PsychoPy - Psychophysics software in '
            'Python.\n'
            '        Journal of Neuroscience Methods, 162(1-2), 8-13.\n'
            '    Peirce, JW (2009) Generating stimuli for neuroscience using '
            'PsychoPy.\n'
            '        Frontiers in Neuroinformatics, 2:10. doi: 10.3389/'
            'neuro.11.010.2008\n"""\n'
            "\nfrom __future__ import absolute_import, division\n")

        self.writeUseVersion(buff)

        buff.write(
            "from psychopy import locale_setup, "
            "%s\n" % ', '.join(self.exp.psychopyLibs) +
            "from psychopy.constants import (NOT_STARTED, STARTED, PLAYING,"
            " PAUSED,\n"
            "                                STOPPED, FINISHED, PRESSED, "
            "RELEASED, FOREVER)\n"
            "import numpy as np  # whole numpy lib is available, "
            "prepend 'np.'\n"
            "from numpy import (%s,\n" % ', '.join(_numpyImports[:7]) +
            "                   %s)\n" % ', '.join(_numpyImports[7:]) +
            "from numpy.random import %s\n" % ', '.join(_numpyRandomImports) +
            "import os  # handy system and path functions\n" +
            "import sys  # to get file system encoding\n"
            "\n")

    def prepareResourcesJS(self):
        """Sets up the resources folder and writes the info.php file for PsychoJS
        """

        join = os.path.join

        def copyTreeWithMD5(src, dst):
            """Copies the tree but checks SHA for each file first
            """
            # despite time to check the md5 hashes this func gives speed-up
            # over about 20% over using shutil.rmtree() and copytree()
            for root, subDirs, files in os.walk(src):
                relPath = os.path.relpath(root, src)
                for thisDir in subDirs:
                    if not os.path.isdir(join(root, thisDir)):
                        os.makedirs(join(root, thisDir))
                for thisFile in files:
                    copyFileWithMD5(join(root, thisFile),
                                    join(dst, relPath, thisFile))

        def copyFileWithMD5(src, dst):
            """Copies a file but only if doesn't exist or SHA is diff
            """
            if os.path.isfile(dst):
                with open(dst, 'r') as f:
                    dstMD5 = hashlib.md5(f.read()).hexdigest()
                with open(src, 'r') as f:
                    srcMD5 = hashlib.md5(f.read()).hexdigest()
                if srcMD5 == dstMD5:
                    return  # already matches - do nothing
                # if we got here then the file exists but not the same
                # delete and replace. TODO: In future this should check date
                os.remove(dst)
            # either didn't exist or has been deleted
            folder = os.path.split(dst)[0]
            if not os.path.isdir(folder):
                os.makedirs(folder)
            shutil.copy2(src, dst)

        # write info.php file
        folder = self.exp.expPath
        if not os.path.isdir(folder):
            os.mkdir(folder)
        # get OSF projcet info if there was a project id
        projLabel = self.params['OSF Project ID'].val
        # these are all blank unless we find a valid proj
        osfID = osfName = osfToken = ''
        osfHtmlFolder = ''
        osfDataFolder = 'data'
        # is email a defined parameter for this version
        if 'email' in self.params:
            email = repr(self.params['email'].val)
        else:
            email = "''"
        if projLabel in projectCatalog:  # this is the psychopy  descriptive label (id+title)
            proj = projectCatalog[projLabel]
            osfID = proj.osf.id
            osfName = proj.osf.title
            osfUser = proj.username
            osfToken = remote.TokenStorage()[osfUser]
            osfHtmlFolder = self.params['HTML path'].val
        infoPHPfilename = os.path.join(folder, 'info.php')
        infoText = readTextFile("JS_infoPHP.tmpl")
        infoText = infoText.format(osfID=osfID,
                                   osfName=osfName,
                                   osfToken=osfToken,
                                   osfHtmlFolder=osfHtmlFolder,
                                   osfDataFolder=osfDataFolder,
                                   params=self.params,
                                   email=email,
                                   )

        infoText = infoText.replace("=> u'", "=> '") # remove unicode symbols
        with open(infoPHPfilename, 'w') as infoFile:
            infoFile.write(infoText)

        # populate resources folder
        resFolder = join(folder, 'resources')
        if not os.path.isdir(resFolder):
            os.mkdir(resFolder)
        resourceFiles = self.exp.getResourceFiles()
        for srcFile in resourceFiles:
            dstAbs = os.path.normpath(join(resFolder, srcFile['rel']))
            dstFolder = os.path.split(dstAbs)[0]
            if not os.path.isdir(dstFolder):
                os.makedirs(dstFolder)
            shutil.copy2(srcFile['abs'], dstAbs)

        # add the js libs if needed for packaging
        ppRoot = os.path.split(os.path.abspath(psychopy.__file__))[0]
        jsPath = join(ppRoot, '..', 'psychojs')
        if os.path.isdir(jsPath):
            if self.params['JS libs'].val == 'packaged':
                copyTreeWithMD5(join(jsPath,'php'), join(folder, 'php'))
                copyTreeWithMD5(join(jsPath,'js'), join(folder, 'js'))

            # always copy server.php
            shutil.copy2(os.path.join(jsPath, 'server.php'), folder)
        else:
            jsZip = zipfile.ZipFile(os.path.join(ppRoot, 'psychojs.zip'))
            # copy over JS libs if needed
            if self.params['JS libs'].val == 'packaged':
                jsZip.extractall(path=folder)
            else:
                jsZip.extract(path=folder, member="server.php")

    def writeInitCodeJS(self, buff, version, localDateTime):
        # write info.php and resources folder as well
        self.prepareResourcesJS()

        # html header
        template = readTextFile("JS_htmlHeader.tmpl")
        header = template.format(
                   name = self.params['expName'].val, # prevent repr() conversion
                   params = self.params)
        buff.write(header)

        # write the code to set up experiment
        buff.setIndentLevel(4, relative=False)
        template = readTextFile("JS_setupExp.tmpl")
        # check where to save data variables
        if self.params['OSF Project ID'].val:
            saveType = "OSF_VIA_EXPERIMENT_SERVER"
            projID = "'{}'".format(self.params['OSF Project ID'].val)
        else:
            saveType = "EXPERIMENT_SERVER"
            projID = 'undefined'
        code = template.format(
                        params=self.params,
                        saveType=saveType,
                        projID=projID,
                        loggingLevel = self.params['logging level'].val.upper(),
                        )
        buff.writeIndentedLines(code)

    def writeStartCode(self, buff):
        code = ("# Ensure that relative paths start from the same directory "
                "as this script\n"
                "_thisDir = os.path.dirname(os.path.abspath(__file__))."
                "decode(sys.getfilesystemencoding())\n"
                "os.chdir(_thisDir)\n\n"
                "# Store info about the experiment session\n")
        buff.writeIndentedLines(code)

        if self.params['expName'].val in [None, '']:
            buff.writeIndented("expName = 'untitled.py'\n")
        else:
            code = ("expName = %s  # from the Builder filename that created"
                    " this script\n")
            buff.writeIndented(code % self.params['expName'])
        expInfo = self.params['Experiment info'].val.strip()
        if not len(expInfo):
            expInfo = '{}'
        try:
            expInfoDict = eval('dict(' + expInfo + ')')
        except SyntaxError:
            logging.error('Builder Expt: syntax error in '
                          '"Experiment info" settings (expected a dict)')
            raise AttributeError('Builder: error in "Experiment info"'
                                 ' settings (expected a dict)')
        buff.writeIndented("expInfo = %s\n" % expInfo)
        if self.params['Show info dlg'].val:
            buff.writeIndentedLines(
                "dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)\n"
                "if dlg.OK == False:\n    core.quit()  # user pressed cancel\n")
        buff.writeIndentedLines(
            "expInfo['date'] = data.getDateStr()  # add a simple timestamp\n"
            "expInfo['expName'] = expName\n")
        level = self.params['logging level'].val.upper()

        saveToDir = self.getSaveDataDir()
        buff.writeIndentedLines("\n# Data file name stem = absolute path +"
                                " name; later add .psyexp, .csv, .log, etc\n")
        # deprecated code: before v1.80.00 we had 'Saved data folder' param
        # fairly fixed filename
        if 'Saved data folder' in self.params:
            participantField = ''
            for field in ('participant', 'Participant', 'Subject', 'Observer'):
                if field in expInfoDict:
                    participantField = field
                    self.params['Data filename'].val = (
                        repr(saveToDir) + " + os.sep + '%s_%s' % (expInfo['" +
                        field + "'], expInfo['date'])")
                    break
            if not participantField:
                # no participant-type field, so skip that part of filename
                self.params['Data filename'].val = repr(
                    saveToDir) + " + os.path.sep + expInfo['date']"
            # so that we don't overwrite users changes doing this again
            del self.params['Saved data folder']

        # now write that data file name to the script
        if not self.params['Data filename'].val:  # i.e., the user deleted it
            self.params['Data filename'].val = (
                repr(saveToDir) +
                " + os.sep + u'psychopy_data_' + data.getDateStr()")
        # detect if user wanted an absolute path -- else make absolute:
        filename = self.params['Data filename'].val.lstrip('"\'')
        # (filename.startswith('/') or filename[1] == ':'):
        if filename == os.path.abspath(filename):
            buff.writeIndented("filename = %s\n" %
                               self.params['Data filename'])
        else:
            buff.writeIndented("filename = _thisDir + os.sep + %s\n" %
                               self.params['Data filename'])

        # set up the ExperimentHandler
        code = ("\n# An ExperimentHandler isn't essential but helps with "
                "data saving\n"
                "thisExp = data.ExperimentHandler(name=expName, version='',\n"
                "    extraInfo=expInfo, runtimeInfo=None,\n"
                "    originPath=%s,\n")
        buff.writeIndentedLines(code % repr(self.exp.expPath))

        code = ("    savePickle=%(Save psydat file)s, saveWideText=%(Save "
                "wide csv file)s,\n    dataFileName=filename)\n")
        buff.writeIndentedLines(code % self.params)

        if self.params['Save log file'].val:
            code = ("# save a log file for detail verbose info\nlogFile = "
                    "logging.LogFile(filename+'.log', level=logging.%s)\n")
            buff.writeIndentedLines(code % level)
        buff.writeIndented("logging.console.setLevel(logging.WARNING)  "
                           "# this outputs to the screen, not a file\n")

        if self.exp.settings.params['Enable Escape'].val:
            buff.writeIndentedLines("\nendExpNow = False  # flag for 'escape'"
                                    " or other condition => quit the exp\n")

    def writeWindowCode(self, buff):
        """Setup the window code.
        """
        buff.writeIndentedLines("\n# Setup the Window\n")
        # get parameters for the Window
        fullScr = self.params['Full-screen window'].val
        # if fullscreen then hide the mouse, unless its requested explicitly
        allowGUI = (not bool(fullScr)) or bool(self.params['Show mouse'].val)
        allowStencil = False
        # NB routines is a dict:
        for thisRoutine in self.exp.routines.values():
            # a single routine is a list of components:
            for thisComp in thisRoutine:
                if thisComp.type == 'Aperture':
                    allowStencil = True
                if thisComp.type == 'RatingScale':
                    allowGUI = True  # to have a mouse

        requestedScreenNumber = int(self.params['Screen'].val)
        try:
            nScreens = wx.Display.GetCount()
        except Exception:
            # will fail if application hasn't been created (e.g. in test
            # environments)
            nScreens = 10
        if requestedScreenNumber > nScreens:
            logging.warn("Requested screen can't be found. Writing script "
                         "using first available screen.")
            screenNumber = 0
        else:
            # computer has 1 as first screen
            screenNumber = requestedScreenNumber - 1

        if fullScr:
            size = wx.Display(screenNumber).GetGeometry()[2:4]
        else:
            size = self.params['Window size (pixels)']
        code = ("win = visual.Window(\n    size=%s, fullscr=%s, screen=%s,"
                "\n    allowGUI=%s, allowStencil=%s,\n")
        vals = (size, fullScr, screenNumber, allowGUI, allowStencil)
        buff.writeIndented(code % vals)
        code = ("    monitor=%(Monitor)s, color=%(color)s, "
                "colorSpace=%(colorSpace)s,\n")
        if self.params['blendMode'].val:
            code += "    blendMode=%(blendMode)s, useFBO=True,\n"

        if self.params['Units'].val != 'use prefs':
            code += "    units=%(Units)s"
        code = code.rstrip(', \n') + ')\n'
        buff.writeIndentedLines(code % self.params)

        if 'microphone' in self.exp.psychopyLibs:  # need a pyo Server
            buff.writeIndentedLines("\n# Enable sound input/output:\n"
                                    "microphone.switchOn()\n")

        code = ("# store frame rate of monitor if we can measure it\n"
                "expInfo['frameRate'] = win.getActualFrameRate()\n"
                "if expInfo['frameRate'] != None:\n"
                "    frameDur = 1.0 / round(expInfo['frameRate'])\n"
                "else:\n"
                "    frameDur = 1.0 / 60.0  # could not measure, so guess\n")
        buff.writeIndentedLines(code)

    def writeWindowCodeJS(self, buff):
        fullscr = str(self.params['Full-screen window']).lower() #lower case string
        template = readTextFile("JS_winInit.tmpl")
        code = template.format(params=self.params,
                               fullscr=fullscr)
        buff.writeIndentedLines(code)

    def writeEndCode(self, buff):
        """Write code for end of experiment (e.g. close log file).
        """
        buff.writeIndented("# these shouldn't be strictly necessary "
                           "(should auto-save)\n")
        if self.params['Save wide csv file'].val:
            buff.writeIndented("thisExp.saveAsWideText(filename+'.csv')\n")
        if self.params['Save psydat file'].val:
            buff.writeIndented("thisExp.saveAsPickle(filename)\n")
        if self.params['Save log file'].val:
            buff.writeIndented("logging.flush()\n")
        code = ("# make sure everything is closed down\n"
                "thisExp.abort()  # or data files will save again on exit\n"
                "win.close()\n"
                "core.quit()\n")
        buff.writeIndentedLines(code)

    def writeEndCodeJS(self, buff):
        abbrevFunc = ("\nfunction abbrevNames(thisTrial) {\n"
                "  return function () {\n"
                "    // abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)\n"
                "    if (thisTrial != undefined) {\n"
                "      for (paramName in thisTrial) {\n"
                "        window[paramName] = thisTrial[paramName];\n"
                "      }\n"
                "    }\n"
                "    return psychoJS.NEXT;\n"
                "  };\n"
                "}\n"
                )
        buff.writeIndentedLines(abbrevFunc)
        quitFunc = ("\nfunction quitPsychoJS() {\n"
                    "    win.close()\n"
                    "    psychoJS.core.quit();\n"
                    "    return psychoJS.QUIT;\n"
                    "}")
        buff.writeIndentedLines(quitFunc)
        buff.setIndentLevel(-1)
        footer = ("\n"
                  "        run();\n"
                  "      });\n"
                  "    </script>\n\n"
                  "  </body>\n"
                  "</html>")
        buff.writeIndentedLines(footer)