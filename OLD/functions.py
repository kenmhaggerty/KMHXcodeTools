#!/usr/bin/env python

# KMHXcodeTools
# functions.py
# Ken M. Haggerty
# CREATED: 2017 Mar 09
# EDITED:  2017 May 30

##### IMPORTS

import re

##### Shared

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

##### PBXProj Order

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

##### PBXBuildFile Section

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
