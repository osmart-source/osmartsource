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
#include "llvm/IR/Value.h"
#include "llvm/IR/Constants.h"
#include "llvm/IR/ValueHandle.h"
#include "llvm/IR/InlineAsm.h"

using namespace llvm;

std::map<Module *,std::set<std::string>> modulefuncs;
//收集一个模块中涉及到的所有的函数（define not declare）
void getModulefunc(Module *M){
    for(auto &F:*M){
        for(auto &B:F){
            // errs()<<"function is "<<F.getName()<<"\n";
            std::string funcname = F.getName().str();
            modulefuncs[M].insert(funcname);
            break;
        }
    }
}

void getModuleglobalvariable(Module*M){
    for(auto &GG:M->getGlobalList()){
        GlobalVariable *g1 = &GG;
        errs()<<g1->getName()<<" ";
    }
}