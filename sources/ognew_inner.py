#!/usr/bin/env python
# coding=utf-8
import argparse
import base64
import copy
import csv
import json
import multiprocessing
import os
import queue
import re
import shutil
import string
import subprocess
import sys
import time
# summarize option group from iiv.json


from exitog import getexitogs

# node format [src,dest,type(0:CD,1:DD,2:AST),details(T/F,Dlen,optionname)]
optionDirectSet = []
visited = []
Sog = {}
optionflows = {}
nametodirect = {}
cdedges = []
ddedges = []
cdfromto = {}
cdtofrom = {}
ddfromto = {}
ddtofrom = {}
nodeoption = {}
nodelist = {}
optiondivandiiv = {}
oglist = {}
vulfuncnames = ["memcpy", "mempcpy", "memmove", "memset", "strcpy", "stpcpy", "strcat", "sprintf", "vsprintf", "gets","strncat","memncpy"]

# sum of control nodes 
controlnums = 0
# sum of vulnerable function nodes
vulnums = 0
# sum of IIV nodes
iivnums = 0
# sum of DIV nodes
divnums = 0
# fucntions using global variables
useglobalfuncs = 0
# global variable and its option groups
globalwithogs = {}
# functions using structs
usestructfuncs = 0
# sum of funtions
allfuncs = 0
# all time cost
timeall = 0
# time of og generation
timeog = 0
# 
fromcontrolnum = 0
# 
ornum = 0





def proegdes(edgejsonfile):
    with open(edgejsonfile, "r") as f:
        content = json.load(f)
    cdedge = content["cd"]
    ddedge = content["dd"]
    nodes = content["node"]
    # control dependency
    for edge in cdedge:
        edgestart = edge[0]
        edgeend = edge[1]
        if edgestart not in cdfromto:
            cdfromto[edgestart] = []
        cdfromto[edgestart].append(edgeend)
        if edgeend not in cdtofrom:
            cdtofrom[edgeend] = []
        cdtofrom[edgeend].append(edgestart)
        cdedges.append((edgestart,edgeend))
    # data dependency
    for index in range(len(ddedge)):
        edge = ddedge[index]
        edgestart = edge[0]
        edgeend = edge[1]
        vars = edge[2]
        vartemp = []
        for var in vars:
            vartemp.append(var)
        # vars = []
        # vars.extend(vartemp)
        edge[2] = vartemp
        ddedges.append(edge)
        # print(edgestart,edgeend,vars)
        if edgestart not in ddfromto:
            ddfromto[edgestart] = []
        ddfromto[edgestart].append(edgeend)
        if edgeend not in ddtofrom:
            ddtofrom[edgeend] = []
        ddtofrom[edgeend].append(edgestart)
    # each node
    for node in nodes:
        nodelist[int(node)] = {}
        nodelist[int(node)]["line"] = int(nodes[node]["line"])
        nodelist[int(node)]["iscontrol"] = nodes[node]["iscontrol"]
        nodelist[int(node)]["calledname"] = nodes[node]["calledname"]
    # print(len(cdedges))   
    # print(len(nodelist))

def proiivs(iivfile):
    # process iiv
    global controlnums
    global vulnums
    global iivnums
    global divnums
    global oglist
    global useglobalfuncs
    global globalwithogs
    global usestructfuncs
    global allfuncs
    global timeog
    global timeall
    global fromcontrolnum
    global ornum
    with open(iivfile, "r") as f:
        content = json.load(f)

  
    for option in content:
        optionname = option
        if optionname not in ["iivariable","function","timeog","timeall","useglobal","funcptrnodes","usefuncptrnum"]:
            iivs = content[option]
            print("option",option)
            # div
            if "ddv" in iivs:
                divs = iivs["ddv"]
                for div in divs:
                    name = optionname
                    if name[0] =="'" and name[-1] == "'":
                        name = name[1:-1]
                    if name not in optiondivandiiv:
                        optiondivandiiv[name] = {}
                        optiondivandiiv[name]["div"] = 0
                        optiondivandiiv[name]["iiv"] = 0
                    optiondivandiiv[name]["div"] += 1  
                    nodeid = int(div)
                    divnums = divnums + 1
                    if divs[div]["iscontrol"] == 1:
                        controlnums += 1
                    if divs[div]["calledname"] in vulfuncnames:
                        vulnums += 1
                    if nodeid not in nodelist:
                        nodelist[nodeid] = {}
                        nodelist[nodeid]["iscontrol"] = divs[div]["iscontrol"]
                        nodelist[nodeid]["calledname"] = divs[div]["calledname"]
                        nodelist[nodeid]["line"] = divs[div]["line"]
                    if divs[div]["fromcontrol"] == 1:
                        fromcontrolnum += 1
                    if divs[div]["isor"] == 1:
                        ornum += 1
                    if (name,) not in oglist:
                        tname = (name,)
                        # print(tname)
                        oglist[tname] = {}
                        oglist[tname]["iscontrol"] = 0
                        oglist[tname]["controllist"] = []
                        oglist[tname]["nodes"] = []
                        oglist[tname]["vulfunc"] = []
                        oglist[tname]["vulfuncnode"] = {}
                        oglist[tname]["isvulfunc"] = 0
                        oglist[tname]["fromcontrol"] = 0
                        oglist[tname]["fromcontrolnodelist"] = []
                        oglist[tname]["ornum"] = 0
                        oglist[tname]["orlist"] = []
                        oglist[tname]["andnum"] = 0
                        oglist[tname]["andlist"] = []
                        oglist[tname]["paramnum"] = 0
                        oglist[tname]["paralist"] = []
                        oglist[tname]["parafunc"] = []
                        oglist[tname]["nodes"].append(nodeid)
                    if nodeid not in nodeoption:
                        nodeoption[nodeid] = []
                    # print(name)
                    # nodeoption[nodeid] = unionog(nodeoption[nodeid],[[name]])
        elif optionname == "iivariable":
            iivs = content["iivariable"]
            for iiv in iivs:
                nodeid = int(iiv)
                    # print(iivs[iiv])
                namelist = iivs[iiv]["optionname"]
                if namelist == []:
                    continue
                iivnums += 1
                
                if iivs[iiv]["iscontrol"] == 1:
                    controlnums += 1
                if iivs[iiv]["calledname"] in vulfuncnames:
                    vulnums += 1
                if nodeid not in nodelist:
                    nodelist[nodeid] = {}
                    nodelist[nodeid]["iscontrol"] = iivs[iiv]["iscontrol"]
                    nodelist[nodeid]["calledname"] = iivs[iiv]["calledname"]
                    nodelist[nodeid]["line"] = iivs[iiv]["line"]
                if iivs[iiv]["fromcontrol"] == 1:
                        fromcontrolnum += 1
                if iivs[iiv]["isor"] == 1:
                    ornum += 1
                for eachname in namelist:
                    if isinstance(eachname,str):
                        namelist = [namelist]
                        break
                # print(nodeid)
                for eachname in namelist:
                    # print(eachname)
                    tname = tuple(eachname)
                    # print(tname)
                    if tname not in oglist:
                        oglist[tname] = {}
                        oglist[tname]["iscontrol"] = 0
                        oglist[tname]["controllist"] = []
                        oglist[tname]["nodes"] = []
                        oglist[tname]["vulfuncnode"] = {}
                        oglist[tname]["isvulfunc"] = 0
                        oglist[tname]["fromcontrol"] = 0
                        oglist[tname]["fromcontrolnodelist"] = []
                        oglist[tname]["ornum"] = 0
                        oglist[tname]["orlist"] = []
                        oglist[tname]["andnum"] = 0
                        oglist[tname]["andlist"] = []
                        oglist[tname]["paramnum"] = 0
                        oglist[tname]["paralist"] = []
                        oglist[tname]["parafunc"] = []
                    oglist[tname]["nodes"].append(nodeid)
                    for name in eachname:
                        if name not in optiondivandiiv:
                            optiondivandiiv[name] = {}
                            optiondivandiiv[name]["div"] = 0
                            optiondivandiiv[name]["iiv"] = 0
                        optiondivandiiv[name]["iiv"] += 1  
                if nodeid not in nodeoption:
                    nodeoption[nodeid] = []
                # nodeoption[nodeid] = unionog(nodeoption[nodeid],namelist)
        elif optionname == "function":
            # global or struct use
            functions = content["function"]
            allfuncs = len(functions)
            for func in functions:
                if functions[func]["hasglobal"] == 1:
                    useglobalfuncs += 1
                if functions[func]["structvar"] == 1:
                    usestructfuncs += 1
        elif optionname == "timeog":
            timeog = content["timeog"]
        elif optionname == "timeall":
            timeall = content["timeall"]
        elif optionname == "useglobal":
            useglobals = content["useglobal"]
            for ug in useglobals:
                if ug != "number":
                    _oglist = useglobals[ug]
                    if len(oglist) > 0 and isinstance(_oglist,list):
                        _temp = []
                        for og in _oglist:
                            _temp.extend(og)
                            
                        globalwithogs[ug] = list(set(_temp))
                    else:
                        globalwithogs[ug] = _oglist
        
                    
        
                
    
        
    print("******************optiondivandiiv***********************")

def matchexitog(exitogs,og):
    for exits in exitogs:
        hasexit = 1
        for digit in exits:
            if digit not in og:
                hasexit = 0
                break
        if hasexit == 1:
            return (1,exits)
    return (0,[])

def ogcount(iivfile,finalfile,programname):
    # 
    oglen = {}
    maxoglen = []
    ogs = []
    ognum = 0
    ogwithlen = {}
    # print(len(nodeoption))
    exitinogjson = {}
    exitogs = getexitogs(iivfile)

    ogs1 = []
    for og in oglist:
        ogs1.append(og)
    exit_in_og = 0
    exitinogs = []
    for og in ogs1:
        # print(og)
      
        if og in exitogs:
            # print(f"exit og is in {og}")
            exit_in_og += 1
            exitinogjson[og] = og

            # del oglist[og]
        elif matchexitog(exitogs,og)[0] == 1:
            exitinogjson[og] = matchexitog(exitogs,og)[1]
            exit_in_og += 1

    for og in oglist:
        # print(og)
        if(len(og) > 1):
            ognum += 1
            maxoglen.append(ognum)
        ogs.append(og)
        # ogwithlen[og]
        if(len(og) not in oglen):
            oglen[len(og)] = 0
        oglen[len(og)] += 1
        oglist[og]["nodes"] = list(set(oglist[og]["nodes"]))
        for node in oglist[og]["nodes"]:
            if nodelist[node]["iscontrol"] == 1:
                oglist[og]["iscontrol"] += 1
                oglist[og]["controllist"].append(node)
            if nodelist[node]["calledname"] in vulfuncnames:
                oglist[og]["vulfuncnode"][node] = nodelist[node]["calledname"]
                oglist[og]["isvulfunc"] += 1
    print("oglen:",len(oglist))
    new_sys2 = sorted(oglist.items(),  key=lambda d: (len(d[1]["controllist"]),len(d[1]["nodes"])), reverse=True)
    new_sys3 = sorted(oglist.items(),  key=lambda d: (len(d[1]["vulfuncnode"]),len(d[1]["nodes"])), reverse=True)
    new_sys4 = sorted(oglist.items(),  key=lambda d: (len(d[1]["nodes"])), reverse=True)
    new_sys5 = sorted(ogs,  key=lambda i: len(i), reverse=True)

    finaldump = {}
    finaldump["program"] = programname
    finaldump["controlrank"] = {}
    finaldump["noderank"] = {}
    finaldump["lengthrank"] = new_sys5
    finaldump["vulrank"] = {}
    
    finaldump["oglen"] = oglen
    finaldump["oglist"] = ogs
    for ogs in new_sys2:
        og = ogs[0]
        finaldump["controlrank"][str(og)] = oglist[og]
    
    for ogs in new_sys3:
        og = ogs[0]
        finaldump["vulrank"][str(og)] = oglist[og]
    for ogs in new_sys4:
        og = ogs[0]
        finaldump["noderank"][str(og)] = oglist[og]
    average0 = 0
    if(len(maxoglen) != 0):
        average0 = sum(maxoglen)/len(maxoglen)
    finaldump["globalwithogs"] = globalwithogs
    finaldump["ognum"] = ognum
    finaldump["exitog"] = len(exitogs)
    exits = []
    for i in exitogs:
        exits.append(str(i))
    finaldump["exitogs"] = exits
    finaldump["exitinog"] = {}
    for key in exitinogjson:
        finaldump["exitinog"][str(key)] = str(exitinogjson[key])
    finaldump["exitinognum"] = exit_in_og
    finaldump["averageognum"] = average0
    finaldump["iivnum"] = iivnums
    finaldump["divnum"] = divnums
    finaldump["totalcontrol"] = controlnums
    finaldump["totalvulfunc"] = vulnums
    finaldump["totalornum"] = ornum
    finaldump["timeall"] = timeall
    finaldump["timeog"] = timeog
    finaldump["fromcontrolnum"] = fromcontrolnum
    finaldump["totalofgnodes"] = len(nodelist)
    finaldump["cdedges"] = len(cdedges)
    finaldump["ddedges"] = len(ddedges)
    finaldump["funcallnum"] = allfuncs
    finaldump["useglobalfuncs"] = useglobalfuncs
    finaldump["usestructfunc"] = usestructfuncs
    finaldump["involvedglobal"] = len(globalwithogs)
    
    with open(finalfile,"w") as f:
        json.dump(finaldump,f,indent=4) 



def trimOg(og):
    # simplify [[],[],[]]
    newog = []
    for op in og:
        if op == []:
            continue
        op = list(set(op))
        op.sort()
        if op not in newog:
            newog.append(op)
    return newog



def getRequest(programdir,temp,programname):      
        graphfile = programdir+"program_pdg.json"
        finalfile = programdir+"og"+temp+".json"
        iivfile = programdir+"iiv"+temp+".json"
        print(finalfile)
        # nodestart = arg.nodestart
        print(finalfile,iivfile)
        proegdes(graphfile)
        
        proiivs(iivfile)
        ogcount(iivfile,finalfile,programname)
    
    