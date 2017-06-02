#!/usr/bin/env python

# KMHXcodeTools
# pbxproj_organizer.py
# Ken M. Haggerty
# VERSION : 1.0
# CREATED : 2017 Mar 09
# EDITED  : 2017 Jun 02

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

PBXBuildFileSectionLineRegex = r"(^|\n)\s*(\w*).*=\s*\{.*fileRef\s*=\s*(\w+).*\};"
# 1 = (start of file / newline)
# 2 = PBXBuildFile ID
# 3 = PBXBuildFile fileRef

### Functions

def processPBXProjOrder(text):
    PBXGroupSectionRegex = generateSectionRegex("PBXGroup")
    pbxGroupSectionBody = re.search(PBXGroupSectionRegex, text).group(3)
    pbxGroupSections = re.findall(PBXGroupSectionGroupRegex, pbxGroupSectionBody)
    PBXBuildFileSectionRegex = generateSectionRegex("PBXBuildFile");
    pbxBuildFileSectionBody = re.search(PBXBuildFileSectionRegex, text).group(3)
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

### Regexes

PBXBuildFileSectionLineRegex = r"(^|\n)(\s*(\w*)\s*(\/\*\s*[^(\*\/)]*\s*\*\/){0,1}\s*={0,1}\s*(\{[^\}]*\}){0,1}\s*;)"
# 1 = (start of file / newline)
# 2 = (value)
# 3 = PBXBuildFile ID
# 4 = PBXBuildFile name and directory
# 5 = PBXBuildFile dictionary

PBXBuildFileSectionFileRefRegex = r"fileRef\s*=\s*(\w+)"
# 1 = PBXBuildFile fileRef

### Functions

def updatePBXBuildFileSection(text, order):
    PBXBuildFileSectionRegex = generateSectionRegex("PBXBuildFile")
    pbxBuildFileSectionBody = re.search(PBXBuildFileSectionRegex, text).group(3)
    pbxBuildFileSections = re.findall(PBXBuildFileSectionLineRegex, pbxBuildFileSectionBody)
    elements = {}
    for section in pbxBuildFileSections:
        fileRef = re.search(PBXBuildFileSectionFileRefRegex, section[4]).group(1)
        value = section[1]
        elements[fileRef] = value
    sortedArray = sortElements(elements, order)
    pbxBuildFileSectionBody = "\n".join(sortedArray)
    updatedText = re.sub(PBXBuildFileSectionRegex, r"\1\2" + pbxBuildFileSectionBody + r"\4\5", text, flags=re.IGNORECASE)
    return updatedText

##### PBXFileReference Section #####

### Regexes

PBXFileReferenceSectionLineRegex = r"(^|\n)(\s*(\w*)\s*(\/\*\s*[^(\*\/)]*\s*\*\/){0,1}\s*={0,1}\s*(\{[^\}]*\}){0,1}\s*;)"
# 1 = (start of file / newline)
# 2 = (value)
# 3 = PBXBuildFile reference ID
# 4 = PBXBuildFile name
# 5 = PBXBuildFile dictionary

### Functions

def updatePBXFileReferenceSection(text, order):
    PBXFileReferenceSectionRegex = generateSectionRegex("PBXFileReference")
    pbxFileReferenceSectionBody = re.search(PBXFileReferenceSectionRegex, text).group(3)
    pbxFileReferenceSectionLines = re.findall(PBXFileReferenceSectionLineRegex, pbxFileReferenceSectionBody)
    elements = {}
    for line in pbxFileReferenceSectionLines:
        fileRef = line[2]
        value = line[1]
        elements[fileRef] = value
    sortedArray = sortElements(elements, order)
    pbxFileReferenceSectionBody = "\n".join(sortedArray)
    updatedText = re.sub(PBXFileReferenceSectionRegex, r"\1\2" + pbxFileReferenceSectionBody + r"\4\5", text, flags=re.IGNORECASE)
    return updatedText

##### PBXFrameworksBuildPhase Section #####

### Functions

### Regexes

PBXFrameworksBuildPhaseSectionsRegex = r"([ \t]*(\w+)?[ \t]*(\/\*\s*([\w \t]*)[ \t]*\*\/)?\s*=\s*\{\s*\n([^\}]*files\s*=\s*\(\s([^\)]*,)?\s*\)\s*;[^\}]*)\}\s*;[^\n]*)"
# 1 = (value)
# 2 = PBXFrameworksBuildPhase section ID
# 3 = (unused)
# 4 = PBXFrameworksBuildPhase section title
# 5 = (unused)
# 6 = PBXFrameworksBuildPhase files

PBXFrameworksBuildPhaseFileRegex = r"(^|\n)(\s*(\w*)\s*(\/\*[^,]*\*\/),)"
# 1 = (start of file / newline)
# 2 = (value)
# 3 = PBXFrameworksBuildPhase file ID
# 4 = PBXFrameworksBuildPhase file name and directory

PBXFrameworksBuildPhaseFilesRegex = r"([\S\s]*files\s*=\s*\([ \t]*\n)([\S\s]*,[ \t]*)\s*\n([ \t]*\)\s*;[\S\s]*)"
# 1 = (start of file)
# 2 = PBXFrameworksBuildPhase files section
# 3 = (end of file)

def updatePBXFrameworksBuildPhaseSection(text, order):
    PBXFrameworksBuildPhaseSectionRegex = generateSectionRegex("PBXFrameworksBuildPhase")
    pbxFrameworksBuildPhaseSectionBody = re.search(PBXFrameworksBuildPhaseSectionRegex, text).group(3)
    pbxFrameworksBuildPhaseSections = re.findall(PBXFrameworksBuildPhaseSectionsRegex, pbxFrameworksBuildPhaseSectionBody)
    for section in pbxFrameworksBuildPhaseSections:
        value = section[0]
        pbxFrameworksBuildPhaseSectionFiles = re.findall(PBXFrameworksBuildPhaseFileRegex, section[5])
        elements = {}
        for file in pbxFrameworksBuildPhaseSectionFiles:
            fileRef = file[2]
            fileValue = file[1]
            elements[fileRef] = fileValue
        sortedArray = sortElements(elements, order)
        filesString = "\n".join(sortedArray)
        updatedSection = re.sub(PBXFrameworksBuildPhaseFilesRegex, r"\1" + filesString + r"\3", value, flags=re.IGNORECASE)
        pbxFrameworksBuildPhaseSectionBody = re.sub(value, updatedSection, pbxFrameworksBuildPhaseSectionBody, flags=re.IGNORECASE)
    updatedText = re.sub(PBXFrameworksBuildPhaseSectionRegex, r"\1\2" + pbxFrameworksBuildPhaseSectionBody + r"\4\5", text, flags=re.IGNORECASE)
    return updatedText

##### PBXGroup Section #####

### Functions

def updatePBXGroupSection(text, order):
    PBXGroupSectionRegex = generateSectionRegex("PBXGroup")
    pbxGroupSectionBody = re.search(PBXGroupSectionRegex, text).group(3)
    pbxGroupSections = re.findall(PBXGroupSectionGroupRegex, pbxGroupSectionBody)
    elements = {}
    for section in pbxGroupSections:
        fileRef = section[2]
        value = section[1]
        elements[fileRef] = value
    sortedArray = sortElements(elements, order)
    pbxGroupSectionBody = "\n".join(sortedArray)
    updatedText = re.sub(PBXGroupSectionRegex, r"\1\2" + pbxGroupSectionBody + r"\4\5", text, flags=re.IGNORECASE)
    return updatedText

##### PBXResourcesBuildPhase Section #####

### Regexes

PBXResourcesBuildPhaseSectionsRegex = r"(([ \t]*(\w*)[ \t]*(\/\*.*\*\/)[ \t]*=[ \t]*\{[^\}]*files[ \t]*=[ \t]*\(\n?)([^\)]*,[ \t]*)?\s*\n([^\}]*\}[ \t]*;))"
# 1 = (value)
# 2 = (start of file)
# 3 = PBXResourcesBuildPhase section ID
# 4 = PBXResourcesBuildPhase section name
# 5 = PBXResourcesBuildPhase section files
# 6 = (end of file)

PBXResourcesBuildPhaseFileRegex = r"(^|\n)(\s*(\w*)\s*(\/\*[^,]*\*\/),)"
# 1 = (start of file / newline)
# 2 = (value)
# 3 = PBXFrameworksBuildPhase fileRef
# 4 = PBXFrameworksBuildPhase file name and directory

### Functions

def updatePBXResourcesBuildPhaseSection(text, order):
    PBXResourcesBuildPhaseSectionRegex = generateSectionRegex("PBXResourcesBuildPhase")
    pbxResourcesBuildPhaseSectionBody = re.search(PBXResourcesBuildPhaseSectionRegex, text).group(3)
    pbxResourcesBuildPhaseSections = re.findall(PBXResourcesBuildPhaseSectionsRegex, pbxResourcesBuildPhaseSectionBody)
    for section in pbxResourcesBuildPhaseSections:
        value = section[0]
        pbxResourcesBuildPhaseSectionFiles = re.findall(PBXResourcesBuildPhaseFileRegex, section[4])
        elements = {}
        for file in pbxResourcesBuildPhaseSectionFiles:
            fileRef = file[2]
            fileValue = file[1]
            elements[fileRef] = fileValue
        sortedArray = sortElements(elements, order)
        filesString = "\n".join(sortedArray)
        updatedSection = re.sub(PBXResourcesBuildPhaseSectionsRegex, r"\2" + filesString + r"\6", value, flags=re.IGNORECASE);
        pbxResourcesBuildPhaseSectionBody = re.sub(value, updatedSection, pbxResourcesBuildPhaseSectionBody, flags=re.IGNORECASE)
    updatedText = re.sub(PBXResourcesBuildPhaseSectionRegex, r"\1\2" + pbxResourcesBuildPhaseSectionBody + r"\4\5", text, flags=re.IGNORECASE)
    return updatedText

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

##### Imports

import glob

##### Code

print "---------- STARTING PYTHON ----------"

# Obtain .xcodeproj files

projects = glob.glob("*.xcodeproj")

for project in projects:

    # Input

    filename = project + "/project.pbxproj"
    file = open(filename, "r+")
    text = "".join(file)

    # Processing

    order = processPBXProjOrder(text)

    text = updatePBXBuildFileSection(text, order)
    text = updatePBXFileReferenceSection(text, order)
    text = updatePBXFrameworksBuildPhaseSection(text, order)
    text = updatePBXGroupSection(text, order)
    text = updatePBXResourcesBuildPhaseSection(text, order)
    text = updatePBXSourcesBuildPhaseSection(text, order)

    # Save To File

    file.seek(0)
    file.write(text)
    file.truncate()
    file.close()

print "---------- PYTHON COMPLETE ----------"
