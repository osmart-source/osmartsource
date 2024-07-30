#!/usr/bin/env python
# coding=utf-8
import argparse

from ognew_inner import getRequest

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-programdir","--programdir",metavar = "string",help = "programdir")
    parser.add_argument("-p","--p",metavar = "string",help = "p")
    
    arg = parser.parse_args()
    programname = arg.p
    programdir = arg.programdir
   
    getRequest(programdir,"",programname)
        
    