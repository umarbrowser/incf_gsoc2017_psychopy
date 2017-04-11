#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Language localization for PsychoPy.

Sets the locale value as a wx languageID (int) and initializes gettext
translation _translate():
    from psychopy.app import localization
"""

# Part of the PsychoPy library
# Copyright (C) 2015 Jonathan Peirce
# Distributed under the terms of the GNU General Public License (GPL).

# Author: Jeremy Gray, July 2014


import gettext
import os
import glob
import codecs
from psychopy import logging, prefs

import wx

# need a wx App for wx.Locale:
try:
    wx.Dialog(None, -1)
except wx._core.PyNoAppError:
    if wx.version() < '2.9':
        tmpApp = wx.PySimpleApp()
    else:
        tmpApp = wx.App(False)

# Get a dict of locale aliases from wx.Locale() -- same cross-platform
# (Win 7, Mac 10.9)
locale = wx.Locale()
aliases = {u'English (U.S.)': 'en_US'}
# set defaults because locale.GetLanguageInfo(0) can return None on some
# systems:
wxIdFromCode = {'en_US': wx.LANGUAGE_DEFAULT}  # int: 0 default, 2-229
# used in directory names e.g. ja_JP; never JPN ala Windows
codeFromWxId = {wx.LANGUAGE_DEFAULT: 'en_US'}
for i in range(230):
    info = locale.GetLanguageInfo(i)
    if info:
        # mix of forms: ja or ja_JP
        aliases[info.Description] = info.CanonicalName
        wxIdFromCode[info.CanonicalName] = i
        codeFromWxId[i] = info.CanonicalName

# read all known mappings cross-platform from a file:
# get windows 3-letter code (=val) from canonical form (=key); use only
# for setting locale (non-wx)
winmap = {'en_US': 'ENU'}
# descriptive name, if available; 5-letter code if not
locname = {'en_US': u'English (U.S.)'}
reverseMap = {u'English (U.S.)': 'en_US'}
mappings = os.path.join(os.path.dirname(__file__), 'mappings.txt')
for line in codecs.open(mappings, 'rU', 'utf8').readlines():
    try:
        # canonical, windows, name-with-spaces
        can, win, name = line.strip().split(' ', 2)
    except ValueError:
        can, win = line.strip().split(' ', 1)
        name = can
    winmap[can] = win
    locname[can] = name
    reverseMap[name] = can

# what are the available translations? available languages on the OS?
expr = os.path.join(os.path.dirname(__file__), '..', 'locale', '*')
available = sorted(map(os.path.basename, glob.glob(expr)))
sysAvail = [str(l) for l in codeFromWxId.values()  # installed language packs
            if l and locale.IsAvailable(wxIdFromCode[l])]


def getID(lang=None):
    """Get wx ID of language to use for translations:
        `lang`, pref, or system default.

    `lang` is a 5 char `language_REGION`, eg ja_JP
    """
    if lang:
        val = lang
    else:
        try:
            val = prefs.app['locale']
        except KeyError:
            val = locale.GetLocale()  # wx.Locale, no encoding
        if not val:
            val = codeFromWxId[wx.LANGUAGE_DEFAULT]
    try:
        # todo: try to set wx.Locale here to language
        language = wxIdFromCode[val]
    except KeyError:
        logging.error('locale %s not known to wx.Locale, using default' % val)
        language = wx.LANGUAGE_DEFAULT

    return language, val

languageID, lang = getID()
# use lang like this:
# import locale  -- the non-wx version of locale
#
# if sys.platform.startswith('win'):
#        v = winmap[val]
# else: v=val
# locale.setlocale(locale.LC_ALL, (v, 'UTF-8'))

# set locale before splash screen:
if locale.IsAvailable(languageID):
    wxlocale = wx.Locale(languageID)
else:
    wxlocale = wx.Locale(wx.LANGUAGE_DEFAULT)

# ideally rewrite the following using wxlocale only:
path = os.path.join(os.path.dirname(__file__), '..',
                    'locale', lang, 'LC_MESSAGE') + os.sep
mofile = os.path.join(path, 'messages.mo')
try:
    logging.debug("Opening message catalog %s for locale %s" % (mofile, lang))
    trans = gettext.GNUTranslations(open(mofile, "rb"))
except IOError:
    logging.debug("Locale for '%s' not found. Using default." % lang)
    trans = gettext.NullTranslations()
trans.install(unicode=True)

# PsychoPy app uses a nonstandard name _translate (instead of _)
# A dependency overwrites _ somewhere, clobbering use of _ as global:
# __builtins__['_translate'] = _
# del(__builtins__['_'])  # idea: force psychopy code to use _translate

# Feb 2016: require modules to explicitly import _translate from localization:
_translate = _  # _ is created by gettext, in builtins namespace
del(__builtins__['_'])


# __builtins__['_'] = wx.GetTranslation
# this seems to have no effect, needs more investigation:
# path = os.path.join(os.path.dirname(__file__), '..', 'locale',
#                     lang, 'LC_MESSAGE') + os.sep
# wxlocale.AddCatalogLookupPathPrefix(path)
