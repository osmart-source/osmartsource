#!/usr/bin/python

import os
import subprocess
import sys

sys.path.append("..")

import utils

globalvariables,methods = [],[]
if True:
    CFG_NODE_TYPE_NULL                      = 0x0
    CFG_NODE_TYPE_METHOD                    = 0x1
    CFG_NODE_TYPE_PARAM                     = 0x2
    CFG_NODE_TYPE_FIELD_IDENT               = 0x3
    CFG_NODE_TYPE_RETURN                    = 0x4
    CFG_NODE_TYPE_METHOD_RETURN             = 0x5
    CFG_NODE_TYPE_UNKNOWN                   = 0x6
    CFG_NODE_TYPE_OP_ASSGIN                 = 0x7
    CFG_NODE_TYPE_OP_ASSGPLUS               = 0x8
    CFG_NODE_TYPE_OP_ASSGMINUS              = 0x9
    CFG_NODE_TYPE_OP_ASSGDIVISION           = 0x10
    CFG_NODE_TYPE_OP_ASSGMUL                = 0x11
    CFG_NODE_TYPE_OP_ASSGOR                 = 0x12
    CFG_NODE_TYPE_OP_ADROF                  = 0x13
    CFG_NODE_TYPE_OP_FIELDACCESS            = 0x14
    CFG_NODE_TYPE_OP_INDFIELDACCESS         = 0x15
    CFG_NODE_TYPE_OP_INDINDEXACCESS         = 0x16
    CFG_NODE_TYPE_OP_IND                    = 0x17
    CFG_NODE_TYPE_OP_LOGICALNOT             = 0x18
    CFG_NODE_TYPE_OP_LOGICALAND             = 0x19
    CFG_NODE_TYPE_OP_LOGICALOR              = 0x20
    CFG_NODE_TYPE_OP_EQUAL                  = 0x21
    CFG_NODE_TYPE_OP_NOTEQUAL               = 0x22
    CFG_NODE_TYPE_OP_ARRAYINIT              = 0x23
    CFG_NODE_TYPE_OP_CONSINIT               = 0x24
    CFG_NODE_TYPE_OP_ADD                    = 0x25
    CFG_NODE_TYPE_OP_MINUS                  = 0x26
    CFG_NODE_TYPE_OP_MULTI                  = 0x27
    CFG_NODE_TYPE_OP_MODULO                 = 0x28
    CFG_NODE_TYPE_OP_ADDITION               = 0x29
    CFG_NODE_TYPE_OP_SUBTRACT               = 0x30
    CFG_NODE_TYPE_OP_DIVISION               = 0x31
    CFG_NODE_TYPE_OP_ARITHSHIFTR            = 0x32
    CFG_NODE_TYPE_OP_ARITHSHIFTL            = 0x33
    CFG_NODE_TYPE_OP_SHIFTR                 = 0x34
    CFG_NODE_TYPE_OP_SHIFTL                 = 0x35
    CFG_NODE_TYPE_OP_AND                    = 0x36
    CFG_NODE_TYPE_OP_OR                     = 0x37
    CFG_NODE_TYPE_OP_XOR                    = 0x38
    CFG_NODE_TYPE_OP_NOT                    = 0x39
    CFG_NODE_TYPE_OP_PLUS                   = 0x40
    CFG_NODE_TYPE_OP_LESSTHAN               = 0x41
    CFG_NODE_TYPE_OP_LESSEQTHAN             = 0x42
    CFG_NODE_TYPE_OP_GREATERTHAN            = 0x43
    CFG_NODE_TYPE_OP_GREATEREQTHAN          = 0x44
    CFG_NODE_TYPE_OP_POSTDEC                = 0x45
    CFG_NODE_TYPE_OP_PREDEC                 = 0x46
    CFG_NODE_TYPE_OP_PREINC                 = 0x47
    CFG_NODE_TYPE_OP_POSTINC                = 0x48
    CFG_NODE_TYPE_OP_SIZEOF                 = 0x49
    CFG_NODE_TYPE_OP_COND                   = 0x50
    CFG_NODE_TYPE_OP_CAST                   = 0x51
    CFG_NODE_TYPE_OP_UNKNOWN                = 0x52
    CFG_NODE_TYPE_OP_THROW                  = 0x53
    CFG_NODE_TYPE_OP_NEW                    = 0x54
    CFG_NODE_TYPE_OP_DELETE                 = 0x55
    CFG_NODE_TYPE_LITERAL                   = 0x56
    CFG_NODE_TYPE_REAL_METHOD               = 0x1000

def get_type(type_str):
    if type_str == 'METHOD':                #1
        return CFG_NODE_TYPE_METHOD
    if type_str == 'LITERAL':
        return CFG_NODE_TYPE_LITERAL
    elif type_str == 'PARAM':               #2
        return CFG_NODE_TYPE_PARAM
    elif type_str == 'FIELD_IDENTIFIER':    #6
        return CFG_NODE_TYPE_FIELD_IDENT    
    elif type_str == 'RETURN':              #A
        return CFG_NODE_TYPE_RETURN        
    elif type_str == 'METHOD_RETURN':       #B
        return CFG_NODE_TYPE_METHOD_RETURN
    elif type_str == 'UNKNOWN':             #C
        return CFG_NODE_TYPE_UNKNOWN        
    elif type_str == '&lt;operator&gt;.assignment':
        return CFG_NODE_TYPE_OP_ASSGIN   
    elif type_str == '&lt;operator&gt;.assignmentPlus':
        return CFG_NODE_TYPE_OP_ASSGPLUS   
    elif type_str == '&lt;operator&gt;.assignmentMinus':
        return CFG_NODE_TYPE_OP_ASSGMINUS   
    elif type_str == '&lt;operator&gt;.assignmentDivision':
        return CFG_NODE_TYPE_OP_ASSGDIVISION  
    elif type_str == '&lt;operator&gt;.assignmentMultiplication':
        return CFG_NODE_TYPE_OP_ASSGMUL  
    elif type_str == '&lt;operators&gt;.assignmentOr':
        return CFG_NODE_TYPE_OP_ASSGOR
    elif type_str == '&lt;operator&gt;.addressOf':
        return CFG_NODE_TYPE_OP_ADROF  
    elif type_str == '&lt;operator&gt;.fieldAccess':
        return CFG_NODE_TYPE_OP_FIELDACCESS 
    elif type_str == '&lt;operator&gt;.indirectFieldAccess':
        return CFG_NODE_TYPE_OP_INDFIELDACCESS  
    elif type_str == '&lt;operator&gt;.indirectIndexAccess':
        return CFG_NODE_TYPE_OP_INDFIELDACCESS  
    elif type_str == '&lt;operator&gt;.indirection':
        return CFG_NODE_TYPE_OP_IND   
    elif type_str == '&lt;operator&gt;.logicalNot':
        return CFG_NODE_TYPE_OP_LOGICALNOT
    elif type_str == '&lt;operator&gt;.logicalAnd':
        return CFG_NODE_TYPE_OP_LOGICALAND        
    elif type_str == '&lt;operator&gt;.logicalOr':
        return CFG_NODE_TYPE_OP_LOGICALOR 
    elif type_str == '&lt;operator&gt;.equals':
        return CFG_NODE_TYPE_OP_EQUAL
    elif type_str == '&lt;operator&gt;.notEquals':
        return CFG_NODE_TYPE_OP_NOTEQUAL
    elif type_str == '&lt;operator&gt;.arrayInitializer':
        return CFG_NODE_TYPE_OP_ARRAYINIT
    elif type_str == '&lt;operator&gt;.constructorInitializer':
        return CFG_NODE_TYPE_OP_CONSINIT
    elif type_str == '&lt;operator&gt;.add':
        return CFG_NODE_TYPE_OP_ADD
    elif type_str == '&lt;operator&gt;.minus':
        return CFG_NODE_TYPE_OP_MINUS
    elif type_str == '&lt;operator&gt;.multiplication':
        return CFG_NODE_TYPE_OP_MULTI
    elif type_str == '&lt;operator&gt;.modulo':
        return CFG_NODE_TYPE_OP_MODULO
    elif type_str == '&lt;operator&gt;.addition':
        return CFG_NODE_TYPE_OP_ADDITION
    elif type_str == '&lt;operator&gt;.subtraction':
        return CFG_NODE_TYPE_OP_SUBTRACT
    elif type_str == '&lt;operator&gt;.division':
        return CFG_NODE_TYPE_OP_DIVISION
    elif type_str == '&lt;operator&gt;.arithmeticShiftRight':
        return CFG_NODE_TYPE_OP_ARITHSHIFTR
    elif type_str == '&lt;operator&gt;.arithmeticShiftLeft':
        return CFG_NODE_TYPE_OP_ARITHSHIFTL
    elif type_str == '&lt;operator&gt;.shiftLeft':
        return CFG_NODE_TYPE_OP_SHIFTL
    elif type_str == '&lt;operator&gt;.shiftRight':
        return CFG_NODE_TYPE_OP_SHIFTR
    elif type_str == '&lt;operator&gt;.and':
        return CFG_NODE_TYPE_OP_AND
    elif type_str == '&lt;operator&gt;.or':
        return CFG_NODE_TYPE_OP_OR
    elif type_str == '&lt;operator&gt;.xor':
        return CFG_NODE_TYPE_OP_XOR
    elif type_str == '&lt;operator&gt;.not':
        return CFG_NODE_TYPE_OP_NOT
    elif type_str == '&lt;operator&gt;.plus':
        return CFG_NODE_TYPE_OP_PLUS
    elif type_str == '&lt;operator&gt;.lessThan':
        return CFG_NODE_TYPE_OP_LESSTHAN
    elif type_str == '&lt;operator&gt;.lessEqualsThan':
        return CFG_NODE_TYPE_OP_LESSEQTHAN
    elif type_str == '&lt;operator&gt;.greaterThan':
        return CFG_NODE_TYPE_OP_GREATERTHAN
    elif type_str == '&lt;operator&gt;.greaterEqualsThan':
        return CFG_NODE_TYPE_OP_GREATEREQTHAN
    elif type_str == '&lt;operator&gt;.postDecrement':
        return CFG_NODE_TYPE_OP_POSTDEC
    elif type_str == '&lt;operator&gt;.preDecrement':
        return CFG_NODE_TYPE_OP_PREDEC
    elif type_str == '&lt;operator&gt;.preIncrement':
        return CFG_NODE_TYPE_OP_PREINC
    elif type_str == '&lt;operator&gt;.postIncrement':
        return CFG_NODE_TYPE_OP_POSTINC
    elif type_str == '&lt;operator&gt;.sizeOf':
        return CFG_NODE_TYPE_OP_SIZEOF 
    elif type_str == '&lt;operator&gt;.conditional':
        return CFG_NODE_TYPE_OP_COND
    elif type_str == '&lt;operator&gt;.cast':
        return CFG_NODE_TYPE_OP_CAST
    elif type_str == '&lt;operator&gt;.unknown':
        return CFG_NODE_TYPE_OP_UNKNOWN
    elif type_str == '&lt;operator&gt;.throw':
        return CFG_NODE_TYPE_OP_THROW
    elif type_str == '&lt;operator&gt;.new':
        return CFG_NODE_TYPE_OP_NEW
    elif type_str == '&lt;operator&gt;.delete':
        return CFG_NODE_TYPE_OP_DELETE
    elif type_str in methods:
        return CFG_NODE_TYPE_REAL_METHOD
    else:
        return CFG_NODE_TYPE_NULL

class PDG_Node:
    num     = -1
    type    = CFG_NODE_TYPE_NULL
    type_str= ''
    src     = ''
    dot_src = ''
    line    = -1
    funcname = ""
    
    def __init__(self, num, mytype=CFG_NODE_TYPE_NULL):
        self.num = num
        self.type = mytype
        self.child = []
        self.parent = []
        
class PDG_Edge:
    ddgparam = []
    def __init__(self,startnode,endnode,iscfg,iscdg,isddg):
        self.start = startnode
        self.end = endnode
        self.iscfg = iscfg
        self.iscdg = iscdg
        self.isddg = isddg
        self.ddgparam = []
        


class PDG_Graph:
    name = 'unknown'
    
    
    def __init__(self, name):
        self.name = name
        self.node_set = {}
        self.edge_set = {}

    def set_name(self, name):
        self.name = name
    def get_name(self):
        return self.name

            
                

"""
NOTE:   this ugly logic is for the 0-ast,
        containing a complete ast for the 
        whole module(file)
"""
def pdgpreprocess(funcname,pdg_file,globaltxt): 
    # print(globaltxt)
    globalvariables,methods = utils.get_global(globaltxt)
    # print(methods)
    pdg_g = ''
    nodelist = {}
    edgelist = {}
    entryid = -1
    # nodearray = []
    with open(pdg_file) as af:
        contents = af.readlines()
    for line in contents:
        line = line.strip()
        if line[:7]=='digraph': #graph
            m = line.split(' ')[1][1:-1].strip()
            if not( m in methods):
                # print ("pdg_file: not in method",m)
                return pdg_g
            
            #print 'GRAPH: %s'%(ast_g.get_name())
            pdg_g = PDG_Graph(line[line.find('\"')+1:line.rfind('\"')])
        elif line.count("[label = <(") > 0:
           
            str1 = " [label = <("
            index1 = line.find(str1)
            nodeid = line[0:index1]
            nodeid = int(nodeid[1:-1])
            
            index2 = index1 + len(str1)
            if line.find('SUB')== -1:
                continue
            if line.count(")") > 0:
                index3 = line.rfind(")")
                nodeinfo = line[index2:index3]
                nodeattrs = utils.split_line(nodeinfo)

                op = nodeattrs[0]
                optype = get_type(op)
                if len(nodeattrs) > 1:
                    dotsrc = nodeattrs[1]
                else :
                    dotsrc = ""
                index4 = line.find("<SUB>")+len("<SUB>")
                index5 = line.find("</SUB>")
                linenumber = line[index4:index5]
                node = PDG_Node(nodeid,optype)
                node.line = int(linenumber)
                node.type = optype
                node.dot_src = dotsrc
                node.type_str = op
                node.funcname = funcname
                # if(op == "compile_init_actions"):
                #     print(op)
                if node.type_str == "METHOD":
                    entryid = nodeid
                nodelist[nodeid] = node
                
        elif line.count(" -> ") > 0 and line.count("  [ label =") > 0 :
            # PDG edge
            str1 = "  [ label = "
            index1 = line.find(str1)
            index2 = index1+len(str1)
            twonodes = line[:index1]
            fromnode = twonodes.split()[0]
            tonode = twonodes.split()[-1]
            fromid = int(fromnode[1:-1])
            toid = int(tonode[1:-1])
            if fromid in nodelist and toid in nodelist:
                nodelist[fromid].child.append(toid)
                nodelist[toid].parent.append(fromid)
                labels = line[index2:-1]
                if labels[1:4] == "DDG":
                    ddparam = labels[6:-1]
                    if(ddparam[0:5] == "&amp;"):
                        ddparam = ddparam[5:]
                    # print(ddparam)
                    if((fromid,toid) in edgelist and edgelist[(fromid,toid)].isddg):
                        # print(fromid,toid)
                        edge = edgelist[(fromid,toid)]
                        edge.ddgparam.append(ddparam)
                        edgelist[(fromid,toid)] = edge
                    elif (fromid,toid) not in edgelist:
                        edge = PDG_Edge(nodelist[fromid],nodelist[toid],0,0,1)
                        edge.ddgparam.append(ddparam)
                        edge.start = fromid
                        edge.end = toid
                        edgelist[(fromid,toid)] = edge
                    # print("ddgedg:",fromid," ",toid," ",edge.ddgparam)
                    # print("ddg:",fromid," ",toid)
                    
                elif labels[1:4] == "CDG":
                    if((fromid,toid) in edgelist):
                        edge = edgelist[(fromid,toid)]
                        edge.iscdg = 1
                        edgelist[(fromid,toid)] = edge
                    elif (fromid,toid) not in edgelist:
                        edge = PDG_Edge(nodelist[fromid],nodelist[toid],0,1,0)
                        edgelist[(fromid,toid)] = edge
    if entryid != -1:
        for nodeid in nodelist:
            node = nodelist[nodeid]
            if((entryid,nodeid) in edgelist):
                edge = edgelist[(entryid,nodeid)]
            else:
                edge = PDG_Edge(nodelist[entryid],nodelist[nodeid],0,0,0)
            edge.start = entryid
            edge.end = nodeid
            edge.iscdg = 1
            edge.isddg = 0
            edgelist[(entryid,nodeid)] = edge
            
                    
    pdg_g.node_set = nodelist
    pdg_g.edge_set = edgelist
    # for edge in edgelist:
    #     print(edge)
    return pdg_g 

def getParam(pdg_g):
    nodelist = pdg_g.node_set
    paramlist = []
    for node in nodelist:
        nodecur = nodelist[node]
        if(nodecur.type == CFG_NODE_TYPE_PARAM):
            paramlist.append(node)
    paramlist.sort()
    return paramlist

        

# if __name__ == '__main__':
        
#     linux_dir = sys.argv[1]
#     cfg_g = preprocess(linux_dir)
#     nodes = cfg_g.node_set
#     edges = cfg_g.edge_set
#     # print(nodes)
#     for key in nodes:
#         print(key)
#     # # print(list(nodes.keys))
#     for key in edges:
#         print(key)
#     # print(list(edges.keys))
#         # print(node)
