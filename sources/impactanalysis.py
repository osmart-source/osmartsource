#!/usr/bin/python
# 完整无优化
# 结构体到结构体的成员变量之间是没有数据依赖关系的
# 结构体成员变量到成员变量有dd，但是如果需要先到成员变量，再到成员变量的赋值点
# 函数参数 一个参数受另一个参数影响如何去判断
# 一个函数里面结构体就记一个，以及相对应的成员变量
# 这种主要去解决返回值，如果返回值是这个结构体的话，传给调用点，有点复杂，再规划一下

import argparse
import sys


import copy
import json
import os
import queue
import subprocess
import time

import utils
from cfg_graph import *
from pdg_graph import *




cfgdot = ""
# globalvariables,methods = [],[]
methodtodot = {"SWFMovie_add":"859"}
methodtograph = {}
# globalvariables =[]
taintflow = []
cfgdir = ""
pdgdir = ""
astdir = ""
processedfunction = {}
node2og = {}
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
nodeinfojson = {}
pdgwithdd = {}
vulfuncnames = ["memcpy", "mempcpy", "memmove", "memset", "strcpy", "strncpy", "strcat", "sprintf", "vsprintf", "gets","strncat","memncpy"]

functionwithogs = {}
functionwithoutparam = {}
functionwithiiv = {}
functionwithiiv["timeog"] = 0

globalinfo = {}
timeog = {}

function_node_arrange = {}

function_node_line = {}

finalflowlist = {}

mode2options = {}

opmodes = []
programname = ""


class Flow_Node:
    num = -1
    frominput = 0
    fromglobal = 0
    
    funcname = ""
    pdgnode = PDG_Node(num)
    line = 0
    def __init__(self, num):
        self.num = num
        # self.vars = []
        self.vars = {}
        self.controlog = []
        self.num = -1
        self.rominput = 0
        self.fromglobal = 0
        self.iscontrol = 0
        self.fromcontrol = 0
        self.funcname = ""
        self.calledname = ""
        self.pdgnode = PDG_Node(num)
        self.line = 0
        self.isor = 0
        self.isand = 0
        self.paramiiv = 0
        self.optionlist = []
        self.isopor = 0
        self.useglobal = 0
        self.usestruct = 0

def proegdes(edgejsonfile):
    # extract cd and dd and edges
    with open(edgejsonfile, "r") as f:
        content = json.load(f)
    cdedges = content["cd"]
    ddedge = content["dd"]
    nodes = content["node"]
    for edge in cdedges:
        edgestart = edge[0]
        edgeend = edge[1]
        if edgestart not in cdfromto:
            cdfromto[edgestart] = []
        cdfromto[edgestart].append(edgeend)
        if edgeend not in cdtofrom:
            cdtofrom[edgeend] = []
        cdtofrom[edgeend].append(edgestart)
    for index in range(len(ddedge)):
        edge = ddedge[index]
        edgestart = edge[0]
        edgeend = edge[1]
        vars = edge[2]
        vartemp = []
        for var in vars:
            vartemp.append(var)
      
        edge[2] = vartemp
        ddedges.append(edge)
      
        if edgestart not in ddfromto:
            ddfromto[edgestart] = []
        ddfromto[edgestart].append(edgeend)
        if edgeend not in ddtofrom:
            ddtofrom[edgeend] = []
        ddtofrom[edgeend].append(edgestart)
    for node in nodes:
        nodelist[int(node)] = {}
        nodelist[int(node)]["line"] = int(nodes[node]["line"])
        nodelist[int(node)]["iscontrol"] = nodes[node]["iscontrol"]
        nodelist[int(node)]["calledname"] = nodes[node]["calledname"]


def getVar(parent,cur):
    var = []
    for edge in ddedges:
        if(edge[0] == parent and edge[1] == cur):
            var = edge[2]
    return var
        
def controlPreds(dest):
    res = []
    if dest in cdtofrom:
        return cdtofrom[dest]
    return res

def dataPreds(dest):
    res = []
    if dest in ddtofrom:
        return ddtofrom[dest]
    return res

def predVisited(dest,visited):
    srclist = []
    if dest in cdtofrom:
        preds = cdtofrom[dest]
        srclist.extend(preds)
    if dest in ddtofrom:
        preds = ddtofrom[dest]
        srclist.extend(preds)
    
    for src in srclist:
        if src not in visited:
            return 0
    return 1

def succs(src):
    res = []

    if src in cdfromto:
        res.extend(cdfromto[src])
    if src in ddfromto:
        res.extend(ddfromto[src])
    return res

        
def processdot(funcname,cfgdir1,pdgdir1,astdir1,globaltxt):
    (globalvariables,methods) = get_global_info(globaltxt)
    if funcname not in methods:
        print("not in method ",funcname)
        return
    if funcname in methodtodot:
        dot = methodtodot[funcname]
    else:
        dot = utils.get_method_file(funcname, astdir1)

        if(dot):
            dot = dot[0]
            methodtodot[funcname] = dot
        else:
            dot = ""
            methodtodot[funcname] = ""
 
    if dot != "":       
        cfgfile = os.path.join(cfgdir1,dot+"-cfg.dot")
        pdgfile = os.path.join(pdgdir1,dot+"-pdg.dot")
        pdg_g = pdgpreprocess(funcname,pdgfile,globaltxt)
        cfg_g = ""
        methodtograph[funcname] = [cfg_g,pdg_g]

def constructdd(pdg_g):

    if pdg_g in pdgwithdd:
        return pdgwithdd[pdg_g]
    ddrelation = {}
    toddrelation = {}

    edgelist = pdg_g.edge_set
    for edge in edgelist:
        if edgelist[edge].isddg:
            fromid = edge[0]
            toid = edge[1]
            variables = edgelist[edge].ddgparam
            if fromid not in ddrelation:
                ddrelation[fromid] = []
            for variable in variables:
                ddrelation[fromid].append((toid,variable))

            if toid not in toddrelation:
                toddrelation[toid] = []
            for variable in variables:
                toddrelation[toid].append((fromid,variable))
    pdgwithdd[pdg_g] = ((ddrelation,toddrelation))         
    return (ddrelation,toddrelation)

def cdrelation(pdg_g):
    nodelist = pdg_g.node_set
    edgelist = pdg_g.egde_set
    cdrealtion = {}
    tocdrealtion = {}
    for edge in edgelist:
        if edge.iscdg == 1:
            edgestart = edge.start
            edgeend = edge.end
            if edgestart not in cdrealtion:
                cdrealtion[edgestart] = []
            cdrealtion[edgestart].append(edgeend)
            if edgeend not in tocdrealtion:
                tocdrealtion[edgeend] = []
            tocdrealtion[edgeend].append(edgestart)
    return (cdrealtion,tocdrealtion)

def cfgcfrelation(cfg_g):
    nodelist = cfg_g.node_set
    edgelist = cfg_g.edge_set
    tocfgrelation = {}
    for edge in edgelist:
        edgestart = edge[0]
        edgeend = edge[1]
        if edgestart not in cfgrelation:
            cfgrelation[edgestart] = []
        cfgrelation[edgestart].append(edgeend)
        if edgeend not in tocfgrelation:
            tocfgrelation[edgeend] = []
        tocfgrelation[edgeend].append(edgestart)
    return (cfgrelation,tocfgrelation)


def ddarrangenode(funcname,cfgdir1,ddrelation,pdg_g,globaltxt):
    if funcname in function_node_arrange and funcname in function_node_line:
        return (function_node_arrange[funcname],function_node_line[funcname])
    dot = methodtodot[funcname]
    nodeset = pdg_g.node_set
    cfgpath = os.path.join(cfgdir1,dot+"-cfg.dot")
    cfg_g = cfgpreprocess(funcname,cfgpath,globaltxt)
    if not cfg_g:
        print("cfg is null",funcname,cfgpath)
        return ([],{})
    (cfgrelation,tocfgrelation) = cfgcfrelation(cfg_g)
    cfgnodeset = cfg_g.node_set
    cfgnodeline = {}
    for node in cfgnodeset:
        line = int(cfgnodeset[node].line)
        if line in cfgnodeline:
            cfgnodeline[line].append(node)
        else:
            cfgnodeline[line] = [node]
    nodeline = {}
    lines = []
    for node in nodeset:
        line = int(nodeset[node].line)
        lines.append(line)
        if line in nodeline:
            nodeline[line].append(node)
        else:
            nodeline[line] = [node]
    lines = list(set(lines))
    lines.sort()
    sortlist = []
    for line in lines:
        if(len(nodeline[line]) > 1):
            nodeid = nodeline[line][0]
            if(nodeset[nodeid].type_str  in ["METHOD","METHOD_RETURN","PARAM"]):
                sortlist.extend(nodeline[line])
            else:
                if line in cfgnodeline:
                    temp = arrangenode(nodeline[line],ddrelation,cfgnodeline[line],cfgrelation)
                    sortlist.extend(temp)
                else:
                    a = nodeline[line]
                    a.reverse()
                    sortlist.extend(a)
        else:
            sortlist.extend(nodeline[line])

    function_node_arrange[funcname] = sortlist
    function_node_line[funcname] = nodeline

    return (sortlist,nodeline)  

def arrangenode(pdgnodes,ddrelation,cfgnodes,cfgrelation):
    ret = []
    cfgnodescur = []
    if pdgnodes != cfgnodes:
        pdgnodeset = set(pdgnodes)
        cfgnodeset = set(cfgnodes)
        if pdgnodeset.issubset(cfgnodeset):
            cfgnodescur = pdgnodes
    else:
        cfgnodescur = cfgnodes
    
    if cfgnodescur == []:
        pdgnodes.reverse()
        ret = pdgnodes
        return ret
 
    for node in cfgnodescur:
        indegree = dict((u,0) for u in cfgnodescur)
    num = len(indegree)
    for u in cfgrelation:
        for v in cfgrelation[u]:
            if u in cfgnodescur and v in cfgnodescur:
                indegree[v] += 1

    Q = [u for u in indegree if indegree[u] == 0]

    seq = []

    Q1 = copy.deepcopy(Q)
    while Q:
        u = Q.pop(0)
        seq.append(u)
        if u in cfgrelation:
            for v in cfgrelation[u]:
                if v in cfgnodescur:
                    indegree[v] -= 1
                    if indegree[v] == 0:
                        Q.append(v)
    if(len(seq) == num):
        return seq
    else:
        pdgnodes.reverse()
        seq = pdgnodes

    return seq

def outparam(funcname,pdgdir1,astdir1,globaltxt):
    if funcname in functionwithoutparam:
        return functionwithoutparam[funcname]
    
    processdot(funcname,"",pdgdir1,astdir1,globaltxt)
    pdg_g = methodtograph[funcname][1]
    edges = pdg_g.edge_set
    nodes = pdg_g.node_set
    (ddrelation,toddrelation) = constructdd(pdg_g)
    paramsdict = {}
    paramid = {}
    params = []
    assigned = []
    paramindex = 0
    assignnode = {}
    paramnode = {}
    
    for nodeid in nodes:
        nodetemp = nodes[nodeid]
        if nodes[nodeid].type_str == "PARAM":
            paramvar = getparamvariable(nodeid,ddrelation)
            needappend = 0
            if "char" in nodes[nodeid].dot_src:
                if ("char **" in nodes[nodeid].dot_src or "char**" in nodes[nodeid].dot_src):
                    needappend = 1
            elif "short *" in nodes[nodeid].dot_src:
                pass
            elif "*" in nodes[nodeid].dot_src:
                needappend = 1
            if needappend == 1:
                params.append(paramvar)
                paramsdict[paramvar] = paramindex
                paramid[paramvar] = nodeid
            paramindex += 1
        else:
            (src,dest,calledname,funcinfo,controls,iscontrol,parseok,orconditionlist) = stateOperands(funcname,nodes[nodeid],astdir1,globaltxt)
            calledname = list(set(calledname))
            for name in calledname:
                if name in ["sprintf","snprintf","strcat","strncat","sscanf"]:
                    dest0 = src[0]
                    if len(dest) > 1:
                        dest = []
                        dest.append(dest0)
       
            for op in dest:
                op0 = op
                if op[0] == "*":
                    op = op[1:]
                if "." in op:
                    op = op.split(".")[0]
                elif "-&gt;" in op:
                    op = op.split("-&gt;")[0]
                for param in params:
                    if op == param or op0 == param:
                        assigned.append(param)
                        assignnode[param] = nodeid
            

    assigned = list(set(assigned))
    assigned_list = []
    for _assign in assigned:
        assigned_list.append(paramsdict[_assign])
    functionwithoutparam[funcname] = (assigned_list,assignnode)
    return (assigned_list,assignnode)

def stateReturns(funcname,node,astdir1,globaltxt):
    (globalvariables,methods) = get_global_info(globaltxt)
    nodestr = str(node.dot_src)
    num = nodestr.count("\\012")
    cfgdir1 = astdir1[0:-3]+"cfg"
    pdgdir1 = astdir1[0:-3]+"pdg"
    returnvalue = ""
    if funcname in methods and funcname not in methodtodot:
        processdot(funcname,cfgdir1,pdgdir1,astdir1,globaltxt)
    if funcname in methodtodot and methodtodot[funcname] != "":
        dotfile = methodtodot[funcname]
        astfile = os.path.join(astdir1,str(dotfile)+"-ast.dot")
        
        returnvalue = utils.get_return(int(node.line),astfile,num)
    return returnvalue

def stateOperands(funcname,node,astdir1,globaltxt):
    global nodeinfojson
    if nodeinfojson == {}:
        programdir = globaltxt[:globaltxt.rfind("/")]
        nodeinfodir = os.path.join(programdir,"nodeinfo.json")
        with open(nodeinfodir,"r") as f:
            nodeinfojson = json.load(f)
    if str(node.num) in nodeinfojson:
        nodeid = str(node.num)
        return (nodeinfojson[nodeid]["src"],nodeinfojson[nodeid]["dest"],nodeinfojson[nodeid]["calledname"],nodeinfojson[nodeid]["funcinfo"],nodeinfojson[nodeid]["controls"],nodeinfojson[nodeid]["iscontrol"],nodeinfojson[nodeid]["parseok"],nodeinfojson[nodeid]["orconditionlist"])
    else:
        return _stateOperands(funcname,node,astdir1,globaltxt)
    
def _stateOperands(funcname,node,astdir1,globaltxt):
    (globalvariables,methods) = get_global_info(globaltxt)
    nodestr = str(node.dot_src)
    num = nodestr.count("\\012")
    cfgdir1 = astdir1[0:-3]+"cfg"
    pdgdir1 = astdir1[0:-3]+"pdg"
    if funcname in methods and funcname not in methodtodot:
        processdot(funcname,cfgdir1,pdgdir1,astdir1,globaltxt)
    if funcname in methodtodot and methodtodot[funcname] != "":
        dotfile = methodtodot[funcname]
        astfile = os.path.join(astdir1,str(dotfile)+"-ast.dot")
        (src,dest,calledname) = utils.get_source_dest(int(node.line),astfile,num)
        funcinfo = utils.get_function_information(int(node.line),astfile,num)
        (controls,iscontrol) = utils.get_control_information(int(node.line),astfile,num)
        forinfo = utils.get_for_information(int(node.line),astfile,num)
        returnvalue = utils.get_return(int(node.line),astfile,num)
        for func in funcinfo:
            funcname = func
            funcvars = funcinfo[func]
            for i in range(len(funcvars)):
                if "&amp;" in funcvars[i]:
                    funcvars[i] = funcvars[i][5:]
            funcinfo[func] = funcvars

        init_str, loop_str, change_str = forinfo[0], forinfo[1],forinfo[2]
        if "++" in change_str.strip():
            changevar = change_str[0:-2].strip()
            if changevar in dest:
                dest = list(set(dest))
                dest.remove(changevar)

        orconditionlist = []
        if iscontrol:
            orconditionlist =  utils.get_and_information(int(node.line),astfile,num)
            
        return (src,dest,calledname,funcinfo,controls,iscontrol,1,orconditionlist)
    return ([],[],"",{},[],False,0,[])

def getldata(preds):
    # get ldata
    res = {}
    for pred in preds:
        predid = pred[0]
        predvar = pred[1]
        if predvar not in res:
            res[predvar] = []
        res[predvar].append(predid)
    return res

# LData={"len":[15,16],"name":[17,18],"key":[20]}
def getCombination(LData):
    SDD = []
    keylen = len(LData.keys())
    for key in LData.keys():
        var = key
        indexs = LData[key])
        if(len(indexs) == 1):
            if SDD == []:
                didi = {}
                didi[key] = indexs[0]
                SDD.append(didi)
            else:
                for didi in SDD:
                    didi[key] = LData[key][0]
        else:
            SDDtemp = SDD
            SDDres = []
            SDD = []
            if SDDtemp == []:
                for i in range(len(indexs)):
                    temp = {}
                    temp[key] = LData[key][i]
                    SDD.append(temp)
            else:
                for i in range(len(indexs)):
                    for didi in SDDtemp:
                        temp = {}
                        temp = copy.deepcopy(didi)
                        temp[key] = LData[key][i]
                        SDDres.append(temp)
                SDD = SDDres

    return SDD

def getoptionname(preds,flowlist):
    res = []
    ldata = getldata(preds)
    sdd = getCombination(ldata)
    # LData=[{"len":15,"key":16},{"len":25,"key":16}]
    for ldd in sdd:
        temp = []
        for pred in ldd:
            varname = pred
            predid = ldd[pred]
            temp = unionog(temp,flowlist[predid].optionlist)
        res.extend(temp)

    newog = []
    for op in res:
        if op == []:
            continue
        op = list(set(op))
        op.sort()
        if op not in newog:
            newog.append(op)
    return newog

def slimog(og):
    newog = []
    newop = []
    tempog = []
    for op in og:
        if isinstance(op,str):
            newop.append(op)
        else:
            tempog.append(op)
    if len(newop) > 0:
        tempog.append(newop)
            

    for op in tempog:
        if op == []:
            continue

        op = list(set(op))
        op.sort()
        # op.sort()
        if op not in newog:
            newog.append(op)
    return newog



def optimizeog(ogs):
    size = 0
    if len(ogs) > 1:
        if isinstance(ogs[0],list):
            size = len(ogs)
        elif isinstance(ogs[0],str):
            size = 1
    templist = []
    result = []
    
    if (size) > 5:
        for _ele in ogs:
            _temp = list(set(_ele))
            if _temp not in templist:
                templist.append(_temp)
                result.append(_temp)
        for i in range(len(templist)):
            og1 = templist[i]
            for j in range(i+1,len(templist)):
                og2 = templist[j]
                # 存在融合的关系
                if set(og1)-set(og2) == set():
                    # og2包含og1
                    if og1 in result and len(result) > 2:
                        result.remove(og1)
                elif set(og2)-set(og1) == set():
                    # og1包含og2
                    if og2 in result and len(result) > 2:
                        result.remove(og2)
                elif len(set(og1)-set(og2)) == 1 and len(set(og2)-set(og1)) == 1:
                    # 双方只有一个选项不一样
                    if og2 in result and len(result) > 2:
                        result.remove(og2)
                
    else:
        return ogs
    return result
                                     
def inbetweenogs(og1,og2):

    for ele in og1:
        if isinstance(ele,str):
            og1 = [og1]

    og1inog2 = 1
    for ele in og1:
        if ele not in og2:
            og1inog2 = 0
            break
    og2inog1 = 1
    for ele in og2:
        if ele not in og1:
            og2inog1 = 0
            break 
    if og1inog2 == 1:
        return 2
    elif og2inog1 == 1:
        return 1
    else:
        return 0      

def appendog(og1,og2):
    res = []
    for og in og1:
        if isinstance(og,list):
            og = list(set(og))
            og.sort()
            if og not in res:
                res.append(og)
        elif isinstance(og,str):
            og = list(set(og1))
            og.sort()
            if og not in res:
                res.append(og)
            break
    for og in og2:
        if isinstance(og,list):
            og = list(set(og))
            og.sort()
            if og not in res:
                res.append(og)
        elif isinstance(og,str):
            og = list(set(og2))
            og.sort()
            if og not in res:
                res.append(og)
            break
    return res

def unionog(og1,og2):

    time1 = time.time()
    og1 = slimog(og1)
    og2 = slimog(og2)
    print("union:",og1,og2)
    res = []
    if(len(og1) == 0 and len(og2) == 0):
        return []
    
    if(og1 == None and og2 != None):
        return og2
    elif og1 != None and og2 == None:
        return og1
    if len(og1) != 0 and len(og2) == 0:
        # print("return   ")
        return og1
    if len(og1) == 0 and len(og2) != 0:
        return og2
    if(og1 == og2 ):
        return og1
    temp1 = og1[0]
    temp2 = og2[0]
    if not isinstance(temp1,list):
        og1 = [og1]
    if not isinstance(temp2,list):
        og2 = [og2]
    for temp1 in og1:
        for temp2 in og2:
            temp3 = [] 
            temp3.extend(temp1)
            temp3.extend(temp2)
            temp3 = list(set(temp3))
            res.append(temp3)

    res = slimog(res)
    print(res)
    time2 = time.time()
    functionwithiiv["timeog"] += time2-time1

    return res

def getCombination(LData):
    SDD = []
    keylen = len(LData.keys())
    for key in LData.keys():
        var = key
        indexs = LData[key]

        if(len(indexs) == 1):
            if SDD == []:
                didi = {}
                didi[key] = indexs[0]
                SDD.append(didi)
            else:
                for didi in SDD:
                    didi[key] = LData[key][0]
        else:
            SDDtemp = SDD
            SDDres = []
            SDD = []
            if SDDtemp == []:
                for i in range(len(indexs)):
                    temp = {}
                    temp[key] = LData[key][i]
              
                    SDD.append(temp)
            else:
                for i in range(len(indexs)):
                    for didi in SDDtemp:
                        temp = {}
                        temp = copy.deepcopy(didi)
                        temp[key] = LData[key][i]
                        SDDres.append(temp))
                SDD = SDDres

    return SDD

def getcdog(node,nodelist):

    cdpreds = controlPreds(node)
    finalog = {}
    newcdpreds = []
    if len(cdpreds) > 1:
        for _cd in cdpreds:
            if _cd in nodelist and nodelist[_cd].type_str != "METHOD":
                newcdpreds.append(_cd)
    if len(newcdpreds) > 0:
        cdpreds = newcdpreds
    
    for cdpred in cdpreds:
        if cdpred in node2og:
            finalog = unionog(finalog,node2og[cdpred])
    finalog = slimog(finalog)
    return finalog

def getddog(predjson,node):
    
    sdd = getCombination(predjson)
    finalog = []
    predog = {}
    for ldd in sdd:
        temp = []
        for var in ldd:
            varog = ldd[var]
            temp = unionog(temp,varog)
        finalog.extend(temp)
    finalog = slimog(finalog)

    finalog = slimog(finalog)
    
    node2og[node] = finalog

    for predvar in predjson:
        predog[predvar] = []
        temp = []
        predogs = predjson[predvar]
        for og in predogs:
            temp = slimog(og)
            predog[predvar].extend(temp)
        predog[predvar] = slimog(predog[predvar])
    return (finalog,predog)

def getogsize(og):
    ret = []
    if og == []:
        return [0]
    for ele in og:
        if isinstance(ele,list):
            ret.append(len(ele))
        elif isinstance(ele,str):
            return [len(og)]


def getog(predjson,node,nodelist):
    cdpreds = controlPreds(node)
    
    sdd = getCombination(predjson)
    timecost = time.time() - timeog["start"]
    
    for var in predjson:
        json1 = predjson[var]
   
    finalog = []
    predog = {}
    for ldd in sdd:
        temp = []
        for var in ldd:
            varog = ldd[var]
            temp = unionog(temp,varog)
        finalog.extend(temp)
    finalog = slimog(finalog)
    
   
    cdog = getcdog(node,nodelist)
    finalog = unionog(finalog,cdog)
    
    node2og[node] = finalog

    for predvar in predjson:
        predog[predvar] = []
        temp = []
        predogs = predjson[predvar]
        for og in predogs:
            temp = slimog(og)
            predog[predvar].extend(temp)
        predog[predvar] = slimog(predog[predvar])

    return (finalog,predog)

def constructflow(funcname,cfg_g,pdg_g,ddrelation,toddrealtion,flowstart,startid,startvar,involvedglobal,frominput,fromglobal,globaloption,flowlist,ddvoptionname,cfgdir1,pdgdir1,astdir1,iiv,globaltxt,structvarjson1,return_structog,return_paramog,functionog,outparamstruct_return,outparamog_alter,entrycdog,iscallfunc):
    global mode2options
    global opmodes
    global programname
    
    return_paramog["has"] = 0
    return_paramog["og"] = []

    (globalvariables,methods) = get_global_info(globaltxt)
    nodelist = pdg_g.node_set

    sortnodelist = []

    nodeline = {}

    (sortnodelist,nodeline) = ddarrangenode(funcname,cfgdir1,ddrelation,pdg_g,globaltxt)

    structvarlist = []
    for structname in structvarjson1:

        for member in structvarjson1[structname]:
            structvarlist.append(structname+"-&gt;"+member)
            structvarlist.append(structname+"."+member)

    hasglobal = 0
    if flowstart != -1:
        flownode = Flow_Node(flowstart)
        flownode.funcname = funcname
        flownode.frominput = frominput
        flownode.fromglobal = fromglobal
        if startvar:
            flownode.vars[startvar] = [ddvoptionname]
        flownode.pdgnode = nodelist[flowstart]
        flownode.line = nodelist[flowstart].line
        flowlist[flowstart] = flownode
        finalflowlist[flowstart] = flownode

    if(sortnodelist.count(startid) > 0):
        startindex = sortnodelist.index(startid)
    else:
        startindex = 0

    for nodeindex in range(startindex,len(sortnodelist)):
        
        node = sortnodelist[nodeindex]

        if nodelist[node].type_str.strip() == "METHOD":
            # if entrycdog != []:
            flownode = Flow_Node(node)
            flownode.funcname = funcname
            flownode.fromglobal = 0
            flownode.frominput = 0
            flownode.pdgnode = nodelist[node]
            flownode.line = nodelist[node].line
            flownode.optionlist = entrycdog
            flownode.controlog = entrycdog
            flowlist[node] = flownode
            if not iscallfunc:
                finalflowlist[node] = flownode
            node2og[node] = flownode.optionlist
            continue
        if nodelist[node].type_str.strip() == "PARAM":
            continue
        # operand:there is use of tainted globals
        (src,dest,calledname,funcinfo,controls,iscontrol,parseok,orconditionlist) = stateOperands(funcname,nodelist[node],astdir1,globaltxt)
        for i in range(len(src)):
            ele = src[i]
            if "(" in ele and ")" in ele:
                ele = ele[ele.find(")")+1:]
            if "*" in ele:
                ele = ele.split("*")[-1]
            src[i] = ele

        dest = list(set(dest))
        if calledname == [] and funcinfo != {}:
            for func in funcinfo:
                calledname.append(func)
        if len(src) == 0 and len(calledname) == 0 and len(controls) == 0:
            continue
        
        isor = 0
       
        isand = 0
        if len(orconditionlist) >= 2:
         
            isor = 1
        if "&&" in nodelist[node].dot_src:
        
            isand = 1

        funcandvars = {}
        if calledname != []:
            if(len(set(calledname)) == 1):
                funcandvars[calledname[0]] = list(set(src))
            else:
                minlen = min(len(calledname), len(src))
                for i in range(minlen):
                    if calledname[i] not in funcandvars:
                        funcandvars[calledname[i]] = []
                    funcandvars[calledname[i]].append(src[i])

        src.extend(controls)
      
        if(iiv == 0):
            for destination in dest:
                if (destination in nodelist[node].dot_src and destination in globalvariables) or ("." in destination and destination.split(".")[0] in globalvariables) or ("-&gt;" in destination and destination.split("-&gt;")[0] in globalvariables):
                    sourcetaint = 0
                    if node in toddrealtion:
                        ddpreds = toddrealtion[node]
                        for pred in ddpreds:
                            predid = pred[0]
                            predvar = pred[1]
                            if predid in flowlist and predvar in flowlist[predid].vars and predvar in src:
                                sourcetaint = 1
      
                    involvedglobal[destination] = sourcetaint
           
                    if node not in flowlist:
                        flownode = Flow_Node(node)
                    else:
                        flownode = flowlist[node]
                    flownode.funcname = funcname
                    flownode.fromglobal = 1
                    flownode.frominput = sourcetaint
                    flownode.pdgnode = nodelist[node]
                    flownode.line = nodelist[node].line
                    if iscontrol:
                        flownode.iscontrol = 1
                    flownode.optionlist = unionog(flownode.optionlist,[ddvoptionname])
                    flownode.vars[destination] = flownode.optionlist
                    globaloption[destination] = flownode.optionlist
                    flowlist[node] = flownode
                    if not iscallfunc:
                        finalflowlist[node] = flownode
                
        
        if nodelist[node].type_str.strip() == "RETURN":
            returnvalue = stateReturns(funcname,nodelist[node],astdir1,globaltxt)

            if returnvalue in structvarjson1:
                return_structog = structvarjson1[returnvalue]
            else:
                return_paramog["has"] = 1
                predjson = {}
                input = 0
                global1 = 0
                fromcontrol = 0
                if node in toddrealtion:
                    ddpreds = toddrealtion[node]
                    hasflownode = 0
                    predtemp = []
                    
                    for pred in ddpreds:
                        predid = pred[0]
                        predvar = pred[1]
                        predvar = predvar.strip()
                        if predvar in nodelist[node].dot_src and predid in flowlist and predvar in flowlist[predid].vars:
                            if predvar not in predjson:
                                predjson[predvar] = []
                            predjson[predvar].append(flowlist[predid].vars[predvar])
                            input = flowlist[predid].frominput
                            global1 = flowlist[predid].fromglobal
                            if flowlist[predid].fromcontrol == 1:
                                fromcontrol = 1
                

                useglobal = 0
                usestruct = 0
                for srcvar in [returnvalue]:
                    srcvar = srcvar.strip()
                 
                    if srcvar in globaloption:
                        if srcvar not in predjson:
                            predjson[srcvar] = []
                        predjson[srcvar].append(globaloption[srcvar])
              
                        input = involvedglobal[srcvar]
                        global1 = 1
                        hasglobal = 1
                        useglobal = 1
            
                    elif srcvar in structvarlist:
                        # ->
                        if "-&gt;" in srcvar:
                            structname = srcvar.split("-&gt;")[0]
                            member = srcvar[srcvar.find("-&gt;")+5:]
                      
                        # .  
                        elif "." in srcvar:
                            structname = srcvar.split(".")[0]
                            member = srcvar[srcvar.find(".")+1:]
                        
                        if srcvar not in predjson:
                            predjson[srcvar] = []
                        if structname in structvarjson1 and member in structvarjson1[structname]:
                            predjson[srcvar].append(structvarjson1[structname][member])
                            usestruct = 1

                (curog,srcog) = getog(predjson,node,nodelist)
                if curog != []:
                    if node not in flowlist:
                        flownode = Flow_Node(node)
                    else:
                        flownode = flowlist[node]
                        curog = unionog(curog,flownode.optionlist)
                    
                    flownode.funcname = funcname
                    flownode.fromglobal = global1
                    flownode.frominput = input
                  
                    for src1 in srcog:
                        flownode.vars[src1] = srcog[src1]           
                    if not srcog:
                        flownode.fromcontrol = 1 
                    else:
                        flownode.fromcontrol = fromcontrol
                    flownode.pdgnode = nodelist[node]
                    flownode.line = nodelist[node].line
                    if iscontrol:
                        flownode.iscontrol = 1
                    flownode.optionlist = curog
                    flownode.controlog = getcdog(node,nodelist)
               
                    flownode.useglobal = useglobal
                    flownode.usestruct = usestruct
                    flowlist[node] = flownode
                    if not iscallfunc:
                        finalflowlist[node] = flownode
                    
                    node2og[node] = flownode.optionlist
                if node in flowlist:
                    return_paramog["og"] = appendog(return_paramog["og"],flowlist[node].optionlist)
                else:
                    return_paramog["og"] = appendog(return_paramog["og"],[])
      

  
        if (len(calledname) < 1 and len(orconditionlist) < 2 and len(dest) < 2) or (len(orconditionlist) < 2 and len(calledname) > 0 and calledname[0] not in nodelist[node].dot_src):
            predjson = {}
            input = 0
            global1 = 0
            fromcontrol = 0
           
            if node in toddrealtion:
                ddpreds = toddrealtion[node]
                hasflownode = 0
                predtemp = []
                
                for pred in ddpreds:
                    predid = pred[0]
                    predvar = pred[1]
                    predvar = predvar.strip()
                    if predvar in nodelist[node].dot_src and predid in flowlist and predvar in flowlist[predid].vars and predvar in src:
                        if predvar not in predjson:
                            predjson[predvar] = []
                        predjson[predvar].append(flowlist[predid].vars[predvar])
                        input = flowlist[predid].frominput
                        global1 = flowlist[predid].fromglobal
                        if flowlist[predid].fromcontrol == 1:
                            fromcontrol = 1

            useglobal = 0
            usestruct = 0
            
            for srcvar in src:
                srcvar = srcvar.strip()
        
                if srcvar in globaloption:
                    if srcvar not in predjson:
                        predjson[srcvar] = []
                    predjson[srcvar].append(globaloption[srcvar])
             
                    input = involvedglobal[srcvar]
                    global1 = 1
                    hasglobal = 1
                    useglobal = 1
    
                elif srcvar in structvarlist:
                    # ->
                    if "-&gt;" in srcvar:
                        structname = srcvar.split("-&gt;")[0]
                        member = srcvar[srcvar.find("-&gt;")+5:]
                   
                    # .  
                    elif "." in srcvar:
                        structname = srcvar.split(".")[0]
                        member = srcvar[srcvar.find(".")+1:]
                    
                    if srcvar not in predjson:
                        predjson[srcvar] = []
                    if structname in structvarjson1 and member in structvarjson1[structname]:
                        predjson[srcvar].append(structvarjson1[structname][member])
                        usestruct = 1
           
            (curog,srcog) = getog(predjson,node,nodelist)
            if curog != []:
   
                if node not in flowlist:
                    flownode = Flow_Node(node)
                else:
                    flownode = flowlist[node]
                    curog = unionog(curog,flownode.optionlist)
                
                flownode.funcname = funcname
                flownode.fromglobal = global1
                flownode.frominput = input
                for src1 in srcog:
                    flownode.vars[src1] = srcog[src1]
                if len(set(dest)) == 1:
                    destvar = dest[0]
                    flownode.vars[destvar] = curog
                    hasstructmem = 0
                    if "-&gt;" in destvar:
                        structname = destvar.split("-&gt;")[0]
                        member = destvar[destvar.find("-&gt;")+5:]
                    elif "." in destvar:
                        structname = destvar.split(".")[0]
                        member = destvar[destvar.find(".")+1:]
                        hasstructmem = 1
                    if hasstructmem == 1:
                        if structname not in structvarjson1:
                            structvarjson1[structname] = {}
                        structvarjson1[structname][member] = curog
                        structvarlist.append(destvar)
                        structvarlist = list(set(structvarlist))
                        if structname in globalvariables:
                            involvedglobal[destvar] = input
                            globaloption[destvar] = curog
                            
                if not srcog:
                    flownode.fromcontrol = 1 
                else:
                    flownode.fromcontrol = fromcontrol
                flownode.pdgnode = nodelist[node]
                flownode.line = nodelist[node].line
                if iscontrol:
                    flownode.iscontrol = 1
                flownode.optionlist = curog
                flownode.controlog = getcdog(node,nodelist)
                flownode.useglobal = useglobal
                flownode.usestruct = usestruct
                flowlist[node] = flownode
                if not iscallfunc:
                    finalflowlist[node] = flownode
                node2og[node] = flownode.optionlist
            if len(set(src)) == 1  and len(set(dest)) == 1:
                if src[0] in structvarjson1:
                    structvarjson1[dest[0]] = {}
                    structvarjson1[dest[0]] = structvarjson1[src[0]]
                    for member in structvarjson1[dest[0]]:
                        structvarlist.append(dest[0]+"-&gt;"+member)
                        structvarlist.append(dest[0]+"."+member)
        elif len(orconditionlist) >= 2 and len(dest) == 0:
            ogtemp = []
            ogall = []
            
            for conditionsrc in orconditionlist:
                predjson = {}
                input = 0
                global1 = 0
                if node in toddrealtion:
                    ddpreds = toddrealtion[node]
                    hasflownode = 0
                    predtemp = []
                    
                    for pred in ddpreds:
                        predid = pred[0]
                        predvar = pred[1]
                        predvar = predvar.strip()
                        if predvar in nodelist[node].dot_src and predid in flowlist and predvar in flowlist[predid].vars and predvar in conditionsrc:
                            if predvar not in predjson:
                                predjson[predvar] = []
                            predjson[predvar].append(flowlist[predid].vars[predvar])
                            input = flowlist[predid].frominput
                            global1 = flowlist[predid].fromglobal
                

                useglobal = 0
                usestruct = 0
                for srcvar in conditionsrc:
                    srcvar = srcvar.strip()
                    if srcvar in globaloption:
                        if srcvar not in predjson:
                            predjson[srcvar] = []
                        predjson[srcvar].append(globaloption[srcvar])
                        input = involvedglobal[srcvar]
                        global1 = 1
                        hasglobal = 1
                        useglobal = 1
                    elif srcvar in structvarlist:
                        # ->
                        if "-&gt;" in srcvar:
                            structname = srcvar.split("-&gt;")[0]
                            member = srcvar[srcvar.find("-&gt;")+5:]
                            
                        elif "." in srcvar:
                            structname = srcvar.split(".")[0]
                            member = srcvar[srcvar.find(".")+1:]
                        if srcvar not in predjson:
                            predjson[srcvar] = []
                        if structname in structvarjson1 and member in structvarjson1[structname]:
                            predjson[srcvar].append(structvarjson1[structname][member])
                            usestruct = 1
                
                (curog,srcog) = getddog(predjson,node)
                if curog != []:
                    ogall.append(curog)
                    
                    if node not in flowlist:
                        flownode = Flow_Node(node)
                    else:
                        flownode = flowlist[node]
                        
                    flownode.funcname = funcname
                    flownode.fromglobal = global1
                    flownode.frominput = input
                    for src1 in srcog:
                        flownode.vars[src1] = srcog[src1]
                        
                    flownode.pdgnode = nodelist[node]
                    flownode.line = nodelist[node].line
                    if iscontrol:
                        flownode.iscontrol = 1
                    if flownode.optionlist == [] and curog:
                        flownode.optionlist = curog
                    elif flownode.optionlist and curog:
                        flownode.optionlist.extend(curog) 
                        flownode.optionlist = slimog(flownode.optionlist)
                    flownode.useglobal = useglobal
                    flownode.usestruct = usestruct
                    flowlist[node] = flownode
                    if not iscallfunc:
                        finalflowlist[node] = flownode

            isogor = 0
            for i in range(len(ogall)):
                for j in range(i+1,len(ogall)):
                    temp1 = ogall[i]
                    temp2 = ogall[j]
                    temp1 = slimog(temp1)
                    temp2 = slimog(temp2)
                    if temp1 != temp2:
                        isogor = 1
                        break
            ogall.append(curog)

            cdog = getcdog(node,nodelist)
            if node in flowlist:
                flowlist[node].controlog = cdog
                if cdog:
                    flowlist[node].optionlist = unionog(flowlist[node].controlog,flowlist[node].optionlist)
                    flowlist[node].fromcontrol = 1
                    flowlist[node].isopor = isogor
                node2og[node] = flowlist[node].optionlist
            elif cdog:
            
                flownode = Flow_Node(node)
                flownode.funcname = funcname
                flownode.fromglobal = global1
                flownode.frominput = input
                flownode.pdgnode = nodelist[node]
                flownode.line = nodelist[node].line
                flownode.controlog = cdog
                flownode.fromcontrol = 1

                if iscontrol:
                    flownode.iscontrol = 1
                flownode.optionlist = slimog(cdog)
                flowlist[node] = flownode
                if not iscallfunc:
                    finalflowlist[node] = flownode
                node2og[node] = flownode.optionlist

        
        # function call
        if len(calledname) >= 1:
            if "do_cli" in calledname:
                continue
            returnstruct = {}
            returnparam = {}
            returnparam["has"] = 0
            returnparam["og"] = []
            input = 0
            global1 = 0
            structasparameter = ""
            fromcontrol = 0
            usestruct = 0
            useglobal = 0

            predjson = {}
            if node in toddrealtion:
                ddpreds = toddrealtion[node]
          
                hasflownode = 0
                predtemp = []
                for pred in ddpreds:
                    predid = pred[0]
                    predvar = pred[1]
                    predvar = predvar.strip()
                    if predvar in nodelist[node].dot_src and predid in flowlist and flowlist[predid].vars != {} and predvar in src and predvar in flowlist[predid].vars:
                        if predvar not in predjson:
                            predjson[predvar] = []
                        predjson[predvar].append(flowlist[predid].vars[predvar])
                        # predjson[predvar] = list(set(predjson[predvar]))
                        input = flowlist[predid].frominput
                        global1 = flowlist[predid].fromglobal
                        if flowlist[predid].fromcontrol == 1:
                            fromcontrol = 1
 
            
            for srcvar in src:
                srcvar = srcvar.strip()
            
                if srcvar in globaloption:
                    if srcvar not in predjson:
                        predjson[srcvar] = []
                    predjson[srcvar].append(globaloption[srcvar])
                    # predjson[srcvar] = list(set(predjson[srcvar]))
                    input = involvedglobal[srcvar]
                    global1 = 1
                    hasglobal = 1
                    useglobal = 1 
       
                elif srcvar in structvarlist:
                    if "-&gt;" in srcvar:
                        structname = srcvar.split("-&gt;")[0]
                        member = srcvar[srcvar.find("-&gt;")+5:]
                        # member = srcvar.split("-&gt;")[1]
                        
                    elif "." in srcvar:
                        structname = srcvar.split(".")[0]
                        member = srcvar[srcvar.find(".")+1:]
                        # member = srcvar.split(".")[1]
                    if srcvar not in predjson:
                        predjson[srcvar] = []
                    if structname in structvarjson1 and member in structvarjson1[structname]:
                        predjson[srcvar].append(structvarjson1[structname][member])
                        usestruct = 1
                elif srcvar in structvarjson1:
    
                    structasparameter = srcvar
                    usestruct = 1

            (curog,srcog) = getog(predjson,node,nodelist)
            if curog != []:
                if node not in flowlist:
                    flownode = Flow_Node(node)
                else:
                    flownode = flowlist[node]
                    curog = unionog(curog,flownode.optionlist)
                flownode.funcname = funcname
                flownode.fromglobal = global1
                flownode.frominput = input
                for src1 in srcog:
                    flownode.vars[src1] = srcog[src1]
                if srcog and len(srcog) >= 1:
                    if calledname[0] not in methods:
                        flownode.paramiiv = 1
                    else:
                        flownode.paramiiv = 2
                        
                if len(set(dest)) == 1:
                    destvar = dest[0]
                    flownode.vars[dest[0]] = curog
                    hasstructmem = 0
                    if "-&gt;" in destvar:
                        structname = destvar.split("-&gt;")[0]
                        member = destvar[destvar.find("-&gt;")+5:]
                        # member = dest[0].split("-&gt;")[1]
                        hasstructmem = 1
                    elif "." in destvar:
                        structname = destvar.split(".")[0]
                        member = destvar[destvar.find(".")+1:]
                        # member = dest[0].split(".")[1]
                        hasstructmem = 1
                    if hasstructmem == 1:
                        if structname not in structvarjson1:
                            structvarjson1[structname] = {}
                        structvarjson1[structname][member] = curog
                        structvarlist.append(destvar)
                        structvarlist = list(set(structvarlist))
                
                        if structname in globalvariables:
                            involvedglobal[destvar] = input
                            globaloption[destvar] = curog
                flownode.pdgnode = nodelist[node]
                flownode.line = nodelist[node].line
                # flownode.optionlist.extend(flowlist[predid].optionlist)
                if not srcog:
                    flownode.fromcontrol = 1
                else:
                    flownode.fromcontrol = fromcontrol
                hasflownode = 1
                if iscontrol:
                    flownode.iscontrol = 1
                flownode.calledname = calledname[0]
                flownode.optionlist = curog
                flownode.controlog = getcdog(node,nodelist)
                flownode.useglobal = useglobal
                flownode.usestruct = usestruct
                # unionog(flownode.controlog,getcdog(node,nodelist))
                flowlist[node] = flownode
                if not iscallfunc:
                    finalflowlist[node] = flownode
                node2og[node] = flownode.optionlist
        
            for func in funcinfo:
                # libc
                if func not in methods:
                    if func in ["sprintf","snprintf"]:
                        srctemp = funcinfo[func]
                        variables = funcandvars[func]
                        if srctemp[0] in variables:
                            variables.remove(srctemp[0])
                        else:
                            continue
                        hasflownode = 0
                        predtemp = []
                        predjson = {}
                        input = 0
                        global1 = 0
                        fromcontrol = 0
                        if node in toddrealtion:
                            ddpreds = toddrealtion[node]
                            for pred in ddpreds:
                                predid = pred[0]
                                predvar = pred[1]
                                predvar = predvar.strip()
                                if predvar in nodelist[node].dot_src and predid in flowlist and predvar in flowlist[predid].vars and predvar in variables:
                                    if predvar not in predjson:
                                        predjson[predvar] = []
                                    predjson[predvar].append(flowlist[predid].vars[predvar])
                                    # predjson[predvar] = list(set(predjson[predvar]))
                                    input = flowlist[predid].frominput
                                    global1 = flowlist[predid].fromglobal
                                    if flowlist[predid].fromcontrol == 1:
                                        fromcontrol = 1
                        usestruct = 0
                        useglobal = 0
                        for srcvar in variables:
                            srcvar = srcvar.strip()
                   
                            if srcvar in globaloption:
                                if srcvar not in predjson:
                                    predjson[srcvar] = []
                                predjson[srcvar].append(globaloption[srcvar])
                                # predjson[srcvar] = list(set(predjson[srcvar]))
                                input = involvedglobal[srcvar]
                                global1 = 1
                                hasglobal = 1
                                useglobal = 1
                      
                            elif srcvar in structvarlist:
                                if "-&gt;" in srcvar:
                                    structname = srcvar.split("-&gt;")[0]
                                    member = srcvar[srcvar.find("-&gt;")+5:]
                                    # member = srcvar.split("-&gt;")[1]
                                elif "." in srcvar:
                                    structname = srcvar.split(".")[0]
                                    member = srcvar[srcvar.find(".")+1:]
                                    # member = srcvar.split(".")[1]
                                if srcvar not in predjson:
                                    predjson[srcvar] = []
                                if structname in structvarjson1 and member in structvarjson1[structname]:
                                    predjson[srcvar].append(structvarjson1[structname][member])
                                    usestruct = 1
                            elif srcvar in structvarjson1:
                                structasparameter = srcvar
                                usestruct = 1
                  
                        (curog,srcog) = getog(predjson,node,nodelist)
                        if curog != []:
   
                            if node not in flowlist:
                                flownode = Flow_Node(node)
                            else:
                                flownode = flowlist[node]
                                # curog = unionog(curog,flownode.optionlist)
                            flownode.funcname = funcname
                            flownode.fromglobal = global1
                            flownode.frominput = input
                            for src in srcog:
                                flownode.vars[src] = srcog[src]
                        
                            flownode.vars[srctemp[0]] = curog
                      
                            if srctemp[0] in globalvariables:
                                involvedglobal[srctemp[0]] = 1
                                globaloption[srctemp[0]] = curog
                            if not srcog:
                                flownode.fromcontrol = 1
                            else:
                                flownode.fromcontrol = fromcontrol
                       
                            srr = srctemp[0]
                            hasstructmem = 0
                            if "-&gt;" in srr:
                                structname = srr.split("-&gt;")[0]
                                member = srr[srr.find("-&gt;")+5:]
                                # member = dest[0].split("-&gt;")[1]
                                hasstructmem = 1
                            elif "." in srr:
                                structname = srr.split(".")[0]
                                member = srr[srr.find(".")+1:]
                                # member = dest[0].split(".")[1]
                                hasstructmem = 1
                            if hasstructmem == 1:
                                if structname not in structvarjson1:
                                    structvarjson1[structname] = {}
                                structvarjson1[structname][member] = curog
                                structvarlist.append(srr)
                                structvarlist = list(set(structvarlist))
                                if structname in globalvariables:
                                    involvedglobal[srr] = input
                                    globaloption[srr] = curog
                            flownode.pdgnode = nodelist[node]
                            flownode.line = nodelist[node].line
                            if iscontrol:
                                flownode.iscontrol = 1
                            flownode.calledname = func
                            flownode.optionlist = curog
                            flownode.controlog = getcdog(node,nodelist)
                            # unionog(flownode.controlog,getcdog(node,nodelist))
                            # hasflownode = 1
                            flownode.useglobal = useglobal
                            flownode.usestruct = usestruct
                            flowlist[node] = flownode
                            if not iscallfunc:
                                finalflowlist[node] = flownode
                            node2og[node] = flownode.optionlist
                            
                    elif func in ["strncat","strcat"]:
                        srctemp = funcinfo[func]
                        variables = funcandvars[func]
                        
                        # if srctemp[0] in variables:
                        src1 = srctemp[1]
                        to = srctemp[0]
                        if(src1 in variables and to in variables):
                            hasflownode = 0
                            predtemp = []
                            predjson = {}
                            input = 0
                            global1 = 0
                            fromcontrol = 0
                            if node in toddrealtion:
                                ddpreds = toddrealtion[node]
                                for pred in ddpreds:
                                    predid = pred[0]
                                    predvar = pred[1]
                                    predvar = predvar.strip()
                                    if (predvar in nodelist[node].dot_src and  predid in flowlist and predvar in flowlist[predid].vars and predvar == src1):
                                        if predvar not in predjson:
                                            predjson[predvar] = []
                                        predjson[predvar].append(flowlist[predid].vars[predvar])
                                        # predjson[predvar] = list(set(predjson[predvar]))
                                        input = flowlist[predid].frominput
                                        global1 = flowlist[predid].fromglobal
                                        if flowlist[predid].fromcontrol == 1:
                                            fromcontrol = 1
                            usestruct = 0
                            useglobal = 0
                        
                            if src1.strip() in globaloption:
                                src1 = src1.strip()
                                if src1 not in predjson:
                                    predjson[src1] = []
                                predjson[src1].append(globaloption[src1])
                                # predjson[src1] = list(set(predjson[src1]))
                                input = involvedglobal[src1]
                                global1 = 1
                                hasglobal = 1
                                useglobal = 1
                     
                            elif src1.strip() in structvarlist:
                                srcvar = src1.strip()
                                if "-&gt;" in srcvar:
                                    structname = srcvar.split("-&gt;")[0]
                                    member = srcvar[srcvar.find("-&gt;")+5:]
                                    # member = srcvar.split("-&gt;")[1]
                                elif "." in srcvar:
                                    structname = srcvar.split(".")[0]
                                    member = srcvar[srcvar.find(".")+1:]
                                    # member = srcvar.split(".")[1]
                                if srcvar not in predjson:
                                    predjson[srcvar] = []
                                if structname in structvarjson1 and member in structvarjson1[structname]:
                                    predjson[srcvar].append(structvarjson1[structname][member])
                                    usestruct = 1
                            elif src1.strip() in structvarjson1:
                                structasparameter = src1.strip()
                                usestruct = 1
                                
                  
                            (curog,srcog) = getog(predjson,node,nodelist)
                            if curog != []:
                                if node not in flowlist:
                                    flownode = Flow_Node(node)
                                else:
                                    flownode = flowlist[node]
                                    # curog = unionog(curog,flownode.optionlist)
                                flownode.funcname = funcname
                                flownode.fromglobal = global1
                                flownode.frominput = input
                                for src1 in srcog:
                                    flownode.vars[src1] = srcog[src1]
                                flownode.vars[to] = curog
                           
                                if to in globalvariables:
                                    involvedglobal[to] = 1
                                    globaloption[to] = curog
                         
                                srr = to
                                hasstructmem = 0
                                if "-&gt;" in srr:
                                    structname = srr.split("-&gt;")[0]
                                    member = srr[srr.find("-&gt;")+5:]
                                    # member = dest[0].split("-&gt;")[1]
                                    hasstructmem = 1
                                elif "." in srr:
                                    structname = srr.split(".")[0]
                                    member = srr[srr.find(".")+1:]
                                    # member = dest[0].split(".")[1]
                                    hasstructmem = 1
                                if hasstructmem == 1:
                                    if structname not in structvarjson1:
                                        structvarjson1[structname] = {}
                                    structvarjson1[structname][member] = curog
                                    structvarlist.append(srr)
                                    structvarlist = list(set(structvarlist))
                                    if structname in globalvariables:
                                        involvedglobal[srr] = input
                                        globaloption[srr] = curog
                                if not srcog:
                                    flownode.fromcontrol = 1
                                else:
                                    flownode.fromcontrol = fromcontrol
                                flownode.pdgnode = nodelist[node]
                                flownode.line = nodelist[node].line
                                if iscontrol:
                                    flownode.iscontrol = 1
                                flownode.calledname = func
                                flownode.optionlist = curog
                                flownode.controlog = getcdog(node,nodelist)
                                # unionog(flownode.controlog,getcdog(node,nodelist))
                                hasflownode = 1 
                                flownode.useglobal = useglobal
                                flownode.usestruct = usestruct
                                flowlist[node] = flownode
                                if not iscallfunc:
                                    finalflowlist[node] = flownode
                                node2og[node] = flownode.optionlist

                else:
                    # defined functions
                    funcvars = funcinfo[func]
                    paramindex = {}
                    callflowno = 0
                    cdog = getcdog(node,nodelist)
                    # no taint related with function parameters
                    if usestruct == 0 and (node not in flowlist or ((len(funcvars) == 1 and funcvars[0].split() == "") or len(funcvars) == 0)) :
                        callflowno = 1
                        
                    # taint related
                    else:
                        for i in range(len(funcvars)):
                            ele = funcvars[i]
                            if "(" in ele and ")" in ele:
                                ele = ele[ele.find(")")+1:]
                            if "*" in ele:
                                ele = ele.split("*")[-1]
                            funcvars[i] = ele

                        hasrelated = 0
                        structindexs = {}
                        structjsons = {}
                        indexdict1 = {} # paramindex with var's og
                        index1 = -1
                        # paramdict = {} #param with e's og
                        for funcvar in funcvars:
                            
                            if node in flowlist and len(flowlist[node].vars) > 0 and funcvar in flowlist[node].vars:
                                hasrelated = 1
                                paramindex = funcvars.index(funcvar)
                                indexdict1[paramindex] = flowlist[node].vars[funcvar]
                                # paramdict[paramindex] = flowlist[node].optionlist
                            elif funcvar != "" and funcvar in structvarjson1:
                                hasrelated = 1
                                structindexs[funcvars.index(funcvar)] = funcvar
                                structjsons[funcvar] = structvarjson1[funcvar]
                        paramdict = indexdict1
                        params= ()
                        if hasrelated == 1:
                            needflow = 1
                            ogindex = 0
                            funcflow = {}
                            params = (paramdict,cdog)
                            if func not in functionwithogs:
                                functionwithogs[func] = []
                                functionwithogs[func].append([])
                                functionwithogs[func][0] = [[],[]]
                                functionwithogs[func][0][0] = [paramdict,cdog]
                                needflow = 1
                                index1 = 0
                            else:
                                for _i in range(len(functionwithogs[func])):
                                    [_params,_cdog] = functionwithogs[func][_i][0]
                                    if [_params,_cdog] == [paramdict,cdog]:
                                        needflow = 0
                                        index1 = _i
                                        break
                                if needflow == 1:
                                    # ogindex = len(functionwithogs[func])
                                    functionwithogs[func].append([[paramdict,cdog],[]])
                                    index1 = len(functionwithogs[func])-1
                                
                                       
                            if needflow == 1:
                                # (outparamlist1,assignnode1) = outparam(func,pdgdir1,astdir1,globaltxt) 
                                # print("outparamlist:",outparamlist1)
                                # if structindex1 in outparamlist1:
                                #     outparamlist1.remove(structindex1)
                                # for param in outparamlist:
                                #     print("param",param,"funcvars:",funcvars,"node ",node)
                                #     flowlist[node].vars[funcvars[param]] = flowlist[node].optionlist
                                # funcflowparam(func,indexdict,involvedglobal,input,global1,globaloption,funcflow,"",cfgdir1,pdgdir1,astdir1,iiv,globaltxt,structindex,structjson,return_structog)
                                # functionwithogs[func][ogindex]["og"] = funcflow
                                
                                funcog = {}
                                funcog["og"] = []
                                outparam_structog = {}
                                outparam_og = {}
                                funcflowlist = {}
                                funcflowparam(func,indexdict1,involvedglobal,input,global1,globaloption,funcflowlist,-1,"","",cfgdir1,pdgdir1,astdir1,iiv,globaltxt,structindexs,structjsons,returnstruct,returnparam,funcog,outparam_structog,outparam_og,cdog,1)
                                for funcnode in funcflowlist:
                                    if funcnode not in finalflowlist:
                                        finalflowlist[funcnode] = funcflowlist[funcnode]
                                    else:
                                        finalflowlist[funcnode].optionlist = appendog(finalflowlist[funcnode].optionlist,funcflowlist[funcnode].optionlist)
                                functionwithogs[func][index1][1] = [outparam_structog,outparam_og,returnstruct,returnparam]
                     
                        if hasrelated == 0:
                            callflowno = 1
                            
                    if callflowno == 1:
                        needflow = 1
                        ogindex = 0
                        funcflow = {}
                        params = [{},cdog]
                        if func not in functionwithogs:
                            # functionwithogs[func] = {}
                            # functionwithogs[func]["paramdict"] = []
                            # functionwithogs[func]["ogdict"] = []
                            # functionwithogs[func]["paramdict"].append(({},cdog))
                            functionwithogs[func] = []
                            functionwithogs[func].append([])
                            functionwithogs[func][0] = [[],[]]
                            functionwithogs[func][0][0] = [{},cdog]
                            index1 = 0
                        else:
                            for _i in range(len(functionwithogs[func])):
                                [_params,_cdog] = functionwithogs[func][_i][0]
                                if [_params,_cdog] == [{},cdog]:
                                    needflow = 0
                                    index1 = _i
                                    break
                            if needflow == 1:
                                # ogindex = len(functionwithogs[func])
                                functionwithogs[func].append([[{},cdog],[]])
                                index1 = len(functionwithogs[func]) -1
                       
                        if needflow == 1:
                            # funcflowno(func,involvedglobal,0,0,globaloption,funcflow,"",cfgdir1,pdgdir1,astdir1,iiv,globaltxt,return_structog)
                            # functionwithogs[func][ogindex]["og"] = funcflow
                            funcog = {}
                            funcog["og"] = []
                            funcflowlist = {}
                            funcflowno(func,involvedglobal,0,0,globaloption,funcflowlist,"",cfgdir1,pdgdir1,astdir1,iiv,globaltxt,returnstruct,returnparam,funcog,cdog,1)
                  
                            for funcnode in funcflowlist:
                                if funcnode not in finalflowlist:
                                    finalflowlist[funcnode] = funcflowlist[funcnode]
                                else:
                                    finalflowlist[funcnode].optionlist = appendog(finalflowlist[funcnode].optionlist,funcflowlist[funcnode].optionlist) 
                            functionwithogs[func][index1][1] = [{},{},returnstruct,returnparam]
                   
                    outparam_structog = {}
                    outparam_og = {}
                    returnstruct = {}
                    returnparam = {}
                    # for _index in range(len(functionwithogs[func]["paramdict"])):
                    #     if params == functionwithogs[func]["paramdict"][_index]:
                            # print(functionwithogs[func]["ogdict"][_index])
                    if len(functionwithogs[func][index1]) > 1 and len(functionwithogs[func][index1][1]) > 3:
                        outparam_structog = functionwithogs[func][index1][1][0]
                        outparam_og = functionwithogs[func][index1][1][1]
                        returnstruct = functionwithogs[func][index1][1][2]
                        returnparam = functionwithogs[func][index1][1][3]
              
                    if outparam_structog != {}:
                        for _index in outparam_structog:
                            if _index < len(funcvars) and _index > -1:
                                _var1 = funcvars[_index]
                                structvarjson1[_var1] = outparam_structog[_index]
                                for member in structvarjson1[_var1]:
                                    structvarlist.append(_var1+"-&gt;"+member)
                                    structvarlist.append(_var1+"."+member)
                            else:
                                print(f"node is {node} outparam in {_index} and funcvars is {funcvars} not match")
                    if outparam_og != {} and node in flowlist:
                        for _index in outparam_og:
                            if _index < len(funcvars):
                                _var1 = funcvars[_index]
                                flowlist[node].vars[_var1] = outparam_og[_index]
                                  
                    if len(returnstruct) > 0:
                        if len(list(set(dest))) == 1:
                            structvarjson1[dest[0]] = returnstruct
                    if returnparam != {} and node in flowlist and returnparam["has"] == 1:
                        # flowlist[node].optionlist = returnparam["og"]
                        flowlist[node].optionlist = unionog(flowlist[node].optionlist,returnparam["og"])
                        if len(dest) > 0:
                            flowlist[node].vars[dest[0]] = flowlist[node].optionlist

    if funcname not in functionwithiiv:
        functionwithiiv[funcname] = {}
    functionwithiiv[funcname]["hasglobal"] = hasglobal
    functionwithiiv[funcname]["structvar"] = len(structvarjson1)

    (outparamlist,assignnode) = outparam(funcname,pdgdir1,astdir1,globaltxt)
    paramlist = getParam(pdg_g)
    for outparamindex in outparamlist:
        outparamid = paramlist[outparamindex]
        paramvar = getparamvariable(outparamid,ddrelation)
        if paramvar in structvarjson1:
            outparamstruct_return[outparamindex] = structvarjson1[paramvar]
        else:
            if assignnode[paramvar] in flowlist:
                outparamog_alter[outparamindex] = flowlist[assignnode[paramvar]].optionlist
    return flowlist

def funcflowparam(funcname,indexdict,involvedglobal,frominput,fromglobal,globaloption,flowlist,divparamindex,divparamvar,ddvoptionname,cfgdir1,pdgdir1,astdir1,iiv,globaltxt,structindex,structjson,return_structog,return_paramog,functionog,outparam_structog,outparam_og,entrycdog,iscallfunc):
    structvarjson = {}
    # restrict functionc call 
    # if funcname in processedfunction:
    #     if processedfunction[funcname] > 0:
    #         return 
    #     else:
    #         processedfunction[funcname] += 1
    # else:
    #     processedfunction[funcname] = 1
       
    processdot(funcname,cfgdir1,pdgdir1,astdir1,globaltxt)
    (globalvariables,methods) = get_global_info(globaltxt)

    cfg_g = ""
    if funcname in methodtograph:
        if funcname not in methods:
            return
        pdg_g = methodtograph[funcname][1]
        (ddrelation,toddrelation) = constructdd(pdg_g)
        paramlist = getParam(pdg_g)
        nodelist = pdg_g.node_set
        if structindex != {}:
            for index in structindex:
                if index < len(paramlist):
                    paramid = paramlist[index]
                    paramvar = getparamvariable(paramid,ddrelation)
                    if paramid != -1 and paramvar != "":
                        structvarjson[paramvar] = structjson[structindex[index]]
        paramid = -1
        paramvar = ""
        for paramnum in indexdict:
            if(len(paramlist) > paramnum):
                paramid = paramlist[paramnum]
            else:
                paramid = -1
            if paramid == -1:
                paramvar = ""
            else:
                paramvar = getparamvariable(paramid,ddrelation)
            if paramvar == "":
                break   
            if paramid != -1 and paramvar != "":
                if paramid in flowlist:
                    flownode = flowlist[paramid]
                else:
                    flownode = Flow_Node(paramid)
                flownode.funcname = funcname
                flownode.frominput = frominput
                flownode.fromglobal = fromglobal
                flownode.pdgnode = nodelist[paramid]
                flownode.line = nodelist[paramid].line
                res = []
                flownode.optionlist = appendog(flownode.optionlist,indexdict[paramnum])
                flownode.vars[paramvar] = flownode.optionlist
                flowlist[paramid] = flownode
                node2og[paramid] = flownode.optionlist
                if not iscallfunc:
                    finalflowlist[paramid] = flowlist[paramid]    

        flowstart = -1
        if ddvoptionname != "" and divparamindex < len(paramlist):
            flowstart = paramlist[divparamindex]
            paramvar = divparamvar
        constructflow(funcname,cfg_g,pdg_g,ddrelation,toddrelation,flowstart,-1,paramvar,involvedglobal,frominput,fromglobal,globaloption,flowlist,ddvoptionname,cfgdir1,pdgdir1,astdir1,iiv,globaltxt,structvarjson,return_structog,return_paramog,functionog,outparam_structog,outparam_og,entrycdog,iscallfunc)


def funcflowno(funcname,involvedglobal,frominput,fromglobal,globaloption,flowlist,ddvoptionname,cfgdir1,pdgdir1,astdir1,iiv,globaltxt,return_structog,return_paramog,functionog,entrycdog,iscallfunc):
    # restrict calls
    # if funcname in processedfunction:
    #     if processedfunction[funcname] > 0:
    #         return 
    #     else:
    #         processedfunction[funcname] += 1
    # else:
    #     processedfunction[funcname] = 1
    
    processdot(funcname,cfgdir1,pdgdir1,astdir1,globaltxt)
    (globalvariables,methods) = get_global_info(globaltxt)
    cfg_g = ""
    if funcname in methodtograph:
        if funcname == "ERREXIT" or funcname not in methods:
            return
        pdg_g = methodtograph[funcname][1]
        if pdg_g == "":
            return
        (ddrelation,toddrelation) = constructdd(pdg_g)
        constructflow(funcname,cfg_g,pdg_g,ddrelation,toddrelation,-1,-1,"",involvedglobal,frominput,fromglobal,globaloption,flowlist,ddvoptionname,cfgdir1,pdgdir1,astdir1,iiv,globaltxt,{},return_structog,return_paramog,functionog,{},{},entrycdog,iscallfunc)
    return   

def getparamvariable(paramid,pdg_dd):
    paramlist = []
    if paramid in pdg_dd:
        ddvars = pdg_dd[paramid]
        for i in ddvars:
            paramlist.append(i[1])
    
    paramset = set(paramlist)
    paramlist = list(paramset)
    if(len(paramlist) == 1):
        return paramlist[0]
    return ""
    
def ddvparam(funcname,paramindex,paramname,optionname,cfgdir1,pdgdir1,astdir1,iiv,globaltxt):
    cfgdir = cfgdir1
    pdgdir = pdgdir1
    astdir = astdir1
    flow = {}
    paramdict = {}
    funcflowparam(funcname,paramdict,{},1,0,{},flow,paramindex,paramname,optionname,cfgdir1,pdgdir1,astdir1,iiv,globaltxt,{},{},{},{},{},{},{},[],0)
    return flow

def ddvno(funcname,optionname,cfgdir1,pdgdir1,astdir1,iiv,globaltxt):
    cfgdir = cfgdir1
    pdgdir = pdgdir1
    astdir = astdir1
    flow = {}
    funcflowno(funcname,{},0,0,{},flow,optionname,cfgdir1,pdgdir1,astdir1,iiv,globaltxt,{},{},{},[],0)
    return flow

def inter_spread(optionnamelist,funcname,paramlist,cfgdir1,pdgdir1,astdir1,divjsonfile,globaltxt):
    timeog["start"] = time.time()
    functionwithiiv["timeog"] = 0
    (globalvariables,methods) = get_global_info(globaltxt)
    flowlist = {}
    hasneed = 0
    global finalflowlist
    finalflowlist = {}
    for optionname in optionnamelist:
        if len(optionname) > 2 and optionname[0] == "'" and optionname[-1] == "'":
            optionname = optionname[1:-1]
        
        for param in paramlist:
            paramname = param[0]
            paramindex = param[1]
            need = param[2]
            if need == 1:
                hasneed = 1
                ddvparam(funcname,paramindex,paramname,optionname,cfgdir1,pdgdir1,astdir1,0,globaltxt)
        if(hasneed) == 0:
            ddvno(funcname,optionname,cfgdir1,pdgdir1,astdir1,0,globaltxt) 
        for i in finalflowlist:
            flowlist[i] = finalflowlist[i]
    resflow = {}
    
    for node in flowlist:
        resflow[node] = {}
        resflow[node]["funcname"] = flowlist[node].funcname
        resflow[node]["nodeid"] = node
        resflow[node]["frominput"] = flowlist[node].frominput
        resflow[node]["fromglobal"] = flowlist[node].fromglobal
        resflow[node]["line"] = flowlist[node].line
        resflow[node]["vars"] = flowlist[node].vars
        resflow[node]["iscontrol"] = flowlist[node].iscontrol
        resflow[node]["calledname"] = flowlist[node].calledname
        resflow[node]["isor"] = flowlist[node].isor
        resflow[node]["isand"] = flowlist[node].isand
        resflow[node]["paramiiv"] = flowlist[node].paramiiv
        resflow[node]["controlog"] = flowlist[node].controlog
        resflow[node]["fromcontrol"] = flowlist[node].fromcontrol

    with open(divjsonfile, "r") as f:
        content = json.load(f)
    with open(divjsonfile, "w") as f:
        for option in optionnamelist:
            if option not in content:
                content[option] = {}
            for node in resflow:
                content[option][node] = resflow[node]
        f.write(json.dumps(content, indent=4))
    
    print("inter_flow spread over")   
    return resflow

def div_propagation(divjsonfile,divwkljsonfile,envdivjsonfile,iivjsonfile,cfgdir1,pdgdir1,astdir1,globaltxt,anotherline,startfunc,structreturnname,optimize,structvars):

    timeog["start"] = time.time()
    globaloption = {}
    flowlist = {}
    structvarjsons = {}
    parse_divflow(divwkljsonfile,flowlist,globaltxt,involvedglobal,globaloption)
    # precess div pass.json
    (parse_func,endline,structvarjsons) = parse_div(divjsonfile,involvedglobal,globaloption,flowlist,cfgdir1,pdgdir1,astdir1,globaltxt,structvarjsons)

    for node in flowlist:
        finalflowlist[node] = flowlist[node]
        if isinstance(flowlist[node].optionlist[0],str):
            finalflowlist[node].optionlist = [flowlist[node].optionlist]
        node2og[node] = finalflowlist[node].optionlist

    processdot(parse_func,cfgdir1,pdgdir1,astdir1,globaltxt)

    cfg_g = ""
    if parse_func not in methodtograph:
        print(f"{parse_func} cannot find in pdg")
        return
    pdg_g = methodtograph[parse_func][1]
    nodelist = pdg_g.node_set
    (ddrelation,toddrelation) = constructdd(pdg_g)
    startid = -1
    for node in nodelist:
        if int(nodelist[node].line) == int(endline):
            startid = node
            break
    # returnstructjson = {}
    constructflow(parse_func,cfg_g,pdg_g,ddrelation,toddrelation,-1,startid,"",involvedglobal,0,0,globaloption,flowlist,"",cfgdir1,pdgdir1,astdir1,1,globaltxt,structvarjsons,{},{},{},{},{},[],0)
    
    structvarjsons1 = {}
    if structvars != [] and len(structvarjsons) > 0:
        for _name in structvarjsons:
            if _name in structvars[1]:
                _index = structvars[1].index(_name)
                structvarjsons1[structvars[0][_index]] = structvarjsons[_name]          
        if structreturnname != "" and len(structvarjsons1) == 0:
            for _name in structvarjsons:
                structvarjsons1[structreturnname] = structvarjsons[_name]
    else:
        if structreturnname != "" and len(structvarjsons1) == 0:
            for _name in structvarjsons:
                structvarjsons1[structreturnname] = structvarjsons[_name]
    

    if int(anotherline) != -1:
        processdot(startfunc,cfgdir1,pdgdir1,astdir1,globaltxt)
        cfg_g = ""
        if startfunc not in methodtograph:
            print(f"{startfunc} cannot find in pdg")
            return 
        pdg_g = methodtograph[startfunc][1]
        nodelist = pdg_g.node_set
        (ddrelation,toddrelation) = constructdd(pdg_g)
        startid = -1
        for node in nodelist:
            if int(nodelist[node].line) == int(anotherline):
                startid = node
                break
        constructflow(startfunc,cfg_g,pdg_g,ddrelation,toddrelation,-1,startid,"",involvedglobal,0,0,globaloption,flowlist,"",cfgdir1,pdgdir1,astdir1,1,globaltxt,structvarjsons1,{},{},{},{},{},[],0)

    resflow = {}
    for node in finalflowlist:
        resflow[node] = {}
        resflow[node]["funcname"] = finalflowlist[node].funcname
        resflow[node]["nodeid"] = node
        resflow[node]["frominput"] = finalflowlist[node].frominput
        resflow[node]["fromglobal"] = finalflowlist[node].fromglobal
        resflow[node]["line"] = finalflowlist[node].line
        resflow[node]["vars"] = finalflowlist[node].vars
        resflow[node]["iscontrol"] = finalflowlist[node].iscontrol
        resflow[node]["isor"] = finalflowlist[node].isor
        resflow[node]["isand"] = finalflowlist[node].isand
        resflow[node]["isoptionor"] = finalflowlist[node].isopor
        resflow[node]["useglobal"] = finalflowlist[node].useglobal
        resflow[node]["usestruct"] = finalflowlist[node].usestruct
        
        resflow[node]["fromcontrol"] = finalflowlist[node].fromcontrol
        resflow[node]["paramiiv"] = finalflowlist[node].paramiiv
        resflow[node]["calledname"] = finalflowlist[node].calledname
        # resflow[node]["optionname"] =[]
        resflow[node]["controlog"] = finalflowlist[node].controlog
        resflow[node]["optionname"]= (finalflowlist[node].optionlist)

    res = {}
    with open(divwkljsonfile, "r") as f:
        content = json.load(f)  
    for option in content:
        if option not in resflow:
            res[option] = {}
        res[option]["ddv"] = content[option] 
    res["iivariable"] = {}
    for node in resflow:
        res["iivariable"][node] = resflow[node]
    res["function"] = {}
    for func in functionwithiiv:
        if func == "timeog":
            res["timeog"] = functionwithiiv["timeog"]
            continue
        res["function"][func] = {}
        res["function"][func]["hasglobal"] = functionwithiiv[func]["hasglobal"]
        res["function"][func]["structvar"] = functionwithiiv[func]["structvar"]
        
    res["useglobal"] = {}
    res["useglobal"]["number"] = len(globaloption)
    for global1 in globaloption:
        res["useglobal"][global1] = globaloption[global1]   
    with open(iivjsonfile, "w") as f:
        f.write(json.dumps(res, indent=4))

def parse_div(divjsonfile,involvedglobal,globaloption,flowlist,cfgdir1,pdgdir1,astdir1,globaltxt,structvarjsons):
    with open(divjsonfile,"r") as f:
        content = json.load(f)
    parse_func = ""
    endline = 0
    frominput = 0
    fromglobal = 0
    if "parse_func" in content:
        parse_func = content["parse_func"]
    if "end_line" in content:
        endline = content["end_line"]
    functionwithiiv["timeog"] = 0
    optionflow = {}
    structvarjsons = {}
    if parse_func != "" and endline != 0:
        globals = {}
        locals = {}
        for option in content:
            if option in ["end_line","parse_func"]:
                continue
            optionname = option
            if(len(option) > 1  and option[0] == "'"):
                optionname = option[1:-1]
            optionflow[optionname] = {}
            divs = content[option]
            for div in divs:
                funcname = div[0]
                varname = div[1]
                isglobal = div[2]
                varline = div[3]
                frominput = div[4]
                if len(div) > 5:
                    fromglobal = div[5]
                else:
                    fromglobal = 0
                if isglobal:
                    if varname not in globals:
                        globals[varname] = {}
                        globals[varname]["optionname"] = []
                    globals[varname]["optionname"].append(optionname)
                    globals[varname]["frominput"] = frominput
                    globals[varname]["fromglobal"] = fromglobal
                    globals[varname]["optionname"] = list(set(globals[varname]["optionname"]))
                else:
                    if varname == "i" or varname == "j":
                        continue
                    if varname not in locals:
                        locals[varname] = {}
                        locals[varname]["lines"] = []
                        locals[varname]["optionname"] = []
                        locals[varname]["funcname"] = ""
                    locals[varname]["lines"].append(varline)
                    locals[varname]["optionname"].append(optionname)
                    locals[varname]["optionname"] = list(set(locals[varname]["optionname"]))
                    locals[varname]["frominput"] = frominput
                    locals[varname]["fromglobal"] = fromglobal
                    locals[varname]["funcname"] = funcname

        parseoptimizeddv(parse_func,locals,globals,involvedglobal,globaloption,flowlist,cfgdir1,pdgdir1,astdir1,globaltxt,structvarjsons)
        
    return (parse_func, endline, structvarjsons)

def parseddv(optionname,parse_func,endline,varname,isglobal,varline,frominput,fromglobal,involvedglobal,globaloption,flowlist,cfgdir1,pdgdir1,astdir1,globaltxt,structvarjsons):
    givenvarid = -1
    processdot(parse_func,cfgdir1,pdgdir1,astdir1,globaltxt)
    cfg_g = ""
    if parse_func not in methodtograph:
        print(f"{parse_func} not in pdg")
        return
    pdg_g = methodtograph[parse_func][1]
    nodelist = pdg_g.node_set
    (ddrelation,toddrelation) = constructdd(pdg_g)
    if isglobal == 1:
        involvedglobal[varname] = frominput
        if varname not in globaloption:
            globaloption[varname] = [[]]
        globaloption[varname][0].append(optionname)
        globaloption[varname][0] = list(set(globaloption[varname][0]))
        # globaloption[varname][0] = list(set(globaloption[varname][0]))
    elif "-&gt;" in varname:
        structname = varname.split("-&gt;")[0]
        # member = varname.split("-&gt;")[1]
        member = varname[len(structname)+len("-&gt;"):]
        if structname not in structvarjsons:
            structvarjsons[structname] = {}
        structvarjsons[structname][member] = [optionname]
    elif "." in varname:
        structname = varname.split(".")[0]
        # member = varname.split(".")[1]
        member = varname[len(structname)+1:]
        if structname not in structvarjsons:
            structvarjsons[structname] = {}
        structvarjsons[structname][member] = [optionname]
    else:
        for node in ddrelation:
            vars = ddrelation[node]
            for var in vars:
                varid = var[0]
                name = var[1]
                if int(nodelist[node].line) == varline and name == varname and int(nodelist[varid].line) != varline:
                    givenvarid = node
                    if node not in flowlist:
                        flowone = Flow_Node(node)
                    else:
                        flowone = flowlist[node]
                    flowone.funcname = parse_func
                    flowone.fromglobal = fromglobal
                    flowone.frominput = frominput
                    # flowone.vars.append(varname)
                    flowone.pdgnode = nodelist[node]
                    flowone.line = varline
                    flowone.optionlist.append(optionname)
                    flowone.optionlist = list(set(flowone.optionlist))
                    flowone.vars[varname] = flowone.optionlist
                    flowlist[node] = flowone
                    finalflowlist[node] = flowone
                    break
            if givenvarid != -1:
                break
    return

def parseoptimizeddv(parse_func,locals,globals,involvedglobal,globaloption,flowlist,cfgdir1,pdgdir1,astdir1,globaltxt,structvarjsons):
    givenvarid = -1
    processdot(parse_func,cfgdir1,pdgdir1,astdir1,globaltxt)
    if parse_func not in methodtograph:
        print(f"{parse_func} not in pdg")
        return
    pdg_g = methodtograph[parse_func][1]
    nodelist = pdg_g.node_set
    (ddrelation,toddrelation) = constructdd(pdg_g)

    for gv in globals:
        involvedglobal[gv] = globals[gv]["frominput"]
        globaloption[gv] = [list(set(globals[gv]["optionname"]))]
    for lv in locals:
        if "-&gt;" in lv:
            structname = lv.split("-&gt;")[0]
            member = lv[len(structname)+len("-&gt;"):]
            # member = lv.split("-&gt;")[1]
            if structname not in structvarjsons:
                structvarjsons[structname] = {}
            structvarjsons[structname][member] = locals[lv]["optionname"]
        elif "." in lv:
            structname = lv.split(".")[0]
            member = lv[len(structname)+1:]
            # member = lv.split(".")[1]
            if structname not in structvarjsons:
                structvarjsons[structname] = {}
            structvarjsons[structname][member] = locals[lv]["optionname"]
        else:
            processdot(locals[lv]["funcname"],cfgdir1,pdgdir1,astdir1,globaltxt)
            if locals[lv]["funcname"] not in methodtograph:
                print(locals[lv]["funcname"],"not in pdg")
                return
            pdg_g1 = methodtograph[locals[lv]["funcname"]][1]
            nodelist1 = pdg_g1.node_set
            (ddrelation,toddrelation) = constructdd(pdg_g1)
            for line in locals[lv]["lines"]:
                for node in ddrelation:
                    vars = ddrelation[node]
                    for var in vars:
                        varid = var[0]
                        name = var[1]
                        if int(nodelist1[node].line) == line and name == lv and int(nodelist1[varid].line) != line:
                            givenvarid = node
                            if node not in flowlist:
                                flowone = Flow_Node(node)
                            else:
                                flowone = flowlist[node]
                            flowone.funcname = locals[lv]["funcname"]
                            flowone.fromglobal = locals[lv]["fromglobal"]
                            flowone.frominput = locals[lv]["frominput"]
                            flowone.line = line
                            flowone.optionlist = list(set(locals[lv]["optionname"]))
                            flowone.vars[lv] = flowone.optionlist
                            flowlist[node] = flowone
                            finalflowlist[node] = flowone
                            break
                    if givenvarid != -1:
                        givenvarid = -1
                        break

def parse_divflow(divwkljsonfile,flowlist,globaltxt,involvedglobal,globaloption):
    (globalvariables,methods) = get_global_info(globaltxt)
    with open(divwkljsonfile, "r") as f:
        content = json.load(f)  
    for option in content:
        ddvs = content[option]
        # ddvs = divs["ddv"]
        opname = option
        if len(opname) > 2 and opname[0] == "'" and opname[-1] == "'":
            opname = opname[1:-1]
        for ddv in ddvs:
            nodeid = int(ddv)
            if nodeid not in flowlist:
                flowone = Flow_Node(nodeid)
                flowone.optionlist = [opname]
            else:
                flowone = flowlist[nodeid]
                flowone.optionlist = unionog([opname],flowone.optionlist)
            flowone.funcname = ddvs[ddv]["funcname"]
            flowone.nodeid = nodeid
            flowone.frominput = ddvs[ddv]["frominput"]
            flowone.fromglobal = ddvs[ddv]["fromglobal"]
            flowone.line = ddvs[ddv]["line"]
            vars = ddvs[ddv]["vars"]
            for var in vars:
                flowone.vars[var] = [[opname]]
                if var in globalvariables or (("." in var and var.split(".")[0] in globalvariables) or ("-&gt;" in var and var.split("-&gt;")[0] in globalvariables)):
                    if var not in globaloption:
                        globaloption[var] = [[]]
                    globaloption[var][0].append(opname)
                    globaloption[var][0] = list(set(globaloption[var][0]))
                    involvedglobal[var] = flowone.frominput
            flowone.iscontrol = ddvs[ddv]["iscontrol"]
            flowone.isor = ddvs[ddv]["isor"]
            flowone.isand = ddvs[ddv]["isand"]
            flowone.fromcontrol = ddvs[ddv]["fromcontrol"]
            flowone.paramiiv = ddvs[ddv]["paramiiv"]
            flowone.calledname = ddvs[ddv]["calledname"]
            flowone.controlog = ddvs[ddv]["controlog"]
            flowlist[nodeid] = flowone
                    
def get_global_info(globaltxt):
    if "globalvariables" not in globalinfo:
        globalinfo["globalvariables"] = []
    if "methods" not in globalinfo:
        globalinfo["methods"] = []   
    if globalinfo["globalvariables"] == [] and globalinfo["methods"] == []:
        globalvariables,methods =utils.get_global(globaltxt)
        globalinfo["globalvariables"] = globalvariables
        globalinfo["methods"] = methods
    else:
        globalvariables = globalinfo["globalvariables"]
        methods = globalinfo["methods"]
    return (globalvariables, methods)
        
def parse_env_div(envdivjsonfile,globaltxt,involvedglobal,globaloption,flowlist,cfgdir1,pdgdir1,astdir1):
    (globalvariables,methods) = get_global_info(globaltxt)
    with open(envdivjsonfile,"r") as f:
        content = json.load(f)

    for env in content:
        uselist = content[env]
        for usenode in uselist:
            line = usenode["line"]
            func = usenode["func"]
            dot_id = usenode["dot_id"]
            if func == "&lt;global&gt;" or func not in methodtograph:
                continue
            processdot(func,cfgdir1,pdgdir1,astdir1,globaltxt)
            pdg_g = methodtograph[func][1]
            nodelist = pdg_g.node_set
            for _node in nodelist:
                if int(nodelist[_node].line) == line:
                    (src,dest,calledname,funcinfo,controls,iscontrol,parseok,orconditionlist) = stateOperands(func,nodelist[_node],astdir1,globaltxt)
                    if len(dest) == 1:
                        var = dest[0]
                        if _node not in flowlist:
                            flowone = Flow_Node(_node)
                        else:
                            flowone = flowlist[_node]
                        flowone.funcname = func
                        flowone.fromglobal = 1
                        flowone.frominput = 0
                        flowone.pdgnode = nodelist[_node]
                        flowone.line = line
                        flowone.optionlist.append(env)
                        flowone.optionlist = list(set(flowone.optionlist))
                        flowone.vars[var] = flowone.optionlist
                        if var in globalvariables:
                            globaloption[var] = flowone.optionlist
                            involvedglobal[var] = 0
                        flowlist[_node] = flowone
                        break
    return                   
            
  
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # programdir
    parser.add_argument("-programdir","--programdir",metavar = "string",help = "programdir")
    # program name
    parser.add_argument("-programname","--programname",metavar = "string",help = "programname")
    # start function
    parser.add_argument("-startfunction","--startfunction",metavar = "string",help = "startfunction")
    # if the parsing function is not the main function, give the line in main after parsing options 
    parser.add_argument("-anotherline","--anotherline",metavar = "string",help = "anotherline")
   
    parser.add_argument("-structreturnname","--structreturnname",metavar = "string",help = "structreturnname")

    parser.add_argument("-needoptimize","--needoptimize",metavar = "int",help = "needoptimize")
 
    parser.add_argument("-needstruct","--needstruct",metavar = "int",help = "needstruct funccallline")
    parser.add_argument("-optionprocessfunc","--optionprocessfunc",metavar = "string",help = "optionprocessfunc")
    
    arg = parser.parse_args()
    programdir = arg.programdir
    programname = arg.programname
    startfunction = arg.startfunction
    anotherline = arg.anotherline
    structreturnname = arg.structreturnname
    needoptimize = arg.needoptimize
    needstruct = arg.needstruct
    optionprocessfunc = arg.optionprocessfunc
    time1 = time.time()

    cfgdir1 = programdir +programname+"-cfg"
    pdgdir1 = programdir +programname+"-pdg"
    astdir1 = programdir +programname+"-ast"
    graphfile = programdir+"program_pdg.json"
    globaltxt = programdir+"global.txt"
    iivjsonfile = programdir + "iiv.json"
    divflowjsonfile = programdir+"div_flow.json"

    divjsonfile = programdir + "pass.json"
    envdivjsonfile = programdir + "div_env.json"
   
    proegdes(graphfile)
    if structreturnname == None:
        structreturnname = ""
    if needoptimize == None:
        needoptimize = 0
    else:
        needoptimize = int(needoptimize)
        
    if needstruct == None:
        needstruct = 0
    else:
        needstruct = int(needstruct)
    
    structvars = []
    
    if needstruct:
        processdot(startfunction,"",pdgdir1,astdir1,globaltxt)
        pdg_g = methodtograph[startfunction][1]
        nodelist = pdg_g.node_set
        tempnode = ""
        for _node in nodelist:
            if int(nodelist[_node].line) == needstruct:
                tempnode = nodelist[_node]
                break
        
        (src,dest,calledname,funcinfo,controls,iscontrol,parseok,orconditionlist) = stateOperands(startfunction,tempnode,astdir1,globaltxt)
        funcvars = funcinfo[optionprocessfunc]
        structvars.append(funcvars)
        processdot(optionprocessfunc,"",pdgdir1,astdir1,globaltxt)
        pdg_g = methodtograph[optionprocessfunc][1]
        paramlist = getParam(pdg_g)
        (ddrelation,toddrelation) = constructdd(pdg_g)
        definedparams = []
        for paramindex in range(len(paramlist)):
            paramid = paramlist[paramindex]
            paramvar = getparamvariable(paramid,ddrelation)
            definedparams.append(paramvar)
        structvars.append(definedparams)
   
    flow_list = div_propagation(divjsonfile,divflowjsonfile,envdivjsonfile,iivjsonfile,cfgdir1,pdgdir1,astdir1,globaltxt,anotherline,startfunction,structreturnname,needoptimize,structvars)
    time2 = time.time()
    print("time cost all:  %.2fs"%(time2-time1))