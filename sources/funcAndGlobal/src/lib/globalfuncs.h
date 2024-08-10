#ifndef _GLOBAL_FUNCS_H
#define _GLOBAL_FUNCS_H


#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string>
#include <map>
#include <set>
#include <vector>

#include "llvm/ADT/Statistic.h"
#include "llvm/IR/DebugLoc.h"
#include "llvm/IR/IntrinsicInst.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/Metadata.h"
#include "llvm/IR/DebugInfo.h"

#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Support/GraphWriter.h"
#include "llvm/Support/FileSystem.h"
#include "llvm/Analysis/CFGPrinter.h"
#include "llvm/Analysis/CallGraph.h"

#include "llvm/ADT/SCCIterator.h"
#include "llvm/Transforms/Utils/BasicBlockUtils.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"
#include "llvm/IR/InstIterator.h"
#include "llvm/IR/Instruction.h"
#include "llvm/IR/Instructions.h"


#include "llvm/IR/CFG.h"
#include "llvm/Analysis/AliasAnalysis.h"
#include "llvm/IR/GlobalAlias.h"
#include "llvm/IR/Value.h"
#include "llvm/IR/Constants.h"
#include "llvm/IR/ValueHandle.h"
#include "llvm/IR/InlineAsm.h"
#include "llvm/IR/Type.h"

using namespace llvm;
#define MAX_VERTEX_NUM 35536
//存储所有模块中define的函数名称

typedef std::map<Module *,std::set<std::string>> Modulemap;
typedef std::vector< std::pair<llvm::Module*, llvm::StringRef> > ModuleList;

typedef struct ArcNode{
    int adjvex;
    struct ArcNode *nextarc;
}ArcNode;

typedef struct VNode{
    std::string bb_name;
    //unsigned int cur_loc;
    int outdegree;
    int indegree;
    bool visited;
    unsigned int loop_stat; //0: undetected, 1: in detection prog, 2: all succ_bb detected 
    unsigned int loop_cnt;
    int loop_pre_bb_num[10];
    ArcNode *firarc;
}VNode, AdjList[MAX_VERTEX_NUM];

typedef struct ALGraph{
    int vexnum;
    int arcnum;
    AdjList list;
}ALGraph;

class GlobalContext {
private:
  // pass specific data
//   std::map<std::string, void*> PassData;

public:
    //map module to its defined functions
    Modulemap Modulefuncs;
    std::map<std::string,std::string>  GlobalFuncAlias;
    //all modules to be prepocessed
    ModuleList Modules;
    std::set<std::string> InvolvedModules;

    // // Map global object name to object definition
    // GObjMap Gobjs;

    // // Map global function name to function defination
    // FuncMap Funcs;

    // // Map function pointers (IDs) to possible assignments
    // FuncPtrMap FuncPtrs;

    // // functions whose addresses are taken
    // FuncSet AddressTakenFuncs;

    // // Map a callsite to all potential callee functions.
    // CalleeMap Callees;

    // // Map a function to all potential caller instructions.
    // CallerMap Callers;

    // // Indirect call instructions
    // std::vector<CallInst *>IndirectCallInsts;

    // // Map function signature to functions
    // DenseMap<size_t, FuncSet>sigFuncsMap;

    // // Map global function name to function.
    // NameFuncMap GlobalFuncs;

    // Unified functions -- no redundant inline functions
    // DenseMap<size_t, Function *>UnifiedFuncMap;
    // set<Function *>UnifiedFuncSet;

    // /****** Alias Analysis *******/
    // FuncPointerAnalysisMap FuncPAResults;
    // FuncAAResultsMap FuncAAResults;

    /****** Leak struct **********/
    //LeakStructMap leakStructMap;

    /****************** Flexible Structural Object Identification **************/

    // map structure to allocation site
    // AllocInstMap allocInstMap;

    // map structure to leak site
    // LeakInstMap leakInstMap;

    // map structure to syscall entry reaching allocation site
    // AllocSyscallMap allocSyscallMap;
    
    // // map structure to syscall entry reaching leak site
    // //LeakSyscallMap leakSyscallMap;

    // // map module to set of used flexible structure
    // ModuleStructMap moduleStructMap;

    // map flexible structure to module
    //StructModuleMap structModuleMap;

    //LeakerList leakerList;

    // mbuf leak api
    // FuncSet LeakAPIs;

    // // device permission allow function list and deny function list
    // FuncSet devAllowList;
    // FuncSet devDenyList;

    /**************** End Flexible Structural Object Identification ************/
    
    /****************** Flexible Structural Object Evaluation **************/
    //LeakerLayout leakerLayout;
    // LeakerICmpMap leakerICmpMap;
    /**************** End Flexible Structural Object Evaluation ************/

    // A factory object that knows how to manage AndersNodes
    // AndersNodeFactory nodeFactory;

    
};

class IterativeModulePass {
protected:
  GlobalContext *Ctx;
  const char *ID;
public:
  IterativeModulePass(GlobalContext *Ctx_, const char *ID_)
    : Ctx(Ctx_), ID(ID_) { }

  // run on each module before iterative pass
  virtual bool doInitialization(Module *M,std::string cfgfile,std::string pdfile,std::string resultfile,std::string cfgpyPath)
    { return true; }

  // run on each module after iterative pass
  virtual bool doFinalization(Module *M)
    { return true; }

  // iterative pass
  virtual bool doModulePass(Module *M)
    { return false; }

  virtual void run(ModuleList &modules,std::string cfgfile,std::string pdfile,std::string resultfile,std::string cfgpyPath);
};

#endif