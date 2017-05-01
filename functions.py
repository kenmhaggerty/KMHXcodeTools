#!/usr/bin/env python

# KMHXcodeTools
# functions.py
# Ken M. Haggerty
# CREATED: 2017 Mar 09
# EDITED:  2017 May 01

##### IMPORTS

import re

##### Shared

### Constants

PBXGroupSectionChildrenKey = "children"

### Functions

def sortElements(elements, order):
    orderCopy = list(order)
    sortedArray = []
    while len(orderCopy) > 0:
        item = orderCopy.pop(0)
        if PBXGroupSectionChildrenKey in item:
            orderCopy = item[PBXGroupSectionChildrenKey] + orderCopy
        elif item in elements:
            value = elements[item]
            sortedArray.append(value)
    return sortedArray

##### PBXProj Order

### Constants

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

### Functions

def updatePBXBuildFileSection(text, order):
    return text

##### PBXFileReference Section

### Functions

def updatePBXFileReferenceSection(text, order):
    return text

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
