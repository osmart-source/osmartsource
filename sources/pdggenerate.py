#!/usr/bin/python

import argparse
import sys
from xml.dom.minicompat import NodeList

sys.path.append("/home/cmd/origin_ofg")

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
globalvariables,methods = [],[]
methodtodot = {"SWFMovie_add":"859"}
methodtograph = {}
taintflow = []
cfgdir = ""
pdgdir = ""
astdir = ""
processedfunction = {}
processedfunction["funcs"] = []
node2og = {}
globalinfo = {}

       
def processdot(funcname,cfgdir1,pdgdir1,astdir1,globaltxt):
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
    if funcname not in methods:
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
         
    return (ddrelation,toddrelation)

def constructcd(pdg_g):
    nodelist = pdg_g.node_set
    edgelist = pdg_g.edge_set
    cdrealtion = {}
    tocdrealtion = {}
    for edge in edgelist:
        if edgelist[edge].iscdg == 1:
            edgestart = edge[0]
            edgeend = edge[1]
            if edgestart not in cdrealtion:
                cdrealtion[edgestart] = []
            cdrealtion[edgestart].append(edgeend)
            if edgeend not in tocdrealtion:
                tocdrealtion[edgeend] = []
            tocdrealtion[edgeend].append(edgestart)
    return (cdrealtion,tocdrealtion)



def programpdg(startfunction,cfgdir1,pdgdir1,astdir1,globaltxt,programpdgdir,nodeinfodir):
    cdedgelist = []
    ddedgelist = []
    nodeall = {}
    nodeinfojson = {}
    
    processdot(startfunction,cfgdir1,pdgdir1,astdir1,globaltxt)
    methods = globalinfo["methods"]
    if startfunction in methodtograph:
        funcpdg = methodtograph[startfunction][1]
        (cdrelation,tocdrelation) = constructcd(funcpdg)
        nodelist = funcpdg.node_set
        for node in nodelist:
            if node not in nodeall:
                nodeall[node] = {}

            nodeall[node]["line"] = nodelist[node].line
            (src,dest,calledname,funcinfo,controls,iscontrol,parseok,orconditionlist) = stateOperands(startfunction,nodelist[node],astdir1,globaltxt)
            nodeinfojson[node] = {}
            nodeinfojson[node]["src"] = src
            nodeinfojson[node]["dest"] = dest
            nodeinfojson[node]["calledname"] = calledname
            nodeinfojson[node]["funcinfo"] = funcinfo
            nodeinfojson[node]["controls"] = controls
            nodeinfojson[node]["iscontrol"] = iscontrol
            nodeinfojson[node]["parseok"] = parseok
            nodeinfojson[node]["orconditionlist"] = orconditionlist
            nodeinfojson[node]["line"] = nodelist[node].line
            nodeinfojson[node]["funcname"] = startfunction
            if iscontrol:
                nodeall[node]["iscontrol"] = 1
            else:
                nodeall[node]["iscontrol"] = 0
            nodeall[node]["calledname"] = ""
            for func in funcinfo:
                if nodelist[node].type_str.strip() == func:
                    nodeall[node]["calledname"] = func
                    break
            
            nodetemp = nodelist[node]
            
            if nodetemp.type_str.strip() in methods:
                funcname = nodetemp.type_str.strip()
                if funcname != startfunction:
                    a=1
                    calledpdg(tocdrelation[node],funcname,cfgdir1,pdgdir1,astdir1,cdedgelist,ddedgelist,nodeall,globaltxt,nodeinfojson)
        
        edgelist = funcpdg.edge_set
        nodelist = funcpdg.node_set

        for edge in edgelist:
            edges = edgelist[edge]
            start = edge[0]
            end = edge[1]
            if nodelist[end].line < nodelist[start].line:
                continue
            if edges.isddg == 1:
                edgetemp = (edge[0],edge[1],edges.ddgparam)
                ddedgelist.append(edgetemp)
            if edges.iscdg == 1:
                
                edgetemp = (edge[0],edge[1],str(nodelist[edge[0]].line)+" "+nodelist[edge[0]].funcname)
                cdedgelist.append(edgetemp)
        res = {}
        res["dd"] = ddedgelist
        res["cd"] = cdedgelist
        res["node"] = nodeall
        with open(programpdgdir,"w") as f:
            f.write(json.dumps(res, indent=4))
        with open(nodeinfodir,"w") as f:
            f.write(json.dumps(nodeinfojson, indent=4))

def calledpdg(tocd,funcname,cfgdir1,pdgdir1,astdir1,cdedgelist,ddedgelist,nodeall,globaltxt,nodeinfojson):

    methods = globalinfo["methods"]
    processdot(funcname,cfgdir1,pdgdir1,astdir1,globaltxt)
    if funcname in methodtograph:
        funcpdg = methodtograph[funcname][1]
        if funcpdg == "":
            return
        nodelist = funcpdg.node_set
        (cdrelation,tocdrelation) = constructcd(funcpdg)
        
        startnode = -1
        for node1 in nodelist:
            nodes = nodelist[node1]
            if nodes.type_str == "METHOD":
                startnode = node1
                break
        if startnode != -1:
            for cd in tocd:
                cdedgelist.append((cd,startnode,"call"+funcname))
        if funcname in processedfunction["funcs"]:
            return

        else:
            processedfunction["funcs"].append(funcname)
        
        for nodeid in nodelist:
            if nodeid not in nodeall:
                nodeall[nodeid] = {}
            nodeall[nodeid]["line"] = nodelist[nodeid].line
            if nodelist[nodeid].dot_src == "UNUSED_HASH_ENTRY" or nodelist[nodeid].dot_src == "65535 / 3":
                (src,dest,calledname,funcinfo,controls,iscontrol,parseok,orconditionlist) = ([],[],[],{},[],0,1,[])
                continue
            (src,dest,calledname,funcinfo,controls,iscontrol,parseok,orconditionlist) = stateOperands(funcname,nodelist[nodeid],astdir1,globaltxt)
       
            nodeinfojson[nodeid] = {}
            nodeinfojson[nodeid]["src"] = src
            nodeinfojson[nodeid]["dest"] = dest
            nodeinfojson[nodeid]["calledname"] = calledname
            nodeinfojson[nodeid]["funcinfo"] = funcinfo
            nodeinfojson[nodeid]["controls"] = controls
            nodeinfojson[nodeid]["iscontrol"] = iscontrol
            nodeinfojson[nodeid]["parseok"] = parseok
            nodeinfojson[nodeid]["orconditionlist"] = orconditionlist
            nodeinfojson[nodeid]["line"] = nodelist[nodeid].line
            nodeinfojson[nodeid]["funcname"] = funcname
            if iscontrol :
                nodeall[nodeid]["iscontrol"] = 1
            else:
                nodeall[nodeid]["iscontrol"] = 0
            nodeall[nodeid]["calledname"] = ""
            for func in funcinfo:
                if nodelist[nodeid].type_str.strip() == func:
                    nodeall[nodeid]["calledname"] = func
                    break
            nodetemp = nodelist[nodeid]
            
            if nodelist[nodeid].type_str.strip() in methods:
                calledname = nodelist[nodeid].type_str.strip()
                if nodeid in tocdrelation:
                    tooo = tocdrelation[nodeid]
                else:
                    tooo = []
                calledpdg(tooo,calledname,cfgdir1,pdgdir1,astdir1,cdedgelist,ddedgelist,nodeall,globaltxt,nodeinfojson)
        edgelist = funcpdg.edge_set
        for edge in edgelist:
            edges = edgelist[edge]
            start = edge[0]
            end = edge[1]
            if nodelist[end].line < nodelist[start].line:
                continue
            if edges.isddg == 1:
                edgetemp = (edge[0],edge[1],edges.ddgparam)
                ddedgelist.append(edgetemp)
            if edges.iscdg == 1:
                edgetemp = (edge[0],edge[1],str(nodelist[edge[0]].line)+" "+nodelist[edge[0]].funcname)
                cdedgelist.append(edgetemp)
    return 


def ddarrangenode(ddrelation,pdg_g):
    nodeset = pdg_g.node_set
    nodeline = {}
    lines = []
    for node in nodeset:
        line = int(nodeset[node].line)
        lines.append(line)
        if line in nodeline:
            nodeline[line].append(node)
        else:
            nodeline[line] = [node]
    lines = set(lines)
    lines = list(lines)
    lines.sort()
    sortlist = []
    for line in lines:
        if(len(nodeline[line]) > 1):
            nodeid = nodeline[line][0]
            if(nodeset[nodeid].type_str  in ["METHOD","METHOD_RETURN","PARAM"]):
                sortlist.extend(nodeline[line])
            else:
                sortlist.extend(temp)
        else:
            sortlist.extend(nodeline[line]) 
    return sortlist  


def arrangenode(nodes,ddrelation):
    indegree = dict((u,0) for u in nodes)
    num = len(indegree)
    for u in ddrelation:
        for v in ddrelation[u]:
            # #print(v)
            if(u in nodes and v[0] in nodes):
                indegree[v[0]] += 1
    Q = [u for u in indegree if indegree[u] == 0]
    seq = []
    Q1 = copy.deepcopy(Q)
    while Q:
        u = Q.pop(0)
        seq.append(u)
        if u in ddrelation:
            for v in ddrelation[u]:
                if v[0] in nodes:
                    indegree[v[0]] -= 1
                    if indegree[v[0]] == 0:
                        Q.append(v[0])
    if seq == Q1:
        seq.sort(reverse = True)
    if(len(seq) == num):
        return seq
    else:
        seq = nodes
        seq.extend(nodes)
    return seq

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

def stateOperands(funcname,node,astdir1,globaltxt):
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
            # {'SWFMovie_save': ['mo', 'outputfile']}
            funcname = func
            funcvars = funcinfo[func]
            for i in range(len(funcvars)):
                if "&amp;" in funcvars[i]:
                    funcvars[i] = funcvars[i][5:]
            funcinfo[func] = funcvars
        # parse result
        # process for information
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
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument("-divjsonfile","--divjsonfile",metavar = "string",help = "divfile")
    # parser.add_argument("-divflowjsonfile","--divflowjsonfile",metavar = "string",help = "divflowfile")
    parser.add_argument("-programdir","--programdir",metavar = "string",help = "programdir")
    parser.add_argument("-programname","--programname",metavar = "string",help = "programname")
    parser.add_argument("-startfunction","--startfunction",metavar = "string",help = "startfunction")
    # parser.add_argument("-anotherline","--anotherline",metavar = "string",help = "anotherline")
    # parser.add_argument("-iivjsonfile","--iivjsonfile",metavar = "string",help = "iivfile")
    arg = parser.parse_args()
    programdir = arg.programdir
    programname = arg.programname
    startfunction = arg.startfunction
    time1 = time.time()
    cfgdir1 = programdir +programname+"-cfg"
    pdgdir1 = programdir +programname+"-pdg"
    astdir1 = programdir +programname+"-ast"
    globaltxt = programdir+"global.txt"
    programpdgdir = programdir + "program_pdg.json"
    nodeinfodir = programdir + "nodeinfo.json"
    programpdg(startfunction,cfgdir1,pdgdir1,astdir1,globaltxt,programpdgdir,nodeinfodir)
    time2 = time.time()
    print("time cost :  %.2fs"%(time2-time1))



