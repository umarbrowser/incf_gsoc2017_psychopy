#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
keyboard_rt.run.py

Keyboard Reaction Time Calulation shown within a line length matching task.

Inital Version: May 6th, 2013, Sol Simpson
"""

from __future__ import division

from psychopy import  core,  visual
from psychopy.iohub import launchHubServer
from math import fabs

io = launchHubServer(psychopy_monitor_name='default')
display = io.devices.display
win = visual.Window(display.getPixelResolution(), monitor='default',
    units='pix', #color=[128, 128, 128], colorSpace='rgb255',
    fullscr=True, allowGUI=False)

# save some 'dots' during the trial loop
keyboard = io.devices.keyboard

# constants for use in example
line_size_match_delay = 5 + int(core.getTime() * 1000) % 5
full_length = win.size[0] / 2
latest_length = 0

static_bar = visual.ShapeStim(win=win, lineColor='Firebrick',
    fillColor='Firebrick',
    vertices=[[0, 0], [full_length, 0], [full_length, 5], [0, 5]],
    pos=(-win.size[0] / 4, win.size[1] / 24))
expanding_line = visual.ShapeStim(win=win, lineColor='Firebrick',
    fillColor='Firebrick',
    vertices=[[0, 0], [0, 0], [1, 0], [0, 0]],
    pos=(-win.size[0] / 4, -win.size[1] / 24))
text = visual.TextStim(win, text='Press Spacebar When Line Lengths Match',
    pos=[0, 0], height=24, alignHoriz='center', alignVert='center',
    wrapWidth=win.size[0] * .8)
stim = [static_bar, expanding_line, text]

# Draw and Display first frame of screen
for s in stim:
    s.draw()
flip_time = win.flip()

# Clear all events from all ioHub event buffers.
io.clearEvents('all')

# Run until space bar is pressed, or larger than window
spacebar_rt = last_len = 0.0
while spacebar_rt == 0.0 or last_len >=  win.size[0]:
    # check for RT
    for kb_event in keyboard.getEvents():
        if kb_event.char == ' ':
            spacebar_rt = kb_event.time - flip_time
            break
            # Update visual stim as needed
    time_passed = core.getTime() - flip_time
    last_len = time_passed / line_size_match_delay * full_length
    expanding_line.setPos((-last_len / 2, -win.size[1] / 24))
    expanding_line.setVertices([[0, 0], [last_len, 0], [last_len, 5], [0, 5]])

    for s in stim:
        s.draw()
    # Clear all events from the ioHub Global event buffer only.
    io.clearEvents()
    win.flip()

io.clearEvents('all')

results = "Did you Forget to Press the Spacebar?\n"
if spacebar_rt > 0.0:
    msg = "RT: %.4f sec  ||  Perc. Length Diff: %.2f  ||  RT Error: %.4f sec\n"
    results = msg % (spacebar_rt,
                     fabs(last_len - full_length) / full_length * 100.0,
                     spacebar_rt - line_size_match_delay)

exitStr = "Press Any Key To Exit"
results = results + exitStr.center(len(results))
text.setText(results)
for s in stim:
    s.draw()
win.flip()

io.clearEvents('all')
while not keyboard.getPresses():
    io.wait(0.05)
    io.clearEvents()

win.close()
core.quit()

# The contents of this file are in the public domain.
