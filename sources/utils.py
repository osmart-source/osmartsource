import os
import string
import sys
from pickle import FALSE
import numpy as np
sys.path.append("..")
import ast_utils

# from cfg import flowgenerate


# generate the <style> dot of <indir> and store to the <outdir>
def generate_dot(indir, outdir, style):
    os.system("joern-parse {}".format(indir))
    os.system("joern-export  --repr {} --out {}".format(style, outdir))

# get all the C files in the <total_dir>
def get_c_path(total_dir):
    file_path_list = []
    for root, dirs, files in os.walk(total_dir):
        for name in files:
            # print(os.path.join(root, name))
            if name.endswith(".c"):
                temp_file_path = os.path.join(root, name)
                # print(temp_file_path)
                file_path_list.append(temp_file_path)
    return file_path_list

# get all the dot files in the <total_dir>
def get_dot_path(total_dir):
    file_path_list = []
    for root, dirs, files in os.walk(total_dir):
        for name in files:
            # print(os.path.join(root, name))
            if name.endswith(".dot"):
                temp_file_path = os.path.join(root, name)
                # print(temp_file_path)
                file_path_list.append(temp_file_path)
    return file_path_list

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

def get_method_file(method_name: string, file_path: string):
    file_path_list = []
    file_path_list = get_dot_path(file_path)
    res_list = []
    for fp in file_path_list:
        with open(fp, "r") as f:
            res = ""
            type_list = []
            while True:
                line = f.readline().strip()
                if line == "":
                    break
                if line[:7] == "digraph":
                    if method_name == line.split()[1][1:-1].strip():
                        res = fp.split("/")[-1].split("-")[0]
                elif line.find("label") != -1:
                    type_list.append(line.split('<')[1][1:-1].strip().split(',')[0].strip())
            if res != "":
                for type in type_list:
                    if type != "METHOD" and type != "PARAM" and type != "METHOD_RETURN":
                        res_list.append(res)
                        break
    return res_list
    
def get_global(file_path: string):
    global_variable_list = []
    custom_function_list = []
    with open(file_path, "r") as f:
        while True:
            line = f.readline().strip()
            if line == "":
                break
            if line[:21] == "globalvariables are: ":
                global_variable_list.extend(line[21:].split())
            elif line[:15] == "functions are: ":
                custom_function_list.extend(line[15:].split())
    return global_variable_list, custom_function_list

# split str
def extract_string(input_string: string):
    res_list = []
    temp_string = ""
    for index in range(len(input_string)):
        if input_string[index] >= 'a' and input_string[index] <= 'z' or\
             input_string[index] >= 'A' and input_string[index] <= 'Z' or\
                 input_string[index] >= '0' and input_string[index] <= '9' or\
                    input_string[index] == '_' or input_string[index] == '-'or\
                        input_string[index] == '&' or input_string[index] == ';':
                    temp_string += input_string[index]
        else:
            if temp_string != "":
                res_list.append(temp_string)
                temp_string = ""
    if temp_string != "":
        res_list.append(temp_string)
    return res_list
#  579 php/phpdbg/phpdbg-ast/6143-ast.dot 0
# 237 jasper/jasper/jasper-ast/424-ast.dot 0
# get source and dest operands
def get_source_dest(line: int, dot_name: string, interval: int):
    g = ast_utils.generate_graph(dot_name)
    line_list = []
    for i in range(interval + 1):
        line_list.append(line + i)
    source_list = []
    dest_list = []
    function_list = []
    for node_id in g.node_set:
        node = g.node_set[node_id]
        if node.line in line_list:
            if node.type_str == "IDENTIFIER":
                node_parent = node.parent[0]
                while node_parent.line in line_list:
                    if node_parent.custom == 1:
                        if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                            source_list.append(node.parent[0].infa_content)
                        elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                            source_list.append(node.parent[0].field_access_content)
                        else:
                            source_list.append(node.ide_var)
                        function_list.append(node_parent.function_name)
                    elif node_parent.type_str == "&lt;operator&gt;.assignment":
                        equal_list = node_parent.assign_content.split('=')
                        if len(equal_list) < 2:
                            break
                        if "-&gt;" in equal_list[0].strip():
                            if node.ide_var in equal_list[0].strip().split("-&gt;")[0]:
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    dest_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    dest_list.append(node.parent[0].field_access_content)
                                else:
                                    dest_list.append(node.ide_var)
                        else:
                            if node.ide_var in equal_list[0].strip().split(".")[0]:
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    dest_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    dest_list.append(node.parent[0].field_access_content)
                                else:
                                    dest_list.append(node.ide_var)
                        if "-&gt;" in equal_list[1].strip():
                            if node.ide_var in equal_list[1].strip().split("-&gt;")[0]:
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    source_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    source_list.append(node.parent[0].field_access_content)
                                else:
                                    source_list.append(node.ide_var)
                        else:
                            if node.ide_var in equal_list[1].strip().split(".")[0]:
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    source_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    source_list.append(node.parent[0].field_access_content)
                                else:
                                    source_list.append(node.ide_var)
                    elif node_parent.type_str == "&lt;operator&gt;.postIncrement":
                        if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                            dest_list.append(node.parent[0].infa_content)
                        elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                            dest_list.append(node.parent[0].field_access_content)
                        else:
                            dest_list.append(node.ide_var)
                        if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                            source_list.append(node.parent[0].infa_content)
                        elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                            source_list.append(node.parent[0].field_access_content)
                        else:
                            source_list.append(node.ide_var)
                    elif node_parent.type_str == "&lt;operator&gt;.postDecrement":
                        if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                            dest_list.append(node.parent[0].infa_content)
                        elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                            dest_list.append(node.parent[0].field_access_content)
                        else:
                            dest_list.append(node.ide_var)
                        if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                            source_list.append(node.parent[0].infa_content)
                        elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                            source_list.append(node.parent[0].field_access_content)
                        else:
                            source_list.append(node.ide_var)
                    elif node_parent.type_str == "&lt;operator&gt;.preDecrement":
                        if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                            dest_list.append(node.parent[0].infa_content)
                        elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                            dest_list.append(node.parent[0].field_access_content)
                        else:
                            dest_list.append(node.ide_var)
                        if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                            source_list.append(node.parent[0].infa_content)
                        elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                            source_list.append(node.parent[0].field_access_content)
                        else:
                            source_list.append(node.ide_var)
                    elif node_parent.type_str == "&lt;operator&gt;.preIncrement":
                        if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                            dest_list.append(node.parent[0].infa_content)
                        elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                            dest_list.append(node.parent[0].field_access_content)
                        else:
                            dest_list.append(node.ide_var)
                        if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                            source_list.append(node.parent[0].infa_content)
                        elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                            source_list.append(node.parent[0].field_access_content)
                        else:
                            source_list.append(node.ide_var)
                    elif node_parent.type_str == "&lt;operator&gt;.assignmentPlus":
                        if "-&gt;" in node_parent.assign_plus_left:
                            if node.ide_var in node_parent.assign_plus_left.split("-&gt;")[0]:
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    dest_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    dest_list.append(node.parent[0].field_access_content)
                                else:
                                    dest_list.append(node.ide_var)
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    source_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    source_list.append(node.parent[0].field_access_content)
                                else:
                                    source_list.append(node.ide_var)
                        else:
                            if node.ide_var in node_parent.assign_plus_left.split(".")[0]:
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    dest_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    dest_list.append(node.parent[0].field_access_content)
                                else:
                                    dest_list.append(node.ide_var)
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    source_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    source_list.append(node.parent[0].field_access_content)
                                else:
                                    source_list.append(node.ide_var)
                        if "-&gt;" in node_parent.assign_plus_right:
                            if node.ide_var in node_parent.assign_plus_right.split("-&gt;")[0]:
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    source_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    source_list.append(node.parent[0].field_access_content)
                                else:
                                    source_list.append(node.ide_var)
                        else:
                            if node.ide_var in node_parent.assign_plus_right.split(".")[0]:
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    source_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    source_list.append(node.parent[0].field_access_content)
                                else:
                                    source_list.append(node.ide_var)
                    elif node_parent.type_str == "&lt;operator&gt;.assignmentMultiplication":
                        if "-&gt;" in node_parent.assign_multi_left:
                            if node.ide_var in node_parent.assign_multi_left.split("-&gt;")[0]:
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    dest_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    dest_list.append(node.parent[0].field_access_content)
                                else:
                                    dest_list.append(node.ide_var)
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    source_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    source_list.append(node.parent[0].field_access_content)
                                else:
                                    source_list.append(node.ide_var)
                        else:
                            if node.ide_var in node_parent.assign_multi_left.split(".")[0]:
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    dest_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    dest_list.append(node.parent[0].field_access_content)
                                else:
                                    dest_list.append(node.ide_var)
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    source_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    source_list.append(node.parent[0].field_access_content)
                                else:
                                    source_list.append(node.ide_var)
                        if "-&gt;" in node_parent.assign_multi_right:
                            if node.ide_var in node_parent.assign_multi_right.split("-&gt;")[0]:
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    source_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    source_list.append(node.parent[0].field_access_content)
                                else:
                                    source_list.append(node.ide_var)
                        else:
                            if node.ide_var in node_parent.assign_multi_right.split(".")[0]:
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    source_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    source_list.append(node.parent[0].field_access_content)
                                else:
                                    source_list.append(node.ide_var)
                    elif node_parent.type_str == "&lt;operator&gt;.assignmentDivision":
                        if "-&gt;" in node_parent.assign_div_left:
                            if node.ide_var in node_parent.assign_div_left.split("-&gt;")[0]:
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    dest_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    dest_list.append(node.parent[0].field_access_content)
                                else:
                                    dest_list.append(node.ide_var)
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    source_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    source_list.append(node.parent[0].field_access_content)
                                else:
                                    source_list.append(node.ide_var)
                        else:
                            if node.ide_var in node_parent.assign_div_left.split(".")[0]:
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    dest_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    dest_list.append(node.parent[0].field_access_content)
                                else:
                                    dest_list.append(node.ide_var)
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    source_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    source_list.append(node.parent[0].field_access_content)
                                else:
                                    source_list.append(node.ide_var)
                        if "-&gt;" in node_parent.assign_div_right:
                            if node.ide_var in node_parent.assign_div_right.split("-&gt;")[0]:
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    source_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    source_list.append(node.parent[0].field_access_content)
                                else:
                                    source_list.append(node.ide_var)
                        else:
                            if node.ide_var in node_parent.assign_div_right.split(".")[0]:
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    source_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    source_list.append(node.parent[0].field_access_content)
                                else:
                                    source_list.append(node.ide_var)
                    elif node_parent.type_str == "&lt;operator&gt;.assignmentOr":
                        if "-&gt;" in node_parent.assign_or_left:
                            if node.ide_var in node_parent.assign_or_left.split("-&gt;")[0]:
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    dest_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    dest_list.append(node.parent[0].field_access_content)
                                else:
                                    dest_list.append(node.ide_var)
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    source_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    source_list.append(node.parent[0].field_access_content)
                                else:
                                    source_list.append(node.ide_var)
                        else:
                            if node.ide_var in node_parent.assign_or_left.split(".")[0]:
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    dest_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    dest_list.append(node.parent[0].field_access_content)
                                else:
                                    dest_list.append(node.ide_var)
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    source_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    source_list.append(node.parent[0].field_access_content)
                                else:
                                    source_list.append(node.ide_var)
                        if "-&gt;" in node_parent.assign_or_right:
                            if node.ide_var in node_parent.assign_or_right.split("-&gt;")[0]:
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    source_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    source_list.append(node.parent[0].field_access_content)
                                else:
                                    source_list.append(node.ide_var)
                        else:
                            if node.ide_var in node_parent.assign_or_right.split(".")[0]:
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    source_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    source_list.append(node.parent[0].field_access_content)
                                else:
                                    source_list.append(node.ide_var)
                    elif node_parent.type_str == "&lt;operator&gt;.assignmentMinus":
                        if "-&gt;" in node_parent.assign_minus_left:
                            if node.ide_var in node_parent.assign_minus_left.split("-&gt;")[0]:
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    dest_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    dest_list.append(node.parent[0].field_access_content)
                                else:
                                    dest_list.append(node.ide_var)
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    source_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    source_list.append(node.parent[0].field_access_content)
                                else:
                                    source_list.append(node.ide_var)
                        else:
                            if node.ide_var in node_parent.assign_minus_left.split(".")[0]:
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    dest_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    dest_list.append(node.parent[0].field_access_content)
                                else:
                                    dest_list.append(node.ide_var)
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    source_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    source_list.append(node.parent[0].field_access_content)
                                else:
                                    source_list.append(node.ide_var)
                        if "-&gt;" in node_parent.assign_minus_right:
                            if node.ide_var in node_parent.assign_minus_right.split("-&gt;")[0]:
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    source_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    source_list.append(node.parent[0].field_access_content)
                                else:
                                    source_list.append(node.ide_var)
                        else:
                            if node.ide_var in node_parent.assign_minus_right.split(".")[0]:
                                if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                    source_list.append(node.parent[0].infa_content)
                                elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                    source_list.append(node.parent[0].field_access_content)
                                else:
                                    source_list.append(node.ide_var)
                    if node_parent.parent == []:
                        break
                    node_parent = node_parent.parent[0]
    return source_list, dest_list, function_list


def get_function_information(line: int, dot_name: string, interval: int):
    g = ast_utils.generate_graph(dot_name)
    line_list = []
    for i in range(interval + 1):
        line_list.append(line + i)
    function_dict = {}
    for node_id in g.node_set:
        node = g.node_set[node_id]
        if node.line in line_list:
            if node.custom == 1 and node.children != [] and node.children[0].type_str != "BLOCK"\
                or node.custom == 1 and node.children == []:
                function_dict[node.function_name] = []
                for child in node.children:
                    if child.type_str == "IDENTIFIER":
                        function_dict[node.function_name].append(child.ide_var)
                    elif child.type_str == "FIELD_IDENTIFIER":
                        function_dict[node.function_name].append(child.fide_left)
                    elif child.type_str == "LITERAL":
                        function_dict[node.function_name].append(child.lit_var)
                    elif child.type_str == "&lt;operator&gt;.addressOf":
                        function_dict[node.function_name].append(child.addressof_content)
                    elif child.type_str == "&lt;operator&gt;.fieldAccess":
                        function_dict[node.function_name].append(child.field_access_content)     
                    elif child.type_str == "&lt;operator&gt;.indirectFieldAccess":
                        function_dict[node.function_name].append(child.infa_content)     
                    elif child.type_str == "&lt;operator&gt;.logicalNot":
                        function_dict[node.function_name].append(child.logic_not_content)     
                    elif child.type_str == "&lt;operator&gt;.indirectIndexAccess":
                        function_dict[node.function_name].append(child.indirect_ia_content)     
                    elif child.type_str == "&lt;operator&gt;.subtraction":
                        function_dict[node.function_name].append(child.subtraction_content)     
                    elif child.type_str == "&lt;operator&gt;.sizeOf":
                        function_dict[node.function_name].append(child.sizeOf_content)     
                    elif child.type_str == "&lt;operator&gt;.indirection":
                        function_dict[node.function_name].append(child.indirect_content)     
                    elif child.type_str == "&lt;operator&gt;.not":
                        function_dict[node.function_name].append(child.not_content)     
                    elif child.type_str == "&lt;operator&gt;.and":
                        function_dict[node.function_name].append(child.and_content)     
                    elif child.type_str == "&lt;operator&gt;.or":
                        function_dict[node.function_name].append(child.or_content)     
                    elif child.type_str == "&lt;operator&gt;.conditional":
                        function_dict[node.function_name].append(child.cond_content)     
                    elif child.type_str == "&lt;operator&gt;.addition":
                        function_dict[node.function_name].append(child.add_content)     
                    elif child.type_str == "&lt;operator&gt;.plus":
                        function_dict[node.function_name].append(child.plus_content)     
                    elif child.type_str == "&lt;operator&gt;.minus":
                        function_dict[node.function_name].append(child.minus_content)     
                    elif child.type_str == "&lt;operator&gt;.multiplication":
                        function_dict[node.function_name].append(child.multi_content)     
                    elif child.type_str == "&lt;operator&gt;.division":
                        function_dict[node.function_name].append(child.div_content)     
                    elif child.type_str == "&lt;operator&gt;.modulo":
                        function_dict[node.function_name].append(child.modulo_content)     
                    elif child.type_str == "&lt;operator&gt;.postDecrement":
                        function_dict[node.function_name].append(child.post_decre_content)     
                    elif child.type_str == "&lt;operator&gt;.postIncrement":
                        function_dict[node.function_name].append(child.post_incre_content)     
                    elif child.type_str == "&lt;operator&gt;.preDecrement":
                        function_dict[node.function_name].append(child.pre_decre_content)     
                    elif child.type_str == "&lt;operator&gt;.preIncrement":
                        function_dict[node.function_name].append(child.pre_incre_content)     
                    elif child.type_str == "&lt;operator&gt;.arithmeticShiftRight":
                        function_dict[node.function_name].append(child.arith_shift_right_content)     
                    elif child.type_str == "&lt;operator&gt;.shiftRight":
                        function_dict[node.function_name].append(child.arith_shift_right_content)     
                    elif child.type_str == "&lt;operator&gt;.arithmeticShiftLeft":
                        function_dict[node.function_name].append(child.arith_shift_left_content)            
                    elif child.type_str == "&lt;operator&gt;.shiftLeft":
                        function_dict[node.function_name].append(child.arith_shift_left_content)       
                    elif child.type_str == "&lt;operator&gt;.cast":
                        function_dict[node.function_name].append(child.cast_content)
                    elif child.custom == 1:
                        function_dict[node.function_name].append(child.function_content)
    return function_dict


def get_or_information(line: int, dot_name: string, interval: int, specific_id = -1):
    g = ast_utils.generate_graph(dot_name)
    line_list = []
    for i in range(interval + 1):
        line_list.append(line + i)
    or_list = []
    or_flag = False
    for node_id in g.node_set:
        if specific_id != -1 and node_id < specific_id:
            continue
        node = g.node_set[node_id]
        parent_flag = False
        temp_node = node
        if specific_id != -1:
            while len(temp_node.parent) > 0:
                if g.node_set[specific_id] == temp_node:
                    parent_flag = True
                    break
                temp_node = temp_node.parent[0]
        if node.line in line_list and (specific_id == -1 or parent_flag == True):
            if node.type_str == "&lt;operator&gt;.logicalOr":
                or_flag = True
                if node.children == []:
                    return or_list
                or_left = node.children[0]
                if or_left.type_str != "&lt;operator&gt;.logicalOr":
                    left_list = []
                    stack = [or_left]
                    while stack:
                        tNode = stack.pop()
                        if tNode.type_str == "IDENTIFIER" and tNode.line in line_list and tNode.ide_var not in left_list:
                            if tNode.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                left_list.append(tNode.parent[0].infa_content)
                            elif tNode.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                left_list.append(tNode.parent[0].field_access_content)
                            else:
                                left_list.append(tNode.ide_var)
                        for child in tNode.children:
                            stack.append(child)
                    or_list.append(left_list)
                or_right = node.children[1]
                if or_right.type_str != "&lt;operator&gt;.logicalOr":
                    right_list = []
                    stack = [or_right]
                    while stack:
                        tNode = stack.pop()
                        if tNode.type_str == "IDENTIFIER" and tNode.line in line_list and tNode.ide_var not in right_list:
                            if tNode.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                                right_list.append(tNode.parent[0].infa_content)
                            elif tNode.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                                right_list.append(tNode.parent[0].field_access_content)
                            else:
                                right_list.append(tNode.ide_var)
                        for child in tNode.children:
                            stack.append(child)
                    or_list.append(right_list)
    if or_flag == False:
        for node_id in g.node_set:
            node = g.node_set[node_id]
            parent_flag = False
            temp_node = node
            if specific_id != -1:
                while len(temp_node.parent) > 0:
                    if g.node_set[specific_id] == temp_node:
                        parent_flag = True
                        break
                    temp_node = temp_node.parent[0]
            if node.line in line_list and (specific_id == -1 or parent_flag == True):
                if node.type_str == "IDENTIFIER" and node.line in line_list and node.ide_var not in or_list:
                    if node.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                        or_list.append(node.parent[0].infa_content)
                    elif node.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                        or_list.append(node.parent[0].field_access_content)
                    else:
                        or_list.append(node.ide_var)
    return or_list
    
#     return and_list
def get_and_information(line: int, dot_name: string, interval:int):
    g = ast_utils.generate_graph(dot_name)
    line_list = []
    for i in range(interval + 1):
        line_list.append(line + i)
    and_list = []
    and_flag = False
    for node_id in g.node_set:
        node = g.node_set[node_id]
        if node.line in line_list:
            if node.type_str == "&lt;operator&gt;.logicalAnd":
                and_flag = True
                # print(node.children_id)
                if node.children == []:
                    return and_list
                left = g.node_set[node.children_id[0]]
                left_flag = True
                right = g.node_set[node.children_id[1]]
                right_flag = True
                left_list = get_or_information(line, dot_name, interval, node.children_id[0])
                right_list = get_or_information(line, dot_name, interval, node.children_id[1])
                if left.type_str == "&lt;operator&gt;.logicalOr":
                    left_flag = True
                else:
                    left_flag = False
                if right.type_str == "&lt;operator&gt;.logicalOr":
                    right_flag = True
                else:
                    right_flag = False
                if left_flag == False and right_flag == False:
                    and_list.extend(left_list)
                    and_list.extend(right_list)
                elif left_flag == True and right_flag == False:
                    for item in left_list:
                        temp_list = []
                        temp_list.extend(item)
                        temp_list.extend(right_list)
                        and_list.append(temp_list)
                elif left_flag == False and right_flag == True:
                    for item in right_list:
                        temp_list = []
                        temp_list.extend(item)
                        temp_list.extend(left_list)
                        and_list.append(temp_list)
                else:
                    for item_left in left_list:
                        for item_right in right_list:
                            temp_list = []
                            temp_list.extend(item_left)
                            temp_list.extend(item_right)
                            and_list.append(temp_list) 
                break
                 
    if and_flag == False:
        and_list = get_or_information(line, dot_name, interval)
 
    if and_list == [] or type(and_list[0]) == str:
        temp_list = []
        temp_list.append(and_list)
        and_list = temp_list

    for i in range(len(and_list)):
        for j in range(len(and_list[i])):
            if type(and_list[i][j]) == list and len(and_list[i][j]) >= 1:
                and_list[i][j] = and_list[i][j][0]
        
    return and_list


def get_control_information(line: int, dot_name: string, interval: int):
    iscontrol = False
    g = ast_utils.generate_graph(dot_name)
    line_list = []
    for i in range(interval + 1):
        line_list.append(line + i)
    var_list = []
    for node_id in g.node_set:
        node = g.node_set[node_id]
        if node.line in line_list:
            if node.type_str == "CONTROL_STRUCTURE":
                iscontrol = True
                if node.children == []:
                    return var_list, iscontrol
                if node.cst_left_type == 'for':
                    stack = [node.children[1]]
                else:
                    stack = [node.children[0]]
                while stack:
                    tNode = stack.pop()
                    if tNode.type_str == "IDENTIFIER" and tNode.line in line_list and tNode.ide_var not in var_list:
                        if tNode.parent[0].type_str == "&lt;operator&gt;.indirectFieldAccess":
                            var_list.append(tNode.parent[0].infa_content)
                        elif tNode.parent[0].type_str == "&lt;operator&gt;.fieldAccess":
                            var_list.append(tNode.parent[0].field_access_content)
                        else:
                            var_list.append(tNode.ide_var)
                    for child in tNode.children:
                        stack.append(child)
    return var_list, iscontrol
            

def get_for_information(line: int, dot_name: string, interval: int):
    g = ast_utils.generate_graph(dot_name)
    line_list = []
    for i in range(interval + 1):
        line_list.append(line + i)
    init_str = ""
    loop_str = ""
    change_str = ""
    for node_id in g.node_set:
        node = g.node_set[node_id]
        if node.line in line_list:
            if node.type_str == "CONTROL_STRUCTURE":
                if node.cst_left_type == "for":
                    # node.children[0]  
                    if len(node.children) > 0 and len(node.children[0].children) != 0:
                        temp = split_line(node.children[0].children[0].dot_src.split('<')[1][1:-1].strip())
                        init_str = temp[1].strip()
                    # node.children[1]  
                    if len(node.children) > 1 and len(node.children[1].children) != 0:
                        temp = split_line(node.children[1].dot_src.split('<')[1][1:-1].strip())
                        loop_str = temp[1].strip()
          
                    if len(node.children) > 2 and len(node.children[2].children) != 0:
                        temp = split_line(node.children[2].dot_src.split('<')[1][1:-1].strip())
                        change_str = temp[1].strip()
    return init_str, loop_str, change_str

def find_method_global(method_name: string, path):
    global_list = []
    global_variable_list, custom_function_list = get_global('/'.join(path.split('/')[:-1]) + "/" + "global.txt")
    ast_path = path
    method_list = get_method_file(method_name, ast_path)
    for method_path in method_list:
        method_path = ast_path + '/' + method_path + "-ast.dot"
        # print(method_path)
        g = ast_utils.generate_graph(method_path)
        for node_id in g.node_set:
            node = g.node_set[node_id]
            if node.type_str == "&lt;operator&gt;.assignment":
                if len(node.assign_content.split("=")) > 1\
                    and node.assign_content.split("=")[1].strip().find("optarg") == -1\
                    and node.assign_content.split("=")[1].strip().find("argv") == -1:
                    global_list.append(node.assign_var)
            elif node.type_str == "&lt;operator&gt;.postDecrement":
                global_list.append(node.post_decre_var)
            elif node.type_str == "&lt;operator&gt;.postIncrement":
                global_list.append(node.post_incre_var)
            elif node.type_str == "&lt;operator&gt;.preDecrement":
                global_list.append(node.pre_decre_var)
            elif node.type_str == "&lt;operator&gt;.preIncrement":
                global_list.append(node.pre_incre_var)
            elif node.type_str == "&lt;operator&gt;.assignmentPlus":
                global_list.append(node.assign_plus_left)
            elif node.type_str == "&lt;operator&gt;.assignmentMinus":
                global_list.append(node.assign_minus_left)
            elif node.type_str == "&lt;operator&gt;.assignmentMultiplication":
                global_list.append(node.assign_multi_left)
            elif node.type_str == "&lt;operator&gt;.assignmentDivision":
                global_list.append(node.assign_div_left)
            elif node.type_str == "&lt;operators&gt;.assignmentOr":
                global_list.append(node.assign_or_left)
    res_list = []
    for var in global_list:
        if var  in global_variable_list:
            res_list.append(var)
    return res_list

def get_return(line: int, dot_name: string, interval: int):
    g = ast_utils.generate_graph(dot_name)
    line_list = []
    for i in range(interval + 1):
        line_list.append(line + i)
    for node_id in g.node_set:
        node = g.node_set[node_id]
        if node.line in line_list:
            if node.type_str == "RETURN":
                if len(node.return_left.split()) < 2 or node.return_left.split()[1] == ";":
                    return ""
                else:
                    return node.return_left.split()[1][:-1]
    return FALSE


src_list, dest_list, func_list = get_source_dest(456, "/home/cmd/OSmart/identitemp/libtiff/tiff2ps/tiff2ps-ast/714-ast.dot", 2)
print(src_list, dest_list, func_list)

funcinfo = get_function_information(456, "/home/cmd/OSmart/identitemp/libtiff/tiff2ps/tiff2ps-ast/714-ast.dot", 2)
print(funcinfo)


