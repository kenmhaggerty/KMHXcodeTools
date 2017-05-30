#!/usr/bin/env python

# KMHXcodeTools
# pbxproj_organizer.py
# Ken M. Haggerty
# VERSION : 1.0
# CREATED : 2017 May 30
# EDITED  : 2017 May 30

########## CODE ##########

##### Imports #####

import re

##### Shared #####

### Constants

PBXGroupSectionChildrenKey = "children"
PBXGroupSectionIdKey = "fileRef"
PBXBuildSectionIdKey = "id"

### Regexes

PBXSectionRegex_1 = r"(^[\S\s]*)(\/\*\s*Begin\s+"
PBXSectionRegex_2 = r"\s+section\s*\*\/s*[^\n]*\n)([\S\s]*)(\n\s*\/\*\s*End\s+"
PBXSectionRegex_3 = r"\s+section\s*\*\/s*[^\n]*)([\S\s]*$)"
# 1 = Beginning of file
# 2 = PBXSection header
# 3 = PBXSection body
# 4 = PBXSection footer
# 5 = End of file

### Functions

def generateSectionRegex(section):
    return PBXSectionRegex_1 + section + PBXSectionRegex_2 + section + PBXSectionRegex_3

def sortElements(elements, order):
    orderCopy = list(order)
    sortedArray = []
    while len(orderCopy) > 0:
        item = orderCopy.pop(0)
        fileRef = item[PBXGroupSectionIdKey]
        if PBXGroupSectionChildrenKey in item:
            orderCopy = item[PBXGroupSectionChildrenKey] + orderCopy
        if fileRef in elements:
            value = elements[fileRef]
            sortedArray.append(value)
        elif PBXBuildSectionIdKey in item:
            buildId = item[PBXBuildSectionIdKey]
            if buildId in elements:
                value = elements[buildId]
                sortedArray.append(value)
    return sortedArray

##### PBXProj Order #####

### Constants

PBXGroupSectionNameKey = "name" # temp

### Regexes

PBXGroupSectionGroupRegex = r"(^|\n)([^\n\w]*(\w*)\s*(\/\*\s*(.*)\s*\*\/){0,1}\s*=\s*(\{[^\}]*\})\s*;[^\n]*)"
# 1 = (start of file / newline)
# 2 = (value)
# 3 = PBXGroupSection fileRef
# 4 = (unused)
# 5 = PBXGroupSection name # temp
# 6 = PBXGroupSection dictionary

PBXGroupSectionChildrenRegex = r"children\s*=\s*\(([^\)\;]*)\)\;"
# 1 = PBXGroup children

PBXGroupSectionChildRegex = r"(^|\n)(\s*(\w*)\s*(\/\*\s*((\S+.*\.\S+)|\S+[^\*\/]*).*\*\/)\s*,[^\n]*)"
# 1 = (start of file / newline)
# 2 = (value)
# 3 = PBXGroupSection child fileRef
# 4 = PBXGroupSection name and directory # temp
# 5 = PBXGroupSection name # temp
# 6 = (unused)

PBXBuildFileSectionRegex = r"\/\*\s*Begin\s*PBXBuildFile\s*section\s*\*\/\n*([\S\s]*)\n*\/\*\s*End\s*PBXBuildFile\s*section\s*\*\/"
# 1 = PBXBuildFileSection body

PBXBuildFileSectionLineRegex = r"(^|\n)\s*(\w*).*=\s*\{.*fileRef\s*=\s*(\w+).*\};"
# 1 = (start of file / newline)
# 2 = PBXBuildFile ID
# 3 = PBXBuildFile fileRef

### Functions

def processPBXProjOrder(text):
    PBXGroupSectionRegex = generateSectionRegex("PBXGroup")
    pbxGroupSectionBody = re.search(PBXGroupSectionRegex, text).group(3)
    pbxGroupSections = re.findall(PBXGroupSectionGroupRegex, pbxGroupSectionBody)
    pbxBuildFileSectionBody = re.search(PBXBuildFileSectionRegex, text).group(1)
    pbxBuildFileSectionLines = re.findall(PBXBuildFileSectionLineRegex, pbxBuildFileSectionBody)
    fileRefDictionary = {}
    for line in pbxBuildFileSectionLines:
        fileRef = line[2]
        fileId = line[1]
        fileRefDictionary[fileRef] = fileId
    elements = {}
    parentIds = set([])
    childrenIds = set([])
    for section in pbxGroupSections:
        fileRef = section[2]
        dictionary = section[5]
        children = re.search(PBXGroupSectionChildrenRegex, dictionary).group(1)
        children = re.findall(PBXGroupSectionChildRegex, children)
        childDictionaries = []
        for child in children:
            childFileRef = child[2]
            childName = child[4]
            dictionary = {
                PBXGroupSectionIdKey : childFileRef,
                PBXGroupSectionNameKey : childName
            }
            try:
                fileId = fileRefDictionary[childFileRef]
                dictionary[PBXBuildSectionIdKey] = fileId
            except Exception:
                pass
            childDictionaries.append(dictionary)
        children = list(map(lambda x: x[2], children))
        dictionary = {}
        if len(childDictionaries) > 0:
            dictionary[PBXGroupSectionChildrenKey] = childDictionaries
        try: # temp
            name = section[4]
            dictionary[PBXGroupSectionNameKey] = name
        except Exception: 
            pass
        elements[fileRef] = dictionary
        parentIds.update([fileRef])
        childrenIds.update(children)
    parents = parentIds - childrenIds
    pbxProjOrder = []
    for parent in parents:
        dictionary = generateChildren(parent, elements)
        pbxProjOrder.append(dictionary)
    return pbxProjOrder

def generateChildren(node, source):
    dictionary = {
        PBXGroupSectionIdKey : node
    }
    if PBXGroupSectionNameKey in source[node]: # temp
        dictionary[PBXGroupSectionNameKey] = source[node][PBXGroupSectionNameKey]
    children = source[node][PBXGroupSectionChildrenKey]
    i = 0
    while i < len(children):
        child = children[i]
        childFileRef = child[PBXGroupSectionIdKey]
        if childFileRef in source:
            children.pop(i)
            grandchildren = generateChildren(childFileRef, source)
            children.insert(i, grandchildren)
        i += 1
    dictionary[PBXGroupSectionChildrenKey] = children
    return dictionary

##### PBXBuildFile Section #####

### Functions

def updatePBXBuildFileSection(text, order):
    return text

##### PBXFileReference Section #####

### Functions

def updatePBXFileReferenceSection(text, order):
    return text

##### PBXFrameworksBuildPhase Section #####

### Functions

def updatePBXFrameworksBuildPhaseSection(text, order):
    return text

##### PBXGroup Section #####

### Functions

def updatePBXGroupSection(text, order):
    return text

##### PBXResourcesBuildPhase Section #####

### Functions

def updatePBXResourcesBuildPhaseSection(text, order):
    return text

##### PBXSourcesBuildPhase Section #####

### Regexes

PBXSourcesBuildPhaseSectionsRegex = r"(([ \t]*(\w*)[ \t]*(\/\*.*\*\/)[ \t]*=[ \t]*\{[ \t]*[^\}]*files[ \t]*=[ \t]*\([ \t]*)\n?([^\)]*,[ \t]*)?\s*\n([ \t]*\)[ \t]*;[^\}]*\}[ \t]*;))"
# 1 = (value)
# 2 = (start of file)
# 3 = PBXSourcesBuildPhase section ID
# 4 = PBXSourcesBuildPhase section name
# 5 = PBXSourcesBuildPhase section files
# 6 = (end of file)

PBXSourcesBuildPhaseFileRegex = r"(^|\n)(\s*(\w*)\s*(\/\*[^,]*\*\/),)"
# 1 = (start of file / newline)
# 2 = (value)
# 3 = PBXSourcesBuildPhase file ID
# 4 = PBXSourcesBuildPhase file name and directory

### Functions

def updatePBXSourcesBuildPhaseSection(text, order):
    PBXSourcesBuildPhaseSectionRegex = generateSectionRegex("PBXSourcesBuildPhase")
    pbxSourcesBuildPhaseSectionBody = re.search(PBXSourcesBuildPhaseSectionRegex, text).group(3)
    pbxSourcesBuildPhaseSections = re.findall(PBXSourcesBuildPhaseSectionsRegex, pbxSourcesBuildPhaseSectionBody)
    for section in pbxSourcesBuildPhaseSections:
        value = section[0]
        pbxSourcesBuildPhaseFiles = re.findall(PBXSourcesBuildPhaseFileRegex, section[4])
        elements = {}
        for file in pbxSourcesBuildPhaseFiles:
            fileRef = file[2]
            fileValue = file[1]
            elements[fileRef] = fileValue
        sortedArray = sortElements(elements, order)
        filesString = "\n".join(sortedArray)
        updatedSection = re.sub(PBXSourcesBuildPhaseSectionsRegex, r"\2" + filesString + r"\6", value, flags=re.IGNORECASE)
        pbxSourcesBuildPhaseSectionBody = re.sub(value, updatedSection, pbxSourcesBuildPhaseSectionBody, flags=re.IGNORECASE)
    updatedText = re.sub(PBXSourcesBuildPhaseSectionRegex, r"\1\2" + pbxSourcesBuildPhaseSectionBody + r"\4\5", text, flags=re.IGNORECASE)
    return updatedText

########## SCRIPT ##########

##### Imports #####

import glob

##### Code #####

print "---------- STARTING PYTHON ----------"

### Obtain .xcodeproj files

projects = glob.glob("*.xcodeproj")

for project in projects:

    ### Input

    filename = project + "/project.pbxproj"
    file = open(filename, "r+")
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
