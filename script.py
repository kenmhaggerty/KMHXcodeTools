#!/usr/bin/env python

# KMHXcodeTools
# script.py
# Ken M. Haggerty
# CREATED: 2017 Mar 09
# EDITED:  2017 Apr 28

##### IMPORTS

from functions import *

##### INPUTS

filename = "Sample.xcodeproj/project.pbxproj"

##### CONSTANTS

directory = "source/"

##### CODE

print "---------- STARTING PYTHON ----------"

### Input

file = open(directory + filename, "r+")
text = "".join(file)

### Processing

order = processPBXProjOrder(text)

text = updatePBXBuildFileSection(text, order)
text = updatePBXFileReferenceSection(text, order)
text = updatePBXFrameworksBuildPhaseSection(text, order)
text = updatePBXGroupSection(text, order)
text = updatePBXResourcesBuildPhaseSection(text, order)
text = updatePBXSourcesBuildPhaseSection(text, order)

### Save To File

# file.seek(0)
# file.write(text)
# file.truncate()
# file.close()

print "---------- PYTHON COMPLETE ----------"
