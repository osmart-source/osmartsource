# osmartsource
**The source code and comparison evaluation results of OSmart is here！**

## Environment: 
We conducted the experiment on a 96-core machine running Ubuntu 20.04.1 LTS with four Intel Xeon Platinum 8268 CPUs and 409 GB memory. We installed JOERN 1.1.1066 and used LLVM 13.0.

## Usage

Taking Libtiff/fax2ps as an example, we present the whole process, which can be seen in example-fax2ps.

The file structure is below:

libtiff/fax2ps

  | -- fax2ps: source code of fax2ps
  
  | -- fax2ps-ast: program AST dir
  
  | -- fax2ps-pdg: program PDG dir

  | -- fax2ps-cfg: program CFG dir

  | -- global.txt: custom functions and global variables 

  | -- div_flow.json: results of DIV extraction

  | -- iiv.json: results of impact analysis, containing IIVs and their option groups

  | -- nodeinfo.json: results of each node, such as source, dest, condition

  | -- og.json: results of summarized option groups

  | -- pass.json: results of DIV analysis

  | -- program_pdg.json: the whole program PDG

#### STEP 1 Extract options from source code based on AST
```
python3 parse_option.py libtiff/fax2ps/fax2ps-ast switch
```
This step will generate pass.json and div_flow.json and we need to specify whether the parsing way is *switch* or *if*.
#### STEP 2 Generate the whole program PDG 
```
python3 pdggenerate.py -programdir=libtiff/fax2ps/ -programname=fax2ps -startfunction=main
```
This step will generate program_pdg.json and nodeinfo.json. 

#### STEP 3 Execute the impact analysis 
```
python3 flownew_prodivflow.py -programdir=libtiff/fax2ps/ -programname=fax2ps -startfunction=main -anotherline=-1 -structreturnname=""
```
This step will generate iiv.json.

#### STEP 4 Summarize the option groups from the results of impact analysis
```
python3 ognew.py -programdir=libtiff/fax2ps/ -p fax2ps
```
This step will generate og.json.
We acquire the opion groups.


