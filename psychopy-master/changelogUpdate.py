#!/usr/bin/env python

# this script replaces hashtags with a sphinx URL string (to the github issues or pull request)
# written by Jon with regex code by Jeremy

import re

input_path = 'psychopy/CHANGELOG.txt'
output_path = 'docs/source/changelog.rst'

def repl_issue(m):
    g = m.group(1)
    return g.replace('#', '`#') +  " <https://github.com/psychopy/psychopy/issues/" + g.strip(' (#') + ">`_"

def repl_commit(m):
    g = m.group(1)
    return g.replace('#', '`commit:')[:18] +  " <https://github.com/psychopy/psychopy/commit/" + g.strip(' (#') + ">`_"

def repl_blue(m):
    g = m.group(1)
    g = g.replace('`', "'")
    return g.replace('CHANGE', ':blue:`CHANGE') + "`\n"

# raw .txt form of changelog:
txt = open(input_path, "rU").read()

# programmatic replacements:
hashtag = re.compile(r"([ (]#\d{3,5})\b")
print "found %i issue tags" %(len(hashtag.findall(txt)))
txt_hash = hashtag.sub(repl_issue, txt)

hashtag = re.compile(r"([ (]#[0-9a-f]{6,})\b")
print "found %i commit tags" %(len(hashtag.findall(txt_hash)))
txt_hash = hashtag.sub(repl_commit, txt_hash)

blue = re.compile(r"(CHANGE.*)\n")
print "found %i CHANGE" %(len(blue.findall(txt_hash)))
txt_hashblue = blue.sub(repl_blue, txt_hash)

# one-off specific .rst directives:
newRST = txt_hashblue.replace('.. note::', """.. raw:: html

    <style> .blue {color:blue} </style>

.. role:: blue

.. note::""", 1)

# add note about blue meaning a change?

with open(output_path, "wb") as doc:
    doc.write(newRST)

#test:
#text = "yes #123\n yes (#4567)\n; none of `#123, #3, #45, #12345 #123a"
#newText = expr.sub(repl, text)
#print newText
