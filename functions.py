#!/usr/bin/env python

# KMHXcodeTools
# functions.py
# Ken M. Haggerty
# CREATED: 2017 Mar 09
# EDITED:  2017 May 01

##### IMPORTS

import re

##### PBXProj Order

### Constants

PBXGroupSectionChildrenKey = "children"
PBXGroupSectionNameKey = "name" # temp
PBXGroupSectionIdKey = "id"

### Regexes

PBXGroupSectionRegex = r"(^[\S\s]*)(\/\*\s*Begin\s+PBXGroup\s+section\s*\*\/s*[^\n]*\n)([\S\s]*)(\n\s*\/\*\s*End\s+PBXGroup\s+section\s*\*\/s*[^\n]*)([\S\s]*$)"
# 1 = Beginning of file
# 2 = PBXGroup section header
# 3 = PBXGroup section body
# 4 = PBXGroup section footer
# 5 = End of file

PBXGroupSectionGroupRegex = r"(.*=.*\{[^\}]*\}\;[\s]*)(\n|$)+"
# 1 = PBXGroup section
# 2 = (newline / end of file)

PBXGroupSectionIdRegex = r"^\s*(\w+)"
# 1 = PBXGroup ID

PBXGroupSectionChildrenRegex = r"children\s*=\s*\(([^\)\;]*)\)\;"
# 1 = PBXGroup children

PBXGroupSectionChildIdRegex = r"(^|\n)\s*(\w+)"
# 1 = (start of file / newline)
# 2 = PBXGroup child ID

PBXGroupSectionNameRegex = r"^.*\/\*\s*((\S+.*\.\S+)|\S+[^\*\/]*).*\*\/" # temp
# 1 = PBXGroup name
# 2 = (unused)

### Functions

def processPBXProjOrder(text):
    pbxGroupSectionBody = re.search(PBXGroupSectionRegex, text).group(3)
    pbxGroupSections = list(map(lambda x: x[0], re.findall(PBXGroupSectionGroupRegex, pbxGroupSectionBody)))
    elements = {}
    parentIds = set([])
    childrenIds = set([])
    for section in pbxGroupSections:
        sectionId = re.search(PBXGroupSectionIdRegex, section).group(1)
        childrenBody = re.search(PBXGroupSectionChildrenRegex, section).group(1)
        childIds = list(map(lambda x: x[1], re.findall(PBXGroupSectionChildIdRegex, childrenBody)))
        dictionary = {}
        if len(childIds) > 0:
            dictionary[PBXGroupSectionChildrenKey] = childIds
        try: # temp
            name = re.search(PBXGroupSectionNameRegex, section).group(1)
            dictionary[PBXGroupSectionNameKey] = name
        except Exception: 
            pass
        elements[sectionId] = dictionary
        parentIds.update([sectionId])
        childrenIds.update(childIds)
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
        if child in source:
            children.pop(i)
            grandchildren = generateChildren(child, source)
            children.insert(i, grandchildren)
        i += 1
    dictionary[PBXGroupSectionChildrenKey] = children
    return dictionary

##### PBXBuildFile Section

### Constants

# PBXBuildFileSectionIdKey = "id"
# PBXBuildFileSectionFileRefKey = "fileRef"
# PBXBuildFileSectionValueKey = "value"
# PBXBuildFileSectionNameKey = "name"
# PBXBuildFileSectionDirectoryKey = "directory"
# PBXBuildFileSectionDictionaryKey = "dictionary"

### Regexes

PBXBuildFileSectionRegex = r"(^[\S\s]*)(\/\*\s*Begin\s+PBXBuildFile\s+section\s*\*\/s*[^\n]*\n)([\S\s]*)(\n\s*\/\*\s*End\s+PBXBuildFile\s+section\s*\*\/s*[^\n]*)([\S\s]*$)"
# 1 = Beginning of file
# 2 = PBXBuildFile section header
# 3 = PBXBuildFile section body
# 4 = PBXBuildFile section footer
# 5 = End of file

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
    pbxBuildFileSectionBody = re.search(PBXBuildFileSectionRegex, text).group(3)
    pbxBuildFileSections = re.findall(PBXBuildFileSectionLineRegex, pbxBuildFileSectionBody)
    elements = {}
    for section in pbxBuildFileSections:
        fileRef = re.search(PBXBuildFileSectionFileRefRegex, section[4]).group(1)
        value = section[1]
        elements[fileRef] = value
    orderCopy = list(order)
    array = []
    while len(orderCopy) > 0:
        item = orderCopy.pop(0)
        if PBXGroupSectionChildrenKey in item:
            orderCopy = item[PBXGroupSectionChildrenKey] + orderCopy
        elif item in elements:
            value = elements[item]
            array.append(value)
    pbxBuildFileSectionBody = "\n".join(array)
    updatedText = re.sub(PBXBuildFileSectionRegex, r"\1\2" + pbxBuildFileSectionBody + r"\4\5", text, flags=re.IGNORECASE)
    return updatedText

##### PBXFileReference Section

### Regexes

PBXFileReferenceSectionRegex = r"(^[\S\s]*)(\/\*\s*Begin\s+PBXFileReference\s+section\s*\*\/s*[^\n]*\n)([\S\s]*)(\n\s*\/\*\s*End\s+PBXFileReference\s+section\s*\*\/s*[^\n]*)([\S\s]*$)"
# 1 = Beginning of file
# 2 = PBXGroup section header
# 3 = PBXGroup section body
# 4 = PBXGroup section footer
# 5 = End of file

PBXFileReferenceSectionLineRegex = r"(^|\n)(\s*(\w*)\s*(\/\*\s*[^(\*\/)]*\s*\*\/){0,1}\s*={0,1}\s*(\{[^\}]*\}){0,1}\s*;)"
# 1 = (start of file / newline)
# 2 = (value)
# 3 = PBXBuildFile reference ID
# 4 = PBXBuildFile name
# 5 = PBXBuildFile dictionary

### Functions

def updatePBXFileReferenceSection(text, order):
    pbxFileReferenceSectionBody = re.search(PBXFileReferenceSectionRegex, text).group(3)
    pbxFileReferenceSectionLines = re.findall(PBXFileReferenceSectionLineRegex, pbxFileReferenceSectionBody)
    elements = {}
    for line in pbxFileReferenceSectionLines:
        fileRef = line[2]
        value = line[1]
        elements[fileRef] = value
    orderCopy = list(order)
    array = []
    while len(orderCopy) > 0:
        item = orderCopy.pop(0)
        if PBXGroupSectionChildrenKey in item:
            orderCopy = item[PBXGroupSectionChildrenKey] + orderCopy
        elif item in elements:
            value = elements[item]
            array.append(value)
    pbxFileReferenceSectionBody = "\n".join(array)
    updatedText = re.sub(PBXFileReferenceSectionRegex, r"\1\2" + pbxFileReferenceSectionBody + r"\4\5", text, flags=re.IGNORECASE)
    return updatedText

##### PBXFrameworksBuildPhase Section

### Functions

def updatePBXFrameworksBuildPhaseSection(text, order):
    return text

##### PBXGroup Section

### Functions

def updatePBXGroupSection(text, order):
    return text

##### PBXResourcesBuildPhase Section

### Functions

def updatePBXResourcesBuildPhaseSection(text, order):
    return text

##### PBXSourcesBuildPhase Section

### Functions

def updatePBXSourcesBuildPhaseSection(text, order):
    return text
