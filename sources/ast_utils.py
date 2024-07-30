import os
import sys

from ast_graph import *

# sys.path.append("..")

# from util import utils

# specil split ',' from the line    
# eg. strcmp,strcmp(argv[i], &quot;-a&quot;) --> [strcmp] and [strcmp(argv[i], &quot;-a&quot;)]
def split_line(line):
    left = 0
    cnt_small  = 0
    cnt_big = 0
    cnt_mid = 0
    cnt_quot = 0
    cnt_single_quot = 0
    res_list = []
    for index in range(len(line)):
        if line[index] == '(' and cnt_quot % 2 == 0 and cnt_quot % 2 == 0:
            cnt_small = cnt_small + 1
        elif line[index] == ')' and cnt_quot % 2 == 0 and cnt_quot % 2 == 0:
            cnt_small = cnt_small - 1
        elif line[index] == '[' and cnt_quot % 2 == 0 and cnt_quot % 2 == 0:
            cnt_mid = cnt_mid + 1
        elif line[index] == ']' and cnt_quot % 2 == 0 and cnt_quot % 2 == 0:
            cnt_mid = cnt_mid - 1
        elif line[index] == '{' and cnt_quot % 2 == 0 and cnt_quot % 2 == 0:
            cnt_big = cnt_big + 1
        elif line[index] == '}' and cnt_quot % 2 == 0 and cnt_quot % 2 == 0:
            cnt_big = cnt_big - 1
        elif line[index] == "'" and cnt_quot % 2 == 0:
            cnt_single_quot = cnt_single_quot + 1
        elif line[index] == '&' and line[index + 1] == 'q' and line[index + 2] == 'u' and line[index + 3] == 'o' and line[index + 4] == 't' and cnt_single_quot %2 == 0:
            cnt_quot = cnt_quot + 1
        if line[index] == ',' and cnt_small == 0 and cnt_mid == 0 and cnt_big == 0 and cnt_quot % 2 == 0 and cnt_single_quot % 2 == 0:
            res_list.append(line[left: index])
            left = index + 1
    res_list.append(line[left: len(line)])
    return res_list

# get the control structure type
def get_control_type(cst):
    cst = cst.strip()
    ans = ""
    for index in range(len(cst)):
        if cst[index] >= 'a' and cst[index] <= 'z' or cst[index] >= 'A' and cst[index] <= 'Z' \
            or cst[index] == '_' or cst[index] >= '0' and cst[index] <= '9':
            ans += cst[index]
        else:
            break
    return ans

# get the left and right of '-'
def get_sub_left_right(content):
    left = ""
    right = ""
    for index in range(len(content)):
        if content[index] == '-' and content[index + 1] != '&':
            left = content[:index]
            right = content[index + 1:]
            break
    return left, right

# get the left and right of '>'
def get_gt_left_right(content):
    left = ""
    right = ""
    for index in range(len(content)):
        if content[index] == '&' and content[index + 1] == 'g' and content[index + 2] == 't'\
            and content[index + 3] == ';' and content[index - 1] != '-':
            left = content[:index].strip()
            right = content[index + 4:].strip()
    return left, right

def generate_graph(ast_file):
    ast_g = AST_Graph("")
    with open(ast_file) as f:
        while True:
            line = f.readline().strip()
            if line == "":
                break

            # the first line, eg: digraph "putw" { 
            if line[:7] == "digraph":
                method_name = line.split()[1][1:-1].strip()
                ast_g.set_name(method_name)
                
            # the node information, eg: "406" [label = <(METHOD,putw)<SUB>556</SUB>> ]
            elif line.find("label") != -1:
                node = AST_Node()
                node.custom = 0
                node.num = int(line.split('"')[1].strip())                      # eg. 406
                if line.find("<SUB>") == -1:
                    node.line = 0
                else:
                    node.line = int(line.split('>')[1].split('<')[0].strip())   # eg. 556
                node.dot_src = line                                             # eg. "406" [label = <(METHOD,putw)<SUB>556</SUB>> ]
                if line.split('<')[1].strip().split('>')[0] == '':              # eg. "20472" [label = <> ]
                    ast_g.node_set[node.num] = node
                    continue
                node_type = line.split('<')[1][1:-1].strip().split(',')[0].strip()
                node.type_str = node_type                                      # eg. METHOD
                node.type = get_type(node_type)                                # eg. AST_NODE_TYPE_METHOD
                temp = split_line(line.split('<')[1][1:-1].strip())             # the list of split by ','
                if node_type == "METHOD" and len(temp) == 2:
                    # METHOD,init
                    node.method_name =  temp[1]                                 # eg. init
                elif node_type == "PARAM" and len(temp) == 2:
                    # PARAM,char *str
                    if len(temp[1].strip().split()) == 2:
                        node.param_type = temp[1].strip().split()[0]            # eg. char
                        node.param_name = temp[1].strip().split()[1]            # eg. *str
                    elif len(temp[1].strip().split()) > 2:
                        node.param_type = ' '.join(temp[1].strip().split()[0:-1])   # eg. const char
                        node.param_name = temp[1].strip().split()[-1]           # eg. *str
                elif node_type == "METHOD_RETURN" and len(temp) == 2:
                    # METHOD_RETURN,int
                    node.return_type = temp[1].strip()                          # int
                elif node_type == "LOCAL" and len(temp) == 2:
                    # LOCAL,int delta: int
                    node.local_type = temp[1].strip().split(':')[-1].strip()    # int
                    node.local_content = temp[1].strip().split(":")[0].strip()  # int doSum
                elif node_type == "IDENTIFIER" and len(temp) == 3:
                    # IDENTIFIER,flag,flag = 0
                    node.ide_var = temp[1].strip()                              # flag
                    node.ide_content = temp[2].strip()                          # flag = 0
                elif node_type == "FIELD_IDENTIFIER" and len(temp) == 3:
                    # FIELD_IDENTIFIER,out,out
                    node.fide_left = temp[1].strip()                            # out
                    node.fide_right = temp[2].strip()                           # out
                elif node_type == "BLOCK" and len(temp) == 3:
                    # BLOCK,&lt;empty&gt;,&lt;empty&gt;
                    node.block_left = temp[1].strip()                           # &lt;empty&gt;
                    node.block_right = temp[2].strip()                          # &lt;empty&gt;
                elif node_type == "CONTROL_STRUCTURE" and len(temp) == 3:
                    # CONTROL_STRUCTURE,else,else
                    node.cst_left = temp[1].strip()                             # else
                    node.cst_left_type = get_control_type(node.cst_left)        # else
                    node.cst_right = temp[2].strip()                            # else
                    node.cst_right_type = get_control_type(node.cst_right)
                elif node_type == "LITERAL" and len(temp) == 3:
                    # LITERAL,1,i = 1
                    node.lit_var = temp[1].strip()                              # 1
                    node.lit_content = temp[2].strip()                          # i = 1
                elif node_type == "JUMP_TARGET" and len(temp) == 2:
                    # JUMP_TARGET,fail
                    node.jt_content = temp[1].strip()                           # fail
                elif node_type == "RETURN" and len(temp) == 3:
                    # RETURN,return 0;,return 0;
                    node.return_left = temp[1].strip()                          # return 0;
                    node.return_right = temp[2].strip()                         # return 0;
                elif node_type == "METHOD_RETURN" and len(temp) == 2:
                    # METHOD_RETURN,void
                    node.rt_type = temp[1].strip()                              # void
                elif node_type == "UNKNOWN" and len(temp) == 3:
                    # UNKNOWN,w,w
                    node.unknown_left = temp[1].strip()                         # w
                    node.unknown_right = temp[2].strip()                        # w
                elif node_type == "&lt;operator&gt;.assignment" and len(temp) == 2:
                    # &lt;operator&gt;.assignment,flag = ENABLE_DEBUG
                    node.assign_content = temp[1].strip()                       # flag = ENABLE_DEBUG
                    node.assign_var = temp[1].strip().split("=")[0].strip()     # flag
                elif node_type == "&lt;operator&gt;.addressOf" and len(temp) == 2:
                    # &lt;operator&gt;.addressOf,&amp;widestr
                    node.addressof_content = temp[1].strip()                    # &amp;widestr
                    node.addressof_var = temp[1].strip().split(';')[1].strip()  # widestr
                elif node_type == "&lt;operator&gt;.fieldAccess" and len(temp) == 2:
                    # &lt;operator&gt;.fieldAccess,record.record    the last dot
                    node.field_access_content = temp[1].strip()                 # record.record
                elif node_type == "&lt;operator&gt;.indirectFieldAccess" and len(temp) == 2:
                    # &lt;operator&gt;.indirectFieldAccess,text-&gt;currentRecord
                    node.infa_content = temp[1].strip()                        # text-&gt;currentRecord
                    node.infa_var = node.infa_content.split("-&gt;")[-1].split()# currentRecord
                elif node_type == "&lt;operator&gt;.logicalNot" and len(temp) == 2:
                    # &lt;operator&gt;.logicalNot,!(SWFOutput_numSBits(dx) &lt; 18)     < or >?
                    node.logic_not_content = temp[1].strip()                          # '!(SWFOutput_numSBits(dx) &lt; 18)
                elif node_type == "&lt;operator&gt;.logicalAnd" and len(temp) == 2:
                    # &lt;operator&gt;.logicalAnd,dx == 0 &amp;&amp; dy == 0
                    node.and_content = temp[1].strip()                          # dx == 0 &amp;&amp; dy == 0
                    node.and_list = node.and_content.split("&amp;&amp;")
                elif node_type == "&lt;operator&gt;.logicalOr" and len(temp) == 2:
                    # &lt;operator&gt;.logicalOr,textRecord == NULL || textRecord-&gt;string != NULL
                    node.or_content = temp[1].strip()                        # textRecord == NULL || textRecord-&gt;string != NULL
                    node.or_list = node.or_content.split("||")
                elif node_type == "&lt;operator&gt;.indirectIndexAccess" and len(temp) ==  2:
                    # &lt;operator&gt;.indirectIndexAccess,widestring[i]
                    node.indirect_ia_content = temp[1].strip()                  # widestring[i]
                    if len(node.indirect_ia_content.split('[')) > 1:
                        node.indirect_ia_index = node.indirect_ia_content.split('[')[1].strip().split(']')[0].strip()   # i
                        node.indirect_ia_array = node.indirect_ia_content.split('[')[0].strip() # widestring
                elif node_type == "&lt;operator&gt;.equals" and len(temp) == 2:
                    # &lt;operator&gt;.equals,textRecord-&gt;advance == NULL
                    node.equal_content = temp[1].strip()                        # textRecord-&gt;advance == NULL
                    node.equal_list = node.equal_content.split("==")            # textRecord-&gt;advance, NULL
                elif node_type == "&lt;operator&gt;.notEquals" and len(temp) == 2:
                    # &lt;operator&gt;.notEquals,textRecord-&gt;advance != NULL
                    node.notequal_content = temp[1].strip()                     # textRecord-&gt;advance != NULL
                    node.notequal_list = node.notequal_content.split("!=")      # textRecord-&gt;advance, NULL
                elif node_type == "&lt;operator&gt;.arrayInitializer" and len(temp) == 2:
                    # &lt;operator&gt;.arrayInitializer,{0, 0}
                    node.arrayInit_content = temp[1].strip()                    # {0, 0}
                elif node_type == "&lt;operator&gt;.subtraction" and len(temp) == 2:
                    # &lt;operator&gt;.subtraction,nBits-2
                    node.subtraction_content = temp[1].strip()
                    node.subtraction_left, node.subtraction_right = get_sub_left_right(node.subtraction_content)    # nBits, 2
                elif node_type == "&lt;operator&gt;.lessThan" and len(temp) == 2:
                    # &lt;operator&gt;.lessThan,nBits &lt; 18
                    node.less_than_content = temp[1].strip()                    # nBits &lt; 18
                    node.less_than_left = node.less_than_content.split("&lt;")[0].strip()   # nBits
                    node.less_than_right = node.less_than_content.split("&lt;")[1].strip()  # 18
                elif node_type == "&lt;operator&gt;.sizeOf" and len(temp) == 2:
                    # &lt;operator&gt;.sizeOf,sizeof(unsigned short)
                    node.sizeOf_content = temp[1].strip()                       # sizeof(unsigned short)
                    node.sizeOf_var = node.sizeOf_content[7:-1]                 # unsigned short
                elif node_type == "&lt;operator&gt;.indirection" and len(temp) == 2:
                    # &lt;operator&gt;.indirection,*psSample
                    node.indirect_content = temp[1].strip()                     # *psSample
                elif node_type == "&lt;operator&gt;.not" and len(temp) == 2:
                    # &lt;operator&gt;.not,~__val
                    node.not_content = temp[1].strip()                          # ~__val
                    node.not_var = node.not_content[1:]                         # __val
                elif node_type == "&lt;operator&gt;.and" and len(temp) == 2:
                    # &lt;operator&gt;.and,flags &amp; SWF_SHAPE_MOVETOFLAG
                    node.and_content = temp[1].strip()
                    node.and_left = node.and_content.split("&amp;")[0].strip()  # flags
                    if len(node.and_content.split("&amp;")) > 1:
                        node.and_right = node.and_content.split("&amp;")[1].strip() # SWF_SHAPE_MOVETOFLAG
                elif node_type == "&lt;operator&gt;.or" and len(temp) == 2:
                    # &lt;operator&gt;.or,0 | flags
                    node.or_content = temp[1].strip()                           # 0 | flags
                    node.or_left = node.or_content.split('|')[0].strip()        # 0
                    if len(node.or_content.split('|')) > 1:
                        node.or_right = node.or_content.split('|')[1].strip()       # flags
                elif node_type == "&lt;operator&gt;.greaterThan" and len(temp) == 2:
                    # &lt;operator&gt;.greaterThan,x+width &gt; rect-&gt;maxX
                    node.gt_content = temp[1].strip()                           # x+width &gt; rect-&gt;maxX
                    node.gt_left, node.gt_right = get_gt_left_right(node.gt_content)    # x+width, rect-&gt;maxX
                elif node_type == "&lt;operator&gt;.greaterEqualsThan" and len(temp) == 2:
                    # &lt;operator&gt;.greaterEqualsThan,tag.timeStamp &gt;= msecs
                    node.get_content = temp[1].strip()                          # tag.timeStamp &gt;= msecs
                    node.get_left = node.get_content.split("&gt;=")[0].strip()  # tag.timeStamp
                    node.get_right = node.get_content.split("&gt;=")[1].strip() # msecs
                elif node_type == "&lt;operator&gt;.lessEqualsThan" and len(temp) == 2:
                    # &lt;operator&gt;.lessEqualsThan,i&lt;=max_init_action_frame
                    node.let_content = temp[1].strip()                          # i&lt;=max_init_action_frame
                    node.let_left = node.let_content.split("&lt;=")[0].strip()  # i
                    node.let_right = node.let_content.split("&lt;=")[1].strip() # max_init_action_frame
                elif node_type == "&lt;operator&gt;.conditional" and len(temp) == 2:
                    # &lt;operator&gt;.conditional,(iDiff &lt; 0) ? iSignBit : 0
                    
                    node.cond_content = temp[1].strip()                         # (iDiff &lt; 0) ? iSignBit : 0
                    node.cond_cond = node.cond_content.split('?')[0].strip()    # (iDiff &lt; 0) 
                    # node.cond_true = node.cond_content.split('?')[1].split(':')[0].strip()  # iSignBit
                    # node.cond_false = node.cond_content.split('?')[1].split(':')[1].strip() # 0
                elif node_type == "&lt;operator&gt;.addition" and len(temp) == 2:
                    # &lt;operator&gt;.addition,n+1
                    node.add_content = temp[1].strip()                          # n + 1
                    node.add_left = node.add_content.split('+')[0].strip()      # n
                    node.add_right = node.add_content.split('+')[1].strip()     # 1
                elif node_type == "&lt;operator&gt;.plus" and len(temp) == 2:
                    # &lt;operator&gt;.plus,+ 1
                    node.plus_content = temp[1].strip()                         # + 1
                    node.plus_var = node.plus_content[1:].strip()               # 1
                elif node_type == "&lt;operator&gt;.minus" and len(temp) == 2:
                    # &lt;operator&gt;.minus,-32768
                    node.minus_content = temp[1].strip()                        # -32768
                    node.minus_var = node.minus_content[1:]                     # 32768
                elif node_type == "&lt;operator&gt;.multiplication" and len(temp) == 2:
                    # &lt;operator&gt;.multiplication,width * 20
                    node.multi_content = temp[1].strip()                        # width * 20
                    if len(node.multi_content.split('*')) > 1:
                        node.multi_left = node.multi_content.split('*')[0].strip()  # width
                        node.multi_right = node.multi_content.split('*')[1].strip() # 20
                elif node_type == "&lt;operator&gt;.division" and len(temp) == 2:
                    # &lt;operator&gt;.division,size/1024.0
                    node.div_content = temp[1].strip()                          # size/1024.0
                    node.div_left = node.div_content.split('/')[0].strip()      # size
                    node.div_right = node.div_content.split('/')[1].strip()     # 1024.0
                elif node_type == "&lt;operator&gt;.modulo" and len(temp) == 2:
                    # &lt;operator&gt;.modulo,bitsize % blocksize
                    node.modulo_content = temp[1].strip()                       # bitsize % blocksize
                    node.modulo_left = node.modulo_content.split('%')[0].strip()    # bitsize
                    node.modulo_right = node.modulo_content.split('%')[1].strip()   # blocksize
                elif node_type == "&lt;operator&gt;.assignmentPlus" and len(temp) == 2:
                    # &lt;operator&gt;.assignmentPlus,xsize+=ccsize
                    node.assign_plus_content = temp[1].strip()                              # xsize+=ccsize
                    node.assign_plus_left = node.assign_plus_content.split("+=")[0].strip() # xsize
                    node.assign_plus_right = node.assign_plus_content.split("+=")[1].strip()    # ccsize
                elif node_type == "&lt;operator&gt;.assignmentMinus" and len(temp) == 2:
                    # &lt;operator&gt;.assignmentMinus,number -= 8
                    node.assign_minus_content = temp[1].strip()
                    node.assign_minus_left = node.assign_minus_content.split("-=")[0].strip()   # number
                    node.assign_minus_right = node.assign_minus_content.split("-=")[1].strip()  # 9
                elif node_type == "&lt;operator&gt;.assignmentMultiplication" and len(temp) == 2:
                    node.assign_multi_content = temp[1].strip()
                    node.assign_multi_left = node.assign_multi_content.split("*=")[0].strip()
                    node.assign_multi_right = node.assign_multi_content.split("*=")[1].strip()
                elif node_type == "&lt;operator&gt;.assignmentDivision" and len(temp) == 2:
                    node.assign_div_content = temp[1].strip()
                    node.assign_div_left = node.assign_div_content.split("/=")[0].strip()
                    node.assign_div_right = node.assign_div_content.split("/=")[1].strip()
                elif node_type == "&lt;operators&gt;.assignmentOr" and len(temp) == 2:
                    # &lt;operators&gt;.assignmentOr,result |= readUInt8(f)
                    node.assign_or_content = temp[1].strip()
                    node.assign_or_left = node.assign_or_content.split("|=")[0].strip() # result
                    node.assign_or_right = node.assign_or_content.split("|=")[1].strip()    # readUInt8(f)
                elif node_type == "&lt;operators&gt;.assignmentAnd" and len(temp) == 2:
                    # &lt;operators&gt;.assignmentAnd,demangle_flags &amp;= ~ DMGL_NO_RECURSE_LIMIT
                    node.assign_and_content = temp[1].strip()
                    node.assign_and_left = node.assign_and_content.split("&amp;=")[0].strip()
                    node.assign_and_right = node.assign_and_content.split("&amp;=")[1].strip()
                elif node_type == "&lt;operator&gt;.postDecrement" and len(temp) == 2:
                    # &lt;operator&gt;.postDecrement,argc--
                    node.post_decre_content = temp[1].strip()                   # argc--
                    node.post_decre_var = node.post_decre_content[:-2]          # argc
                elif node_type == "&lt;operator&gt;.postIncrement" and len(temp) == 2:
                    # &lt;operator&gt;.postIncrement,argv++
                    node.post_incre_content = temp[1].strip()                   # argv++
                    node.post_incre_var = node.post_incre_content[:-2]          # argv
                elif node_type == "&lt;operator&gt;.preDecrement" and len(temp) == 2:
                    node.pre_decre_content = temp[1].strip()
                    node.pre_decre_var = node.pre_decre_content[2:]
                elif node_type == "&lt;operator&gt;.preIncrement" and len(temp) == 2:
                    node.pre_incre_content = temp[1].strip()
                    node.pre_incre_var = node.pre_incre_content[2:]
                elif node_type == "&lt;operator&gt;.arithmeticShiftRight" and len(temp) == 2 \
                    or node_type == "&lt;operator&gt;.shiftRight" and len(temp) == 2:
                    # &lt;operator&gt;.arithmeticShiftRight,(__bsx) &gt;&gt; 8
                    node.arith_shift_right_content = temp[1].strip()            # (__bsx) &gt;&gt; 8
                    node.arith_shift_right_var = node.arith_shift_right_content.split("&gt;&gt;")[0].strip()    # (__bsx)
                    node.arith_shift_right_num = node.arith_shift_right_content.split("&gt;&gt;")[1].strip()    # 8
                elif node_type == "&lt;operator&gt;.arithmeticShiftLeft" and len(temp) == 2 \
                    or node_type == "&lt;operator&gt;.shiftLeft" and len(temp) == 2:
                    node.arith_shift_left_content = temp[1].strip()
                    node.arith_shift_left_var = node.arith_shift_left_content.split("&lt;&lt;")[0].strip()
                    node.arith_shift_left_num = node.arith_shift_left_content.split("&lt;&lt;")[1].strip()
                elif node_type == "&lt;operator&gt;.cast" and len(temp) == 2:
                    # &lt;operator&gt;.cast,(void *)method
                    node.cast_content = temp[1].strip()                         # temp[1].strip() 
                elif len(temp) == 2:
                    # SWFMovie_output,SWFMovie_output(movie, method, data)
                    node.custom = 1
                    node.function_name = temp[0].strip()
                    node.function_content = temp[1].strip()
                else:
                    # print("the unknown type")
                    # print(line)
                    # exit(-1)
                    pass
                    
                ast_g.node_set[node.num] = node
                
            # the edge information, eg: "406" -> "407" 
            elif line.find("->") != -1:
                start_node = int(line.split("->")[0].strip()[1:-1])
                end_node = int(line.split("->")[1].strip()[1:-1])

                # the two nodes of edge do not appear in the graph
                if not (start_node in ast_g.node_set.keys()) or not (end_node in ast_g.node_set.keys()):
                    print("start node or end node not in graph")
                    print(line)
                    exit(-1)
                
                # generate edge
                ast_g.edge_set[(start_node, end_node)] = (ast_g.node_set[start_node], ast_g.node_set[end_node])
                ast_g.node_set[start_node].children.append(ast_g.node_set[end_node])
                ast_g.node_set[end_node].parent.append(ast_g.node_set[start_node])
                ast_g.node_set[start_node].children_id.append(end_node)
                ast_g.node_set[end_node].parent_id.append(start_node)
        return ast_g


