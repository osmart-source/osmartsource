#!/usr/bin/python

import os
import subprocess
import sys

if True:
    AST_NODE_TYPE_NULL                      = 0x0
    AST_NODE_TYPE_METHOD                    = 0x1
    AST_NODE_TYPE_PARAM                     = 0x2
    AST_NODE_TYPE_BLOCK                     = 0x3
    AST_NODE_TYPE_LOCAL                     = 0x4
    AST_NODE_TYPE_IDENT                     = 0x5
    AST_NODE_TYPE_FIELD_IDENT               = 0x6
    AST_NODE_TYPE_CONTROL                   = 0x7
    AST_NODE_TYPE_LITERAL                   = 0x8
    AST_NODE_TYPE_JUMP_TARGET               = 0x9
    AST_NODE_TYPE_RETURN                    = 0xa
    AST_NODE_TYPE_METHOD_RETURN             = 0xb
                    
    AST_NODE_TYPE_UNKNOWN                   = 0xc


    AST_NODE_TYPE_OP_ASSGIN                 = 0x100
    AST_NODE_TYPE_OP_ADROF                  = 0x101
    AST_NODE_TYPE_OP_FIELDACCESS            = 0x102
    AST_NODE_TYPE_OP_INDFIELDACCESS         = 0x103
    AST_NODE_TYPE_OP_LOGICALNOT             = 0x104
    AST_NODE_TYPE_OP_LOGICALAND             = 0x105
    AST_NODE_TYPE_OP_LOGICALOR              = 0x106
    AST_NODE_TYPE_OP_INDINDEXACCESS         = 0x107
    AST_NODE_TYPE_OP_EQUAL                  = 0x108
    AST_NODE_TYPE_OP_NOTEQUAL               = 0x109
    AST_NODE_TYPE_OP_ARRAYINIT              = 0x10a
    AST_NODE_TYPE_OP_SUBTRACT               = 0x10b
    AST_NODE_TYPE_OP_LESSTHAN               = 0x10c
    AST_NODE_TYPE_OP_SIZEOF                 = 0x10d
    AST_NODE_TYPE_OP_IND                    = 0x10e
    AST_NODE_TYPE_OP_NOT                    = 0x10f
    AST_NODE_TYPE_OP_AND                    = 0x110
    AST_NODE_TYPE_OP_OR                     = 0x111
    AST_NODE_TYPE_OP_GREATERTHAN            = 0x112
    AST_NODE_TYPE_OP_GREATEREQTHAN          = 0x113
    AST_NODE_TYPE_OP_LESSEQTHAN             = 0x114
    AST_NODE_TYPE_OP_COND                   = 0x115
    AST_NODE_TYPE_OP_ADD                    = 0x116
    AST_NODE_TYPE_OP_PLUS                   = 0x117
    AST_NODE_TYPE_OP_MINUS                  = 0x118
    AST_NODE_TYPE_OP_MULTI                  = 0x119
    AST_NODE_TYPE_OP_DIV                    = 0x11a
    AST_NODE_TYPE_OP_MODULO                 = 0x11b
    AST_NODE_TYPE_OP_ASSGPLUS               = 0x11c
    AST_NODE_TYPE_OP_ASSGMINUS              = 0x11d
    AST_NODE_TYPE_OP_ASSGMULTI              = 0x11e
    AST_NODE_TYPE_OP_ASSGDIV                = 0x11f
    AST_NODE_TYPE_OP_ASSGOR                 = 0x120
    AST_NODE_TYPE_OP_POSTDEC                = 0x121
    AST_NODE_TYPE_OP_POSTINC                = 0x122
    AST_NODE_TYPE_OP_PREDEC                 = 0x123
    AST_NODE_TYPE_OP_PREINC                 = 0x124
    AST_NODE_TYPE_OP_ARITHSHIFTR            = 0x125
    AST_NODE_TYPE_OP_ARITHSHIFTL            = 0x126
    AST_NODE_TYPE_OP_SHIFTL                 = 0x127
    AST_NODE_TYPE_OP_SHIFTR                 = 0x128
    AST_NODE_TYPE_OP_CAST                   = 0x129

    AST_NODE_TYPE_REAL_METHOD               = 0x1000

def get_type(type_str):
    if type_str == 'METHOD':                #1
        return AST_NODE_TYPE_METHOD
    elif type_str == 'PARAM':               #2
        return AST_NODE_TYPE_PARAM
    elif type_str == 'BLOCK':               #3
        return AST_NODE_TYPE_BLOCK
    elif type_str == 'LOCAL':               #4
        return AST_NODE_TYPE_LOCAL
    elif type_str == 'IDENTIFIER':          #5
        return AST_NODE_TYPE_IDENT
    elif type_str == 'FIELD_IDENTIFIER':    #6
        return AST_NODE_TYPE_FIELD_IDENT    
    elif type_str == 'CONTROL_STRUCTURE':   #7
        return AST_NODE_TYPE_CONTROL        
    elif type_str == 'LITERAL':             #8
        return AST_NODE_TYPE_LITERAL 
    elif type_str == 'JUMP_TARGET':         #9
        return AST_NODE_TYPE_JUMP_TARGET    
    elif type_str == 'RETURN':              #A
        return AST_NODE_TYPE_RETURN        
    elif type_str == 'METHOD_RETURN':       #B
        return AST_NODE_TYPE_METHOD_RETURN
    elif type_str == 'UNKNOWN':             #C
        return AST_NODE_TYPE_UNKNOWN        
    elif type_str == '&lt;operator&gt;.assignment':
        return AST_NODE_TYPE_OP_ASSGIN        
    elif type_str == '&lt;operator&gt;.addressOf':
        return AST_NODE_TYPE_OP_ADROF
    elif type_str == '&lt;operator&gt;.fieldAccess':
        return AST_NODE_TYPE_OP_FIELDACCESS 
    elif type_str == '&lt;operator&gt;.indirectFieldAccess':
        return AST_NODE_TYPE_OP_INDFIELDACCESS  
    elif type_str == '&lt;operator&gt;.logicalNot':
        return AST_NODE_TYPE_OP_LOGICALNOT
    elif type_str == '&lt;operator&gt;.logicalAnd':
        return AST_NODE_TYPE_OP_LOGICALAND        
    elif type_str == '&lt;operator&gt;.logicalOr':
        return AST_NODE_TYPE_OP_LOGICALOR        
    elif type_str == '&lt;operator&gt;.indirectIndexAccess':
        return AST_NODE_TYPE_OP_INDINDEXACCESS
    elif type_str == '&lt;operator&gt;.equals':
        return AST_NODE_TYPE_OP_EQUAL
    elif type_str == '&lt;operator&gt;.notEquals':
        return AST_NODE_TYPE_OP_NOTEQUAL
    elif type_str == '&lt;operator&gt;.arrayInitializer':
        return AST_NODE_TYPE_OP_ARRAYINIT
    elif type_str == '&lt;operator&gt;.subtraction':
        return AST_NODE_TYPE_OP_SUBTRACT
    elif type_str == '&lt;operator&gt;.lessThan':
        return AST_NODE_TYPE_OP_LESSTHAN
    elif type_str == '&lt;operator&gt;.sizeOf':
        return AST_NODE_TYPE_OP_SIZEOF 
    elif type_str == '&lt;operator&gt;.indirection':
        return AST_NODE_TYPE_OP_IND 
    elif type_str == '&lt;operator&gt;.not':
        return AST_NODE_TYPE_OP_NOT
    elif type_str == '&lt;operator&gt;.and':
        return AST_NODE_TYPE_OP_AND
    elif type_str == '&lt;operator&gt;.or':
        return AST_NODE_TYPE_OP_OR
    elif type_str == '&lt;operator&gt;.greaterThan':
        return AST_NODE_TYPE_OP_GREATERTHAN
    elif type_str == '&lt;operator&gt;.greaterEqualsThan':
        return AST_NODE_TYPE_OP_GREATEREQTHAN
    elif type_str == '&lt;operator&gt;.lessEqualsThan':
        return AST_NODE_TYPE_OP_LESSEQTHAN  
    elif type_str == '&lt;operator&gt;.conditional':
        return AST_NODE_TYPE_OP_COND
    elif type_str == '&lt;operator&gt;.addition':
        return AST_NODE_TYPE_OP_ADD
    elif type_str == '&lt;operator&gt;.plus':
        return AST_NODE_TYPE_OP_PLUS
    elif type_str == '&lt;operator&gt;.minus':
        return AST_NODE_TYPE_OP_MINUS
    elif type_str == '&lt;operator&gt;.multiplication':
        return AST_NODE_TYPE_OP_MULTI
    elif type_str == '&lt;operator&gt;.division':
        return AST_NODE_TYPE_OP_DIV
    elif type_str == '&lt;operator&gt;.modulo':
        return AST_NODE_TYPE_OP_MODULO
    elif type_str == '&lt;operator&gt;.assignmentPlus':
        return AST_NODE_TYPE_OP_ASSGPLUS
    elif type_str == '&lt;operator&gt;.assignmentMinus':
        return AST_NODE_TYPE_OP_ASSGMINUS
    elif type_str == '&lt;operator&gt;.assignmentMultiplication':
        return AST_NODE_TYPE_OP_ASSGMULTI
    elif type_str == '&lt;operator&gt;.assignmentDivision':
        return AST_NODE_TYPE_OP_ASSGDIV
    elif type_str == '&lt;operators&gt;.assignmentOr':
        return AST_NODE_TYPE_OP_ASSGOR
    elif type_str == '&lt;operator&gt;.postDecrement':
        return AST_NODE_TYPE_OP_POSTDEC
    elif type_str == '&lt;operator&gt;.postIncrement':
        return AST_NODE_TYPE_OP_POSTINC
    elif type_str == '&lt;operator&gt;.preDecrement':
        return AST_NODE_TYPE_OP_PREDEC
    elif type_str == '&lt;operator&gt;.preIncrement':
        return AST_NODE_TYPE_OP_PREINC
    elif type_str == '&lt;operator&gt;.arithmeticShiftRight':
        return AST_NODE_TYPE_OP_ARITHSHIFTR
    elif type_str == '&lt;operator&gt;.arithmeticShiftLeft':
        return AST_NODE_TYPE_OP_ARITHSHIFTL
    elif type_str == '&lt;operator&gt;.shiftLeft':
        return AST_NODE_TYPE_OP_SHIFTL
    elif type_str == '&lt;operator&gt;.shiftRight':
        return AST_NODE_TYPE_OP_SHIFTR
    elif type_str == '&lt;operator&gt;.cast':
        return AST_NODE_TYPE_OP_CAST
    else:
        return AST_NODE_TYPE_REAL_METHOD

class AST_Node:
    num     = -1
    type    = AST_NODE_TYPE_NULL
    type_str= ''
    src     = ''
    dot_src = ''
    line    = -1
    # method
    method_name = ''
    # param
    param_type = ''
    param_name = ''
    # method_return
    return_type = ''
    # local
    local_type = ''
    local_content = ''
    # identifier
    ide_var = ''
    ide_content = ''
    # field identifier
    fide_left = ''
    fide_right = ''
    # block
    block_left = ''
    block_right = ''
    # control_structure
    cst_left = ''
    cst_left_type = ''
    cst_right = ''
    cst_right_type = ''
    # literal
    lit_content = ''
    lit_var = ''
    # jump target
    jt_content = ''
    # return
    return_left = ''
    return_right = ''
    # method return 
    rt_type = ''
    # unkown
    unknown_left = ''
    unknown_right = ''
    # &lt;operator&gt;.assignment
    assign_content = ''
    assign_var = ''
    # &lt;operator&gt;.addressOf
    addressof_content = ''
    addressof_var = ''
    # &lt;operator&gt;.fieldAccess
    field_access_content = ''
    # &lt;operator&gt;.indirectFieldAccess
    infa_content = ''
    infa_var = ''
    # &lt;operator&gt;.logicalNot
    logic_not_content = ''
    # &lt;operator&gt;.logicalAnd
    and_content = ''
    and_list = []
    # &lt;operator&gt;.logicalOr
    or_content = ''
    or_list = []
    # &lt;operator&gt;.indirectIndexAccess
    indirect_ia_content = ''
    indirect_ia_index = ''
    indirect_ia_array = ''
    # &lt;operator&gt;.equals
    equal_content = ''
    equal_list = []
    # &lt;operator&gt;.notEquals
    notequal_content = ''
    notequal_list = []
    # &lt;operator&gt;.arrayInitializer
    arrayInit_content = ''
    # &lt;operator&gt;.subtraction
    subtraction_content = ''
    subtraction_left = ''
    subtraction_right = ''
    # &lt;operator&gt;.lessThan
    less_than_content = ''
    less_than_left = ''
    less_than_right = ''
    # &lt;operator&gt;.sizeOf
    sizeOf_content = ''
    sizeOf_var = ''
    # &lt;operator&gt;.indirection
    indirect_content = ''
    # &lt;operator&gt;.not
    not_content = ''
    not_var = ''
    # &lt;operator&gt;.and
    and_content = ''
    and_left = ''
    and_right = ''
    # &lt;operator&gt;.greaterThan
    gt_content = ''
    gt_left = ''
    gt_right = ''
    # &lt;operator&gt;.greaterEqualsThan
    get_content = ''
    get_left = ''
    get_right = ''
    # &lt;operator&gt;.conditional
    cond_content = ''
    cond_cond = ''
    cond_true = ''
    cond_false = ''
    # &lt;operator&gt;.minus
    minus_content = ''
    minus_var = ''
    # &lt;operator&gt;.multiplication
    multi_content = ''
    multi_left = ''
    multi_right = ''
    # &lt;operator&gt;.assignmentMinus
    assign_minus_content = ''
    assign_minus_left = ''
    assign_minus_right = ''
    # &lt;operators&gt;.assignmentOr
    assign_or_content = ''
    assign_or_left = ''
    assign_or_right = ''
    # &lt;operator&gt;.postDecrement
    post_decre_content = ''
    post_decre_var = ''
    # &lt;operator&gt;.postIncrement
    post_incre_content = ''
    post_incre_var = ''
    # &lt;operator&gt;.arithmeticShiftRight
    arith_shift_right_content = ''
    arith_shift_right_var = ''
    arith_shift_right_num = ''
    # &lt;operator&gt;.cast
    cast_content = ''
    # else
    function_name = ''
    function_content = ''
    def __init__(self, mytype=AST_NODE_TYPE_NULL):
        self.type = mytype
        self.children = []
        self.parent = []
        self.children_id = []
        self.parent_id = []
        self.var_str = ''

class AST_Graph:
    name = 'unknown'

    def __init__(self, name):
        self.name = name
        self.node_set = {}
        self.edge_set = {}

    def set_name(self, name):
        self.name = name
    def get_name(self):
        return self.name
