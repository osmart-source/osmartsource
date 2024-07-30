import json
import os
import sys

from ast_graph import *
from ast_utils import *
from utils import *
from impactanalysis import inter_spread

parse_func_dict = {
    "ar": ["decode_options"],
    "as": ["parse_args"],
    "xmlwf": ["tmain"],
    "gdb": ["captured_main_1"],
    "gprof": ["main"],
    "objdump": ["main"],
    "readelf": ["parse_args"],
    "size": ["main"],
    "fax2ps": ["main"],
    "fax2tiff": ["main"],
    "tiff2ps": ["main"],
    "tiff2rgba": ["main"],
    "tiffcp": ["main"],
    "tiffcrop": ["process_command_opts"],
    "tiffinfo": ["main"],
    "scp": ["main"],
    "sftp": ["main"],
    "ssh": ["main"],
    "ssh-agent": ["main"],
    "ssh-keygen": ["main"],
    "ssh-keyscan": ["main"],
    "ab": ["main"],
    "htcacheclean": ["main"],
    "htdbm": ["main"],
    # "htpasswd": ["parse_common_options", "check_args"],
    "htpasswd": ["parse_common_options"],
    "httpd": ["main"],
    "mupdf-x11": ["main"],
    "muraster": ["main"],
    "mutool-clean": ["pdfclean_main"],
    "mutool-convert": ["muconvert_main"],
    "mutool-draw": ["mudraw_main"],
    "imgcmp": ["main"],
    "imginfo": ["main"],
    "jasper": ["cmdopts_parse"],
    "cjpeg": ["parse_switches"],
    "jpegtran": ["parse_switches"],
    "tjbench": ["main"],
    "qemu-edid": ["main"],
    "qemu-img-bench": ["img_bench"],
    "qemu-img-convert": ["img_convert"],
    "qemu-img-dd": ["img_dd"],
    "qemu-img-measure": ["img_measure"],
    "qemu-nbd": ["main"],
    "catdoc": ["main"],
    "xls2csv": ["main"],
    "bsdcpio": ["main"],
    "bsdtar": ["main"],
    "xmlcatalog": ["main"],
    "xmllint": ["main"],
    "nasm": ["process_arg"],
    "ndisasm": ["main"],
    "s2nc": ["main"],
    "s2nd": ["main"],
    # "php": ["do_cli", "do_cli"],
    "php": ["do_cli"],
    "phpdbg": ["main"],
    "bison": ["getargs"],
    "gifsicle": ["main"],
    # "imagew": ["process_option_name", "process_option_arg"],
    "imagew": ["process_option_arg"],
    "jbig2dec": ["parse_options"],
    "jhead": ["main"],
    "dwarfdump": ["set_command_options"],
    "dwarfdump-conf": ["parse_abi"],
    "makeswf": ["main"],
    "pngfix": ["main"],
    "img2sixel": ["sixel_encoder_setopt"],
    "nginx": ["ngx_get_options"],
    "sngrep": ["main"],
    "sngrep-conf": ["read_options"],
    "sqlite3": ["main"],
    "w3m": ["main"],
    "outparamtest":["main"]
}

parse_start_dict = {
    "ar": [500],
    "as": [609],
    "gdb": [830],
    "gprof": [204],
    "objdump": [5571],
    "readelf": [5426],
    "size": [154],
    "fax2ps": [352],
    "fax2tiff": [110],
    "tiff2ps": [284],
    "tiff2rgba": [78],
    "tiffcp": [224],
    "tiffcrop": [1854],
    "tiffinfo": [85],
    "scp": [482],
    "sftp": [2451],
    "ssh": [706],
    "ssh-agent": [2039],
    "ssh-keygen": [3358],
    "ssh-keyscan": [692],
    "ab": [2358],
    "htcacheclean": [1440],
    "htdbm": [340],
    # "htpasswd": [284, 181],
    "htpasswd": [284],
    "httpd": [549],
    "mupdf-x11": [910],
    "muraster": [1479],
    "mutool-clean": [92],
    "mutool-convert": [133],
    "mutool-draw": [1934],
    "imgcmp": [217],
    "imginfo": [179],
    "jasper": [476],
    "cjpeg": [296],
    "jpegtran": [176],
    "tjbench": [857],
    "qemu-edid": [49],
    "qemu-img-bench": [4376],
    "qemu-img-convert": [2238],
    "qemu-img-dd": [4960],
    "qemu-img-measure": [5209],
    "qemu-nbd": [598],
    "catdoc": [59],
    "xls2csv": [64],
    "bsdcpio": [190],
    "bsdtar": [291],
    "xmlcatalog": [330],
    "xmllint": [3143],
    "nasm": [994],
    "ndisasm": [106],
    "s2nc": [356],
    "s2nd": [324],
    # "php": [625, 688],
    "php": [689],
    "phpdbg": [1195],
    "bison": [693],
    "gifsicle": [1532],
    # "imagew": [2224, 2448],
    "imagew": [2448],
    "jbig2dec": [270],
    "jhead": [1473],
    "dwarfdump": [2540],
    "dwarfdump-conf": [1126],
    "makeswf": [233],
    "pngfix": [3874],
    "img2sixel": [1234],
    "nginx": [755],
    "sngrep": [210],
    "sngrep-conf": [125],
    "sqlite3": [26003],
    "w3m": [569],
    "outparamtest":[20]
}

parse_end_dict = {
    "ar": 777,
    "as": 1317,
    "gdb": 1005,
    "gprof": 489,
    "objdump": 5901,
    "readelf": 22833,
    "size": 249,
    "fax2ps": 396,
    "fax2tiff": 225,
    "tiff2ps": 452,
    "tiff2rgba": 129,
    "tiffcp": 354,
    "tiffcrop": 2646,
    "tiffinfo": 151,
    "scp": 587,
    "sftp": 2556,
    "ssh": 1058,
    "ssh-agent": 2093,
    "ssh-keygen": 3553,
    "ssh-keyscan": 778,
    "ab": 2610,
    "htcacheclean": 1623,
    "htdbm": 380,
    "htpasswd": 330,
    "httpd": 657,
    "mupdf-x11": 933,
    "muraster": 1540,
    "mutool-clean": 120,
    "mutool-convert": 153,
    "mutool-draw": 2041,
    "imgcmp": 261,
    "imginfo": 239,
    "jasper": 186,
    "cjpeg": 606,
    "jpegtran": 496,
    "tjbench": 975,
    "qemu-edid": 118,
    "qemu-img-bench": 4520,
    "qemu-img-convert": 2386,
    "qemu-img-dd": 4992,
    "qemu-img-measure": 5274,
    "qemu-nbd": 787,
    "catdoc": 108,
    "xls2csv": 116,
    "bsdcpio": 388,
    "bsdtar": 805,
    "xmlcatalog": 372,
    "xmllint": 3487,
    "nasm": 584,
    "ndisasm": 271,
    "s2nc": 491,
    "s2nd": 457,
    "php": 855,
    "phpdbg": 1290,
    "bison": 103,
    "gifsicle": 2172,
    "imagew": 2979,
    "jbig2dec": 572,
    "jhead": 1725,
    "dwarfdump": 2859,
    "dwarfdump-conf": 356,
    "makeswf": 340,
    "pngfix": 4023,
    "img2sixel": 418,
    "nginx": 215,
    "sngrep": 330,
    "sngrep-conf": 330,
    "sqlite3": 26116,
    "w3m": 839,
    "outparamtest":35
}

if __name__ == "__main__":
    
    ast_path = sys.argv[1]  # binutils/ar/ar-ast
    dot_list = get_dot_path(ast_path)
    global_path = '/'.join(ast_path.split('/')[:-1]) + "/" + "global.txt"
    global_variable_list, custom_function_list = get_global(global_path)
    
    parse_kind = sys.argv[2]
    
    prog_target = ast_path.split("/")[-2]
    # if prog_target == "mutool" or prog_target == "qemu":
    #     prog_target += " " + sys.argv[3]
    
    ans_dict = {}   # return results
    cfg_path = '/'.join(ast_path.split('/')[:-1]) + "/" + prog_target + "-cfg"
    pdg_path = '/'.join(ast_path.split('/')[:-1]) + "/" + prog_target + "-pdg"
    div_flow_path = '/'.join(ast_path.split('/')[:-1]) + "/" + "div_flow.json"
    out_path = '/'.join(ast_path.split('/')[:-1]) + "/" + "pass.json"
    num_path = '/'.join(ast_path.split('/')[:-1]) + "/" + "num.json"
    num_dict = {}
    
    res_num_list = []
    res_str_list = []
    finish_flag = False
    
    # DIV num
    div_count = 0
    # count numeric
    num_count = 0
    # count string 
    str_count = 0
    
    if parse_kind == "switch":
        
        for dot in dot_list:
            if finish_flag == True:
                break
            g = generate_graph(dot)
            for func_index in range(len(parse_func_dict[prog_target])):
                
                if g.get_name() == parse_func_dict[prog_target][func_index]:
                    for node_id in g.node_set:
                        node = g.node_set[node_id]
                        # if finish_flag == True:
                        #     break
                        if node.line != parse_start_dict[prog_target][func_index]:
                            continue
                        # node is under loop
                        if (node.type_str == "CONTROL_STRUCTURE" and (node.cst_left_type == "while" or node.cst_left_type == "for" or node.cst_left_type == "if")) or (node.type_str == "CONTROL_STRUCTURE" and node.cst_left_type == "switch") :
                            if node.type_str == "CONTROL_STRUCTURE" and node.cst_left_type == "switch":
                                queue = [node]
                            else:
                                queue = [node]
                                # look for switch
                                while True:
                                    nextQueue = []
                                    switch_flag = False
                                    for point in queue:
                                        for child in point.children:
                                            nextQueue.append(child)
                                            if child.type_str == "CONTROL_STRUCTURE" and child.cst_left_type == "switch":
                                                switch_flag = True
                                    queue = nextQueue
                                    if switch_flag == True:
                                        break
                            
                            cnt_case = ""   # current option 
                            cnt_case_list = []  # options not finished
                            div_content_list = []   # DIVs for current option
                            
                            for switch_node in queue:
                                if switch_node.type_str == "CONTROL_STRUCTURE" and switch_node.cst_left_type == "switch":
                                    # print(switch_node.line)
                                    switch_block_node = switch_node.children[1]
                                    for block_child_index in range(len(switch_block_node.children)):
                                        switch_child = switch_block_node.children[block_child_index]
                                        # case node
                                        if switch_child.type_str == "JUMP_TARGET" and switch_child.jt_content == "case":
                                            
                                            # break in block
                                            if block_child_index != 0 and switch_block_node.children[block_child_index - 1].type_str == "BLOCK" and switch_block_node.children[block_child_index - 1].children != [] and switch_block_node.children[block_child_index - 1].children[-1].type_str == "CONTROL_STRUCTURE" and switch_block_node.children[block_child_index - 1].children[-1].cst_left_type == "break":
                                                if cnt_case_list != [] and div_content_list != []:
                                                    for case in cnt_case_list:
                                                        ans_dict[case].extend(div_content_list)
                                                cnt_case_list = []
                                                
                                            if cnt_case_list != [] and div_content_list != []:
                                                for case in cnt_case_list:
                                                    ans_dict[case].extend(div_content_list)
                                                    
                                            if switch_block_node.children[block_child_index + 1].type_str == "LITERAL":
                                                cnt_case = switch_block_node.children[block_child_index + 1].lit_var
                                            elif switch_block_node.children[block_child_index + 1].type_str == "IDENTIFIER":
                                                cnt_case = switch_block_node.children[block_child_index + 1].ide_var
                                            elif switch_block_node.children[block_child_index + 1].custom == 1:
                                                cnt_case = switch_block_node.children[block_child_index + 1].type_str
                                            cnt_case_list.append(cnt_case)
                                            ans_dict[cnt_case] = []
                                            div_content_list = []
                                            
                                        # break node
                                        elif switch_child.type_str == "CONTROL_STRUCTURE" and switch_child.cst_left_type == "break" or switch_child.type_str == "RETURN":
                                            
                                            if cnt_case_list != [] and div_content_list != []:
                                                for case in cnt_case_list:
                                                    ans_dict[case].extend(div_content_list)
                                            cnt_case_list = []
                                            
                                        # default node
                                        elif switch_child.type_str == "JUMP_TARGET" and switch_child.jt_content == "default":
                                            
                                            if cnt_case_list != [] and div_content_list != []:
                                                for case in cnt_case_list:
                                                    ans_dict[case].extend(div_content_list)
                                            cnt_case = "default"
                                            cnt_case_list.append(cnt_case)
                                            ans_dict[cnt_case] = []
                                            div_content_list = []
                                            
                                        stack = [switch_child]
                                        while stack:
                                            tNode = stack.pop()
                                            
                                            # two vars
                                            if tNode.type_str in ["&lt;operator&gt;.assignment", "&lt;operator&gt;.assignmentPlus", "&lt;operator&gt;.assignmentMinus", "&lt;operator&gt;.assignmentMultiplication", "&lt;operator&gt;.assignmentDivision", "&lt;operators&gt;.assignmentOr", "&lt;operators&gt;.assignmentAnd", "&lt;operator&gt;.arithmeticShiftRight", "&lt;operator&gt;.shiftRight", "&lt;operator&gt;.arithmeticShiftLeft", "&lt;operator&gt;.shiftLeft"]:
                                                if tNode.type_str == "&lt;operator&gt;.assignment":
                                                    content, left, right = tNode.assign_content, tNode.assign_var, tNode.assign_content.split('=')[1].strip()
                                                elif tNode.type_str == "&lt;operator&gt;.assignmentPlus":
                                                    content, left, right = tNode.assign_plus_content, tNode.assign_plus_left, tNode.assign_plus_right
                                                elif tNode.type_str == "&lt;operator&gt;.assignmentMinus":
                                                    content, left, right = tNode.assign_minus_content, tNode.assign_minus_left, tNode.assign_minus_right
                                                elif tNode.type_str == "&lt;operator&gt;.assignmentMultiplication":
                                                    content, left, right = tNode.assign_multi_content, tNode.assign_multi_left, tNode.assign_multi_right
                                                elif tNode.type_str == "&lt;operator&gt;.assignmentDivision":
                                                    content, left, right = tNode.assign_div_content, tNode.assign_div_left, tNode.assign_div_right
                                                elif tNode.type_str == "&lt;operators&gt;.assignmentOr":
                                                    content, left, right = tNode.assign_or_content, tNode.assign_or_left, tNode.assign_or_right
                                                elif tNode.type_str == "&lt;operators&gt;.assignmentAnd":
                                                    content, left, right = tNode.assign_and_content, tNode.assign_and_left, tNode.assign_and_right
                                                elif tNode.type_str == "&lt;operator&gt;.arithmeticShiftRight" or tNode.type_str == "&lt;operator&gt;.shiftRight":
                                                    content, left, right = tNode.arith_shift_right_content, tNode.arith_shift_right_var, tNode.arith_shift_right_num
                                                elif tNode.type_str == "&lt;operator&gt;.arithmeticShiftLeft" or tNode.type_str == "&lt;operator&gt;.shiftLeft":
                                                    content, left, right = tNode.arith_shift_left_content, tNode.arith_shift_left_var, tNode.arith_shift_left_num

                                                # transfer
                                                if ("optarg" in right or "argv" in right or "opt_arg" in right or "argument" in right or "param" in right or "p[1]" in right or "clp-&gt;vstr" in right or "clp-&gt;val.i" in right or "clp-&gt;val.s" in right or "clp-&gt;val.u" in right ) and "argv[0]" not in right:
                                                # if "line" in right:
                                                    if left in global_variable_list:
                                                        div_content_list.append((parse_func_dict[prog_target][func_index], left, 1, -1, 1))
                                                        div_count += 1
                                                        if any(substr in right for substr in ["atoi", "atof", "atol","strtoul","strtol","strtoimax", "strtoull", "qemu_strtoui", "qemu_strtoi", "qemu_strtou64", "qemu_strtol", "qemu_strtoul", "cvtnum", "cvtnum_full", "strtonum"]):
                                                            
                                                        # if "atoi" in right or "atof" in right or "atol" in right or "strtoul" in right or "strtol" in right or "strtoimax" in right or "strtoull" in right or "qemu_strtoui" in right :
                                                            res_num_list.append(cnt_case)
                                                            
                                                            num_count += 1
                                                        else:
                                                            res_str_list.append(cnt_case)
                                                            
                                                            str_count += 1
                                                    else:
                                                        div_content_list.append((parse_func_dict[prog_target][func_index], left, 0, tNode.line, 1))
                                                        div_count += 1
                                                        if any(substr in right for substr in ["atoi", "atof", "atol","strtoul","strtol","strtoimax", "strtoull", "qemu_strtoui", "qemu_strtoi", "qemu_strtou64", "qemu_strtol", "qemu_strtoul", "cvtnum", "cvtnum_full", "strtonum"]):
                                                        
                                                        # if "atoi" in right or "atof" in right or "atol" in right or "strtoul" in right or "strtol" in right or "strtoimax" in right or "strtoull" in right or "qemu_strtoui" in right:
                                                            res_num_list.append(cnt_case)
                                                            
                                                            num_count += 1
                                                        else:
                                                            res_str_list.append(cnt_case)
                                                            
                                                            str_count += 1
                                                        
                                                # enable
                                                else:
                                                    if left in global_variable_list:
                                                        div_content_list.append((parse_func_dict[prog_target][func_index], left, 1, -1, 0))
                                                        div_count += 1
                                                    else:
                                                        div_content_list.append((parse_func_dict[prog_target][func_index], left, 0, tNode.line, 0))
                                                        div_count += 1
                                                
                                            # one variable
                                            elif tNode.type_str in ["&lt;operator&gt;.postDecrement", "&lt;operator&gt;.postIncrement", "&lt;operator&gt;.preDecrement", "&lt;operator&gt;.preIncrement"]:
                                                if tNode.type_str == "&lt;operator&gt;.postDecrement":
                                                    content, left = tNode.post_decre_content, tNode.post_decre_var
                                                elif tNode.type_str == "&lt;operator&gt;.postIncrement":
                                                    content, left = tNode.post_incre_content, tNode.post_incre_var
                                                elif tNode.type_str == "&lt;operator&gt;.preDecrement":
                                                    content, left = tNode.pre_decre_content, tNode.pre_decre_var
                                                elif tNode.type_str == "&lt;operator&gt;.preIncrement":
                                                    content, left = tNode.pre_incre_content, tNode.pre_incre_var
                                                
                                                if left in global_variable_list:
                                                    div_content_list.append((parse_func_dict[prog_target][func_index], left, 1, -1, 0))
                                                    div_count += 1
                                                else:
                                                    div_content_list.append((parse_func_dict[prog_target][func_index], left, 0, tNode.line, 0))
                                                    div_count += 1
                                                
                                                if ("optarg" in left or "argv" in left  or "opt_arg" in left or "argument" in left  or "param" in left or "p[1]" in left or "clp-&gt;vstr" in left or "clp-&gt;val.i" in left or "clp-&gt;val.s" in left or "clp-&gt;val.u" in left ) and "argv[0]" not in left:
                                                    if any(substr in left for substr in ["atoi", "atof", "atol","strtoul","strtol","strtoimax", "strtoull", "qemu_strtoui", "qemu_strtoi", "qemu_strtou64", "qemu_strtol", "qemu_strtoul", "cvtnum", "cvtnum_full", "strtonum"]):
                                                        
                                                    # if "atoi" in left or "atof" in left or "atol" in left or "strtoul" in left or "strtol" in left or "strtoimax" in left or "strtoull" in left or "qemu_strtoui" in left:
                                                        res_num_list.append(cnt_case)
                                                        
                                                        num_count += 1
                                                    else:
                                                        res_str_list.append(cnt_case)
                                                        
                                                        str_count += 1
                                                    
                                            # custom functions
                                            elif tNode.custom == 1 and tNode.function_name in custom_function_list or "addargs" in tNode.function_name or "strcmp" in tNode.function_name:
                                            # elif tNode.custom == 1 :
                                                print("=*&@")
                                                param_list = []
                                                for index in range(len(tNode.children)):
                                                    child = tNode.children[index]
                                                    print(child.ide_var)
                                                    if ("optarg" in child.ide_var or "argv" in child.ide_var or "opt_arg" in child.ide_var or "value" in child.ide_var or "argument" in child.ide_var  or "param" in child.ide_var or "p[1]" in child.ide_var or "clp-&gt;vstr" in child.ide_var or "clp-&gt;val.i" in child.ide_var or "clp-&gt;val.s" in child.ide_var or "clp-&gt;val.u" in child.ide_var ) and "argv[0]" not in child.ide_var:
                                                        print("abcdddd")
                                                        if any(substr in child.ide_var for substr in ["atoi", "atof", "atol","strtoul","strtol","strtoimax", "strtoull", "qemu_strtoui", "qemu_strtoi", "qemu_strtou64", "qemu_strtol", "qemu_strtoul", "cvtnum", "cvtnum_full", "strtonum", "value"]) or any(substr in tNode.function_name for substr in ["atoi", "atof", "atol","strtoul","strtol","strtoimax", "strtoull", "qemu_strtoui", "qemu_strtoi", "qemu_strtou64", "qemu_strtol", "qemu_strtoul", "cvtnum", "cvtnum_full", "strtonum", "value"]):
                                                            res_num_list.append(cnt_case)
                                                            
                                                            num_count += 1
                                                        else:
                                                            res_str_list.append(cnt_case)
                                                            
                                                            str_count += 1
                                                    if child.type_str == "LITERAL":
                                                        param_list.append((child.lit_var, index, 0))
                                                    elif child.type_str == "IDENTIFIER":
                                                        if child.ide_var.find("opt") != -1 or child.ide_var.find("arg") != -1:
                                                        # if child.ide_var.find("line") != -1
                                                            param_list.append((child.ide_var, index, 1))
                                                        else:
                                                            param_list.append((child.ide_var, index, 0))
                                                    elif child.custom == 1:
                                                        param_list.append((child.function_content, index, 0))
                                                    elif child.type_str == "&lt;operator&gt;.indirectIndexAccess":
                                                        if child.indirect_ia_array.find("argv") != -1 and child.indirect_ia_index != '0':
                                                            param_list.append((child.indirect_ia_content, index, 1))
                                                        else:                                                    
                                                            param_list.append((child.indirect_ia_content, index, 0))
                                                for param in param_list:
                                                    for p in div_content_list:
                                                        if param[0] == p[1]:
                                                            if param in param_list:
                                                                param_list.remove(param)
                                                                param_list.append((param[0], param[1], p[4]))
                                                spread_dict = inter_spread(cnt_case_list, tNode.function_name, param_list, cfg_path, pdg_path, ast_path, div_flow_path, global_path)
                                                func_list = []
                                                for k in spread_dict:
                                                    if spread_dict[k]["funcname"] not in func_list:
                                                        func_list.append(spread_dict[k]["funcname"])
                                                for k in spread_dict:
                                                    for var in spread_dict[k]["vars"]:
                                                        if var in global_variable_list:
                                                            div_content_list.append((spread_dict[k]["funcname"], var, 1, -1, 1))
                                                            str_count += 1
                                                            div_count += 1
                                                for func in func_list:
                                                    global_list = find_method_global(func, ast_path)
                                                    for global_var in global_list:
                                                        if (func, global_var, 1, -1, 0) not in div_content_list:
                                                            div_content_list.append((func, global_var, 1, -1, 0))
                                                            div_count += 1
                                                func_list = []
                                            # snprintf
                                            elif tNode.custom == 1 and tNode.function_name == "snprintf":
                                                child_num = len(tNode.children)
                                                pass_flag = 0
                                                # whether impacted by options
                                                for index in range(3, child_num):
                                                    tNode_child = tNode.children[index]
                                                    if ("optarg" in tNode_child.ide_var or "argv" in tNode_child.ide_var or "opt_arg" in tNode_child.ide_var or "argument" in tNode_child.ide_var   or "param" in tNode_child.ide_var  or "p[1]" in tNode_child.ide_var  or "clp-&gt;vstr" in tNode_child.ide_var or "clp-&gt;val.i" in tNode_child.ide_var or "clp-&gt;val.s" in tNode_child.ide_var or "clp-&gt;val.u" in tNode_child.ide_var ) and "argv[0]" not in tNode_child.ide_var:
                                                        if any(substr in tNode_child.ide_var for substr in ["atoi", "atof", "atol","strtoul","strtol","strtoimax", "strtoull", "qemu_strtoui", "qemu_strtoi", "qemu_strtou64", "qemu_strtol", "qemu_strtoul", "cvtnum", "cvtnum_full", "strtonum"]):
                                                    
                                                        # if "atoi" in tNode_child.ide_var or "atof" in tNode_child.ide_var or "atol" in tNode_child.ide_var or "strtoul" in tNode_child.ide_var or "strtol" in tNode_child.ide_var or "strtoimax" in tNode_child.ide_var or "strtoull" in tNode_child.ide_var:
                                                            res_num_list.append(cnt_case)
                                                            
                                                            num_count += 1
                                                        else:
                                                            res_str_list.append(cnt_case)
                                                            
                                                            str_count += 1
                                                    if (tNode_child.type_str == "IDENTIFIER" and tNode_child.ide_var.find("optarg") != -1) or (tNode_child.type_str == "&lt;operator&gt;.indirectIndexAccess" and tNode_child.indirect_ia_array == "argv" and tNode_child.indirect_ia_index != 0):
                                                    # if (tNode_child.type_str == "IDENTIFIER" and tNode_child.ide_var.find("line") != -1) or (tNode_child.type_str == "&lt;operator&gt;.indirectIndexAccess" and tNode_child.indirect_ia_array == "argv" and tNode_child.indirect_ia_index != 0):
                                                        pass_flag = 1
                                                if tNode.children[0].type_str == "IDENTIFIER":
                                                    if tNode.children[0].ide_var in global_variable_list:
                                                        div_content_list.append((parse_func_dict[prog_target][func_index], tNode.children[0].ide_var, 1, -1, pass_flag))
                                                        div_count += 1
                                                    else:
                                                        div_content_list.append((parse_func_dict[prog_target][func_index], tNode.children[0].ide_var, 0, tNode.children[0].line, pass_flag))
                                                        div_count += 1
                                                    if pass_flag == 1:
                                                        str_count += 1
                                                elif tNode.chilren[0].type_str == "&lt;operator&gt;.indirectIndexAccess":
                                                    if tNode.children[0].indirect_ia_content in global_variable_list:
                                                        div_content_list.append((parse_func_dict[prog_target][func_index], tNode.children[0].indirect_ia_content, 1, -1, pass_flag))
                                                        div_count += 1
                                                    else:
                                                        div_content_list.append((parse_func_dict[prog_target][func_index], tNode.children[0].indirect_ia_content, 0, tNode.children[0].line, pass_flag))
                                                        div_count += 1
                                                    if pass_flag == 1:
                                                        str_count += 1
                                                        
                                            # sscanf
                                            elif tNode.custom == 1 and tNode.function_name == "__isoc99_sscanf":
                                                child_num = len(tNode.children)
                                                pass_flag = 0
                                                if (tNode.children[0].type_str == "IDENTIFIER" and tNode.children[0].ide_var.find("optarg") != -1) or (tNode.children[0].type_str == "&lt;operator&gt;.indirectIndexAccess" and tNode.children[0].indirect_ia_array == "argv" and tNode.children[0].indirect_ia_index != 0):
                                                # if (tNode.children[0].type_str == "IDENTIFIER" and tNode.children[0].ide_var.find("line") != -1) or (tNode.children[0].type_str == "&lt;operator&gt;.indirectIndexAccess" and tNode.children[0].indirect_ia_array == "argv" and tNode.children[0].indirect_ia_index != 0):
                                                    pass_flag = 1
                                                for index in range(2, child_num):
                                                    tNode_child = tNode.children[index]
                                                    if ("optarg" in tNode_child.ide_var or "argv" in tNode_child.ide_var or "opt_arg" in tNode_child.ide_var or "argument" in tNode_child.ide_var  or "param" in tNode_child.ide_var  or "p[1]" in tNode_child.ide_var  or "clp-&gt;vstr" in tNode_child.ide_var or "clp-&gt;val.i" in tNode_child.ide_var or "clp-&gt;val.s" in tNode_child.ide_var or "clp-&gt;val.u" in tNode_child.ide_var ) and "argv[0]" not in tNode_child.ide_var:
                                                        if any(substr in tNode_child.ide_var for substr in ["atoi", "atof", "atol","strtoul","strtol","strtoimax", "strtoull", "qemu_strtoui", "qemu_strtoi", "qemu_strtou64", "qemu_strtol", "qemu_strtoul", "cvtnum", "cvtnum_full", "strtonum"]):
                                                    
                                                        # if "atoi" in tNode_child.ide_var or "atof" in tNode_child.ide_var or "atol" in tNode_child.ide_var or "strtoul" in tNode_child.ide_var or "strtol" in tNode_child.ide_var or "strtoimax" in tNode_child.ide_var or "strtoull" in tNode_child.ide_var:
                                                            res_num_list.append(cnt_case)
                                                            
                                                            num_count += 1
                                                        else:
                                                            res_str_list.append(cnt_case)
                                                            
                                                            str_count += 1
                                                    if tNode_child.type_str == "&lt;operator&gt;.addressOf":
                                                        if tNode_child.addressof_var in global_variable_list:
                                                            div_content_list.append((parse_func_dict[prog_target][func_index], tNode_child.addressof_var, 1, -1, pass_flag))
                                                            div_count += 1
                                                        else:
                                                            div_content_list.append((parse_func_dict[prog_target][func_index], tNode_child.addressof_var, 0, tNode_child.line, pass_flag))
                                                            div_count += 1
                                                        if pass_flag == 1:
                                                            str_count += 1
                                            
                                            for child in tNode.children:
                                                stack.append(child)
                        
                        finish_flag = True      
                    # break
            
    else:
        for dot in dot_list:
            g = generate_graph(dot)
            for func_index in range(len(parse_func_dict[prog_target])):
                if finish_flag:
                    break
                if g.get_name() == parse_func_dict[prog_target][func_index]:
                    for node_id in g.node_set:
                        if finish_flag:
                            break
                        node = g.node_set[node_id]
                        
                        if node.line != parse_start_dict[prog_target][func_index]:
                            continue
                        
                        if node.type_str == "CONTROL_STRUCTURE" and node.cst_left_type == "if":
                            cnt_case = ""   # current option
                            div_content_list = []   # current DIVs
                            while len(node.children) == 3 and node.children[2].type_str == "CONTROL_STRUCTURE" and node.children[2].cst_left_type == "else":
                                temp_node = node
                                while temp_node.children != [] and (not (temp_node.children[0].custom == 1 and (temp_node.children[0].function_name == "keymatch" or temp_node.children[0].function_name == "strcmp" or temp_node.children[0].function_name == "strncmp" or temp_node.children[0].function_name == "strcasecmp" or temp_node.children[0].function_name == "memcmp" or temp_node.children[0].function_name == "cli_strcmp"))) :
                                    temp_node = temp_node.children[0]
                                
                                if temp_node.children == []:
                                    if node.children[2].children[0].type_str == "BLOCK":
                                        node = node.children[2].children[0].children[0]
                                    else:
                                        node = node.children[2].children[0]
                                    continue
                                
                                if temp_node.children[0].function_name == "keymatch":
                                    cnt_case = temp_node.children[0].children[1].lit_var
                                    
                                if temp_node.children[0].function_name == "strcasecmp":
                                    cnt_case = temp_node.children[0].children[1].lit_var
                                
                                if temp_node.children[0].function_name == "strcmp":
                                    if prog_target == "w3m":
                                        cnt_case = temp_node.children[0].children[0].lit_var
                                    else:
                                        cnt_case = temp_node.children[0].children[1].lit_var
                                    
                                if temp_node.children[0].function_name == "memcmp":
                                    cnt_case = temp_node.children[0].children[1].lit_var
                                    
                                if temp_node.children[0].function_name == "strncmp":
                                    cnt_case = temp_node.children[0].children[1].lit_var
                                    
                                if temp_node.children[0].function_name == "cli_strcmp":
                                    cnt_case = temp_node.children[0].children[1].lit_var
                                        
                                # print(cnt_case)
                                # print(node.dot_src)
                                
                                ans_dict[cnt_case] = []
                                block_node = node.children[1]
                                stack = [block_node]
                                while stack:
                                    tNode = stack.pop()
                                    
                                    # two variables
                                    if tNode.type_str in ["&lt;operator&gt;.assignment", "&lt;operator&gt;.assignmentPlus", "&lt;operator&gt;.assignmentMinus", "&lt;operator&gt;.assignmentMultiplication", "&lt;operator&gt;.assignmentDivision", "&lt;operators&gt;.assignmentOr", "&lt;operators&gt;.assignmentAnd", "&lt;operator&gt;.arithmeticShiftRight", "&lt;operator&gt;.shiftRight", "&lt;operator&gt;.arithmeticShiftLeft", "&lt;operator&gt;.shiftLeft"]:
                                        if tNode.type_str == "&lt;operator&gt;.assignment":
                                            content, left, right = tNode.assign_content, tNode.assign_var, tNode.assign_content.split('=')[1].strip()
                                        elif tNode.type_str == "&lt;operator&gt;.assignmentPlus":
                                            content, left, right = tNode.assign_plus_content, tNode.assign_plus_left, tNode.assign_plus_right
                                        elif tNode.type_str == "&lt;operator&gt;.assignmentMinus":
                                            content, left, right = tNode.assign_minus_content, tNode.assign_minus_left, tNode.assign_minus_right
                                        elif tNode.type_str == "&lt;operator&gt;.assignmentMultiplication":
                                            content, left, right = tNode.assign_multi_content, tNode.assign_multi_left, tNode.assign_multi_right
                                        elif tNode.type_str == "&lt;operator&gt;.assignmentDivision":
                                            content, left, right = tNode.assign_div_content, tNode.assign_div_left, tNode.assign_div_right
                                        elif tNode.type_str == "&lt;operators&gt;.assignmentOr":
                                            content, left, right = tNode.assign_or_content, tNode.assign_or_left, tNode.assign_or_right
                                        elif tNode.type_str == "&lt;operators&gt;.assignmentAnd":
                                            content, left, right = tNode.assign_and_content, tNode.assign_and_left, tNode.assign_and_right
                                        elif tNode.type_str == "&lt;operator&gt;.arithmeticShiftRight" or tNode.type_str == "&lt;operator&gt;.shiftRight":
                                            content, left, right = tNode.arith_shift_right_content, tNode.arith_shift_right_var, tNode.arith_shift_right_num
                                        elif tNode.type_str == "&lt;operator&gt;.arithmeticShiftLeft" or tNode.type_str == "&lt;operator&gt;.shiftLeft":
                                            content, left, right = tNode.arith_shift_left_content, tNode.arith_shift_left_var, tNode.arith_shift_left_num

                                        # transfer
                                        if ("optarg" in right or "argv" in right or "opt_arg" in right or "argument" in right or "arg" in right or "param" in right or "p[1]" in right or "clp-&gt;vstr" in right or "clp-&gt;val.i" in right or "clp-&gt;val.s" in right or "clp-&gt;val.u" in right ) and "argv[0]" not in right:
                                        # if "type" in right or "option" in right or "value" in right:
                                            if left in global_variable_list:
                                                div_content_list.append((parse_func_dict[prog_target][func_index], left, 1, -1, 1))
                                                div_count += 1
                                                if any(substr in right for substr in ["atoi", "atof", "atol","strtoul","strtol","strtoimax", "strtoull", "qemu_strtoui", "qemu_strtoi", "qemu_strtou64", "qemu_strtol", "qemu_strtoul", "cvtnum", "cvtnum_full", "strtonum"]):
                                                    
                                                # if "atoi" in right or "atof" in right  or "atol" in right or "strtol" in right or "strtoul" in right or "strtoimax" in right or "strtoull" in right:
                                                    res_num_list.append(cnt_case)
                                                    num_count += 1
                                                else:
                                                    res_str_list.append(cnt_case)
                                                    str_count += 1
                                            else:
                                                div_content_list.append((parse_func_dict[prog_target][func_index], left, 0, tNode.line, 1))
                                                div_count += 1
                                                if any(substr in right for substr in ["atoi", "atof", "atol","strtoul","strtol","strtoimax", "strtoull", "qemu_strtoui", "qemu_strtoi", "qemu_strtou64", "qemu_strtol", "qemu_strtoul", "cvtnum", "cvtnum_full", "strtonum"]):
                                                
                                                # if "atoi" in right or "atof" in right  or "atol" in right or "strtol" in right or "strtoul" in right or "strtoimax" in right or "strtoull" in right:
                                                    res_num_list.append(cnt_case)
                                                    num_count += 1
                                                else:
                                                    res_str_list.append(cnt_case)
                                                    str_count += 1
                                        # enable
                                        else:
                                            if left in global_variable_list:
                                                div_content_list.append((parse_func_dict[prog_target][func_index], left, 1, -1, 0))
                                                div_count += 1
                                            else:
                                                div_content_list.append((parse_func_dict[prog_target][func_index], left, 0, tNode.line, 0))
                                                div_count += 1
                                    
                                    # one variable
                                    elif tNode.type_str in ["&lt;operator&gt;.postDecrement", "&lt;operator&gt;.postIncrement", "&lt;operator&gt;.preDecrement", "&lt;operator&gt;.preIncrement"]:
                                        if tNode.type_str == "&lt;operator&gt;.postDecrement":
                                            content, left = tNode.post_decre_content, tNode.post_decre_var
                                        elif tNode.type_str == "&lt;operator&gt;.postIncrement":
                                            content, left = tNode.post_incre_content, tNode.post_incre_var
                                        elif tNode.type_str == "&lt;operator&gt;.preDecrement":
                                            content, left = tNode.pre_decre_content, tNode.pre_decre_var
                                        elif tNode.type_str == "&lt;operator&gt;.preIncrement":
                                            content, left = tNode.pre_incre_content, tNode.pre_incre_var
                                        
                                        if left in global_variable_list:
                                            div_content_list.append((parse_func_dict[prog_target][func_index], left, 1, -1, 0))
                                            div_count += 1
                                        else:
                                            div_content_list.append((parse_func_dict[prog_target][func_index], left, 0, tNode.line, 0))
                                            div_count += 1

                                        if ("optarg" in left or "argv" in left or "opt_arg" in left or "argument" in left  or "param" in left or "arg" in left or "p[1]" in left or "clp-&gt;vstr" in left or "clp-&gt;val.i" in left or "clp-&gt;val.s" in left or "clp-&gt;val.u" in left ) and "argv[0]" not in left:
                                            if any(substr in left for substr in ["atoi", "atof", "atol","strtoul","strtol","strtoimax", "strtoull", "qemu_strtoui", "qemu_strtoi", "qemu_strtou64", "qemu_strtol", "qemu_strtoul", "cvtnum", "cvtnum_full", "strtonum"]):
                                                
                                            # if "atoi" in left or "atof" in left or "atol" in left or "strtoul" in left or "strtol" in left or "strtoimax" in left or "strtoull" in left:
                                                res_num_list.append(cnt_case)
                                                num_count += 1
                                            else:
                                                res_str_list.append(cnt_case)
                                                str_count += 1
                                    # custom function
                                    elif tNode.custom == 1 and tNode.function_name in custom_function_list  or "addargs" in tNode.function_name:
                                        param_list = []
                                        for index in range(len(tNode.children)):
                                            child = tNode.children[index]
                                            if ("optarg" in child.ide_var or "argv" in child.ide_var or "opt_arg" in child.ide_var or "arg" in child.ide_var or "argument" in child.ide_var  or "param" in child.ide_var  or "p[1]" in child.ide_var  or "clp-&gt;vstr" in child.ide_var or "clp-&gt;val.i" in child.ide_var or "clp-&gt;val.s" in child.ide_var or "clp-&gt;val.u" in child.ide_var ) and "argv[0]" not in child.ide_var:
                                                if any(substr in child.ide_var for substr in ["atoi", "atof", "atol","strtoul","strtol","strtoimax", "strtoull", "qemu_strtoui", "qemu_strtoi", "qemu_strtou64", "qemu_strtol", "qemu_strtoul", "cvtnum", "cvtnum_full", "strtonum"]) or any(substr in tNode.function_name for substr in ["atoi", "atof", "atol","strtoul","strtol","strtoimax", "strtoull", "qemu_strtoui", "qemu_strtoi", "qemu_strtou64", "qemu_strtol", "qemu_strtoul", "cvtnum", "cvtnum_full", "strtonum"]):
                                            
                                                # if "atoi" in child.ide_var or "atof" in child.ide_var or "atol" in child.ide_var or "strtoul" in child.ide_var or "strtol" in child.ide_var or "strtoimax" in child.ide_var or "strtoull" in child.ide_var:
                                                    res_num_list.append(cnt_case)
                                                    num_count += 1
                                                else:
                                                    res_str_list.append(cnt_case)
                                                    str_count += 1
                                            if child.type_str == "LITERAL":
                                                param_list.append((child.lit_var, index, 0))
                                            elif child.type_str == "IDENTIFIER":
                                                # if child.ide_var.find("opt") != -1 or child.ide_var.find("arg") != -1:
                                                if child.ide_var.find("type") != -1 or child.ide_var.find("option") != -1 or child.ide_var.find("value") != -1:
                                                    param_list.append((child.ide_var, index, 1))
                                                else:
                                                    param_list.append((child.ide_var, index, 0))
                                            elif child.custom == 1:
                                                param_list.append((child.function_content, index, 0))
                                            elif child.type_str == "&lt;operator&gt;.indirectIndexAccess":
                                                if child.indirect_ia_array.find("argv") != -1 and child.indirect_ia_index != '0':
                                                    param_list.append((child.indirect_ia_content, index, 1))
                                                else:                                                    
                                                    param_list.append((child.indirect_ia_content, index, 0))
                                        for param in param_list:
                                            for p in div_content_list:
                                                if param[0] == p[1]:
                                                    if param in param_list:
                                                        param_list.remove(param)
                                                        param_list.append((param[0], param[1], p[4]))
                                        spread_dict = inter_spread([cnt_case], tNode.function_name, param_list, cfg_path, pdg_path, ast_path, div_flow_path, global_path)
                                        func_list = []
                                        for k in spread_dict:
                                            if spread_dict[k]["funcname"] not in func_list:
                                                func_list.append(spread_dict[k]["funcname"])
                                        for k in spread_dict:
                                            for var in spread_dict[k]["vars"]:
                                                if var in global_variable_list:
                                                    div_content_list.append((spread_dict[k]["funcname"], var, 1, -1, 1))
                                                    div_count += 1
                                                    str_count += 1
                                        for func in func_list:
                                            global_list = find_method_global(func, ast_path)
                                            for global_var in global_list:
                                                if (func, global_var, 1, -1, 0) not in div_content_list:
                                                    div_content_list.append((func, global_var, 1, -1, 0))
                                                    div_count += 1
                                        func_list = []
                                    
                                    
                                    # snprintf
                                    elif tNode.custom == 1 and tNode.function_name == "snprintf":
                                        child_num = len(tNode.children)
                                        pass_flag = 0
                                        # whether impacted by options
                                        for index in range(3, child_num):
                                            tNode_child = tNode.children[index]
                                            if ("optarg" in tNode_child.ide_var or "argv" in tNode_child.ide_var  or "opt_arg" in tNode_child.ide_var or "arg" in tNode_child.ide_var or "argument" in tNode_child.ide_var  or "param" in tNode_child.ide_var  or "p[1]" in tNode_child.ide_var  or "clp-&gt;vstr" in tNode_child.ide_var or "clp-&gt;val.i" in tNode_child.ide_var or "clp-&gt;val.s" in tNode_child.ide_var or "clp-&gt;val.u" in tNode_child.ide_var ) and "argv[0]" not in tNode_child.ide_var:
                                                if any(substr in tNode_child.ide_var for substr in ["atoi", "atof", "atol","strtoul","strtol","strtoimax", "strtoull", "qemu_strtoui", "qemu_strtoi", "qemu_strtou64", "qemu_strtol", "qemu_strtoul", "cvtnum", "cvtnum_full", "strtonum"]):
                                            
                                                # if "atoi" in tNode_child.ide_var or "atof" in tNode_child.ide_var or "atol" in tNode_child.ide_var or "strtoul" in tNode_child.ide_var or "strtol" in tNode_child.ide_var or "strtoimax" in tNode_child.ide_var or "strtoull" in tNode_child.ide_var:
                                                    res_num_list.append(cnt_case)
                                                    num_count += 1
                                                else:
                                                    res_str_list.append(cnt_case)
                                                    str_count += 1
                                            # if (tNode_child.type_str == "IDENTIFIER" and tNode_child.ide_var.find("optarg") != -1) or (tNode_child.type_str == "&lt;operator&gt;.indirectIndexAccess" and tNode_child.indirect_ia_array == "argv" and tNode_child.indirect_ia_index != 0):
                                            if (tNode_child.type_str == "IDENTIFIER" and tNode_child.ide_var.find("type") != -1) or (tNode_child.type_str == "IDENTIFIER" and tNode_child.ide_var.find("option") != -1) or (tNode_child.type_str == "IDENTIFIER" and tNode_child.ide_var.find("value") != -1) or (tNode_child.type_str == "&lt;operator&gt;.indirectIndexAccess" and tNode_child.indirect_ia_array == "argv" and tNode_child.indirect_ia_index != 0):
                                                pass_flag = 1
                                        if tNode.children[0].type_str == "IDENTIFIER":
                                            if tNode.children[0].ide_var in global_variable_list:
                                                div_content_list.append((parse_func_dict[prog_target][func_index], tNode.children[0].ide_var, 1, -1, pass_flag))
                                                div_count += 1
                                            else:
                                                div_content_list.append((parse_func_dict[prog_target][func_index], tNode.children[0].ide_var, 0, tNode.children[0].line, pass_flag))
                                                div_count += 1
                                            if pass_flag == 1:
                                                str_count += 1
                                        elif tNode.chilren[0].type_str == "&lt;operator&gt;.indirectIndexAccess":
                                            if tNode.children[0].indirect_ia_content in global_variable_list:
                                                div_content_list.append((parse_func_dict[prog_target][func_index], tNode.children[0].indirect_ia_content, 1, -1, pass_flag))
                                                div_count += 1
                                            else:
                                                div_content_list.append((parse_func_dict[prog_target][func_index], tNode.children[0].indirect_ia_content, 0, tNode.children[0].line, pass_flag))
                                                div_count += 1
                                            if pass_flag == 1:
                                                str_count += 1

                                    
                                    
                                    # sscanf
                                    elif tNode.custom == 1 and tNode.function_name == "__isoc99_sscanf":
                                        child_num = len(tNode.children)
                                        pass_flag = 0
                                        # if (tNode.children[0].type_str == "IDENTIFIER" and tNode.children[0].ide_var.find("optarg") != -1) or (tNode.children[0].type_str == "&lt;operator&gt;.indirectIndexAccess" and tNode.children[0].indirect_ia_array == "argv" and tNode.children[0].indirect_ia_index != 0):
                                        if (tNode.children[0].type_str == "IDENTIFIER" and tNode.children[0].ide_var.find("type") != -1) or (tNode.children[0].type_str == "IDENTIFIER" and tNode.children[0].ide_var.find("option") != -1) or (tNode.children[0].type_str == "IDENTIFIER" and tNode.children[0].ide_var.find("value") != -1) or (tNode.children[0].type_str == "&lt;operator&gt;.indirectIndexAccess" and tNode.children[0].indirect_ia_array == "argv" and tNode.children[0].indirect_ia_index != 0):
                                            pass_flag = 1
                                        for index in range(2, child_num):
                                            tNode_child = tNode.children[index]
                                            if ("optarg" in tNode_child.ide_var or "argv" in tNode_child.ide_var or "arg" in tNode_child.ide_var or "opt_arg" in tNode_child.ide_var or "argument" in tNode_child.ide_var  or "param" in tNode_child.ide_var  or "p[1]" in tNode_child.ide_var  or "clp-&gt;vstr" in tNode_child.ide_var or "clp-&gt;val.i" in tNode_child.ide_var or "clp-&gt;val.s" in tNode_child.ide_var or "clp-&gt;val.u" in tNode_child.ide_var ) and "argv[0]" not in tNode_child.ide_var:
                                                if any(substr in tNode_child.ide_var for substr in ["atoi", "atof", "atol","strtoul","strtol","strtoimax", "strtoull", "qemu_strtoui", "qemu_strtoi", "qemu_strtou64", "qemu_strtol", "qemu_strtoul", "cvtnum", "cvtnum_full", "strtonum"]):
                                            
                                                # if "atoi" in tNode_child.ide_var or "atof" in tNode_child.ide_var or "atol" in tNode_child.ide_var or "strtoul" in tNode_child.ide_var or "strtol" in tNode_child.ide_var or "strtoimax" in tNode_child.ide_var or "strtoull" in tNode_child.ide_var:
                                                    res_num_list.append(cnt_case)
                                                    num_count += 1
                                                else:
                                                    res_str_list.append(cnt_case)
                                                    str_count += 1
                                            if tNode_child.type_str == "&lt;operator&gt;.addressOf":
                                                if tNode_child.addressof_var in global_variable_list:
                                                    div_content_list.append((parse_func_dict[prog_target][func_index], tNode_child.addressof_var, 1, -1, pass_flag))
                                                    div_count += 1
                                                else:
                                                    div_content_list.append((parse_func_dict[prog_target][func_index], tNode_child.addressof_var, 0, tNode_child.line, pass_flag))
                                                    div_count += 1 
                                                if pass_flag == 1:
                                                    str_count += 1           
                                                            
                                    for child in tNode.children:
                                        stack.append(child)
                                
                                ans_dict[cnt_case].extend(div_content_list)
                                div_content_list = []
                                
                                if node.children[2].children[0].type_str == "BLOCK":
                                    node = node.children[2].children[0].children[0]
                                else:
                                    node = node.children[2].children[0]
                        
                        finish_flag = True
                                
                    break
    
    
    for opt in ans_dict:
        for i in range(len(ans_dict[opt])):
            for j in range(len(ans_dict[opt])):
                if i != j and i < len(ans_dict[opt]) and j < len(ans_dict[opt]) and ans_dict[opt][i][0] == ans_dict[opt][j][0] and ans_dict[opt][i][1] == ans_dict[opt][j][1] and ans_dict[opt][i][2] == ans_dict[opt][j][2] and ans_dict[opt][i][3] == ans_dict[opt][j][3] and ans_dict[opt][i][4] == 1 and ans_dict[opt][j][4] == 0:
                    del ans_dict[opt][j]
                    
    # output
    ans_dict["end_line"] = parse_end_dict[prog_target]
    ans_dict["parse_func"] = parse_func_dict[prog_target][0]
    with open(out_path, "w")as f:
        f.write(json.dumps(ans_dict, indent=4))
        
    num_dict["div_count"] = div_count
    
    res_num_list = list(set(res_num_list))
    res_str_list = list(set(res_str_list))
    tmp_str_list = []
    for case in res_str_list:
        if case not in res_num_list:
            tmp_str_list.append(case)
    num_dict["num_list"] = res_num_list
    num_dict["str_list"] = tmp_str_list
    num_dict["num_count"] = len(res_num_list)
    num_dict["str_count"] = len(tmp_str_list)
    
    with open(num_path, "w") as f:
        f.write(json.dumps(num_dict, indent=4))
    print("===========================")
    print("===========================", res_num_list, " num_len: ", len(res_num_list))
    print("===========================", res_str_list, " str_len: ", len(res_str_list))
    print("===========================", tmp_str_list, " tmp_len: ", len(tmp_str_list))
    
        
    
    