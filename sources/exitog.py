#!/usr/bin/env python
# coding=utf-8
# get exitog
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
# // "GUARD_EXIT"
def getexitogs(iivfilepath):
    exitfuncs = ["TIFFError","exit","usage","fatal","xexit","bfd_fatal","as_fatal","error","done","err","ErrFatal","lafe_errc","nasm_fatalf","cleanup_exit","cleanup_exit","w3m_exit","DROP_ERROR_INSTANCE"]
    # iivfile = "/home/cmd/OSmart/identitemp/libtiff/tiff2ps"
    # iivfilepath = os.path.join(iivfile,"iiv.json")
    with open(iivfilepath,"r") as f:
        iivs = json.load(f)
    exitogs = []
    iivars = iivs["iivariable"]
    print(len(iivars))
    i = 0
    for iivar in iivs["iivariable"]:
        i += 1
        # print(iivar,iivs["iivariable"][iivar]
        calledname = iivs["iivariable"][iivar]["calledname"]
        funcname = iivs["iivariable"][iivar]["funcname"]
        if calledname in exitfuncs:
            ogs = iivars[iivar]["optionname"]
            for og in ogs:
                if isinstance(og,list):
                    exitogs.append(tuple(og))
                elif isinstance(og,str):
                    exitogs.append(tuple(ogs))
                    break
                    
    exitogs = list(set(exitogs))
    return exitogs
            