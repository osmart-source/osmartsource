//===-- Analyzer.cc - the kernel-analysis framework--------------===//
//
// This file implements the analysis framework. It calls the pass for
// building call-graph and the pass for finding security checks.
//
// ===-----------------------------------------------------------===//

#include "llvm/IR/LLVMContext.h"
#include "llvm/IR/PassManager.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/Verifier.h"
#include "llvm/Bitcode/BitcodeReader.h"
#include "llvm/Bitcode/BitcodeWriter.h"
#include "llvm/Support/ManagedStatic.h"
#include "llvm/Support/PrettyStackTrace.h"
#include "llvm/Support/ToolOutputFile.h"
#include "llvm/Support/SystemUtils.h"
#include "llvm/Support/FileSystem.h"
#include "llvm/IRReader/IRReader.h"
#include "llvm/Support/SourceMgr.h"
#include "llvm/Support/Signals.h"
#include "llvm/Support/Path.h"
#include <llvm/IR/DebugInfo.h>
#include <llvm/IR/Instructions.h>
#include <llvm/ADT/DenseMap.h>
#include <llvm/ADT/SmallPtrSet.h>
#include <llvm/ADT/StringExtras.h>
#include <llvm/Support/raw_ostream.h>
#include <llvm/Analysis/AliasAnalysis.h>
#include "llvm/Support/CommandLine.h"

#include <memory>
#include <vector>
#include <sstream>
#include <sys/resource.h>

// #include "taintsrc.h"
#include "globalfuncs.h"
// #include "controlFlow.h"
// #include "Analyzer.h"
// #include "CallGraph.h"
// #include "Config.h"
// #include "SecurityChecks.h"
// #include "MissingChecks.h"
// #include "PointerAnalysis.h"
// #include "TypeInitializer.h"

using namespace llvm;

// Command line parameters.
cl::list<std::string> InputFilenames(
    cl::Positional, cl::OneOrMore, cl::desc("<input bitcode files>"));

cl::opt<unsigned> VerboseLevel(
    "verbose-level", cl::desc("Print information at which verbose level"),
    cl::init(0));

cl::opt<bool> SecurityChecks(
    "sc", 
    cl::desc("Identify sanity checks"), 
    cl::NotHidden, cl::init(false));

// cl::opt<bool> MissingChecks(
// 		"mc",
// 		cl::desc("Identify missing-check bugs"),
// 		cl::NotHidden, cl::init(false));

// cl::opt<std::string> CFGFile(
// 	"cfgFile",
// 	cl::desc("store cfg dot"),
// 	cl::value_desc("store cfg dot"),
// 	cl::init(""));

// cl::opt<std::string> PDFile(
// 	"pdFile",
// 	cl::desc("store pd dot"),
// 	cl::value_desc("store pd dot"),
// 	cl::init(""));

// cl::opt<std::string> ResultFile(
// 	"resultFile",
// 	cl::desc("store dfs result"),
// 	cl::value_desc("store dfs result"),
// 	cl::init(""));

// cl::opt<std::string> CFGPythonFile(
// 	"cfgPy",
// 	cl::desc("process cfg's python"),
// 	cl::value_desc("process cfg's python"),
// 	cl::init(""));




// GlobalContext GlobalCtx;

void getModuleglobalvariable(Module*M){
    for(auto &GG:M->getGlobalList()){
        GlobalVariable *g1 = &GG;
		std::string gname = g1->getName().str();
		if(std::strstr(gname.c_str(),".str") == NULL)
        	errs()<<g1->getName()<<" ";
    }
	errs()<<"\n";
}
void IterativeModulePass::run(ModuleList &modules,std::string cfgfile,std::string pdfile,std::string resultfile,std::string cfgpyPath) {
	
	ModuleList::iterator i, e;
	errs() << "[" << ID << "] Initializing " << modules.size() << " modules ";
	bool again = true;
	//   while (again) {
	//     again = false;
	for (i = modules.begin(), e = modules.end(); i != e; ++i) {
		errs()<<cfgfile<<"\n";
		doInitialization(i->first,cfgfile,pdfile,resultfile,cfgpyPath);
		// errs() << ".";
	}
	//   }
	// errs() << "\n";
	int process = 0;
	for (i = modules.begin(), e = modules.end(); i != e; ++i) {
		errs() << "[" << ID << "] propecessing  " << i->second << " modules \n";
		doModulePass(i->first);

		// errs() << ".";
	}
}

GlobalContext GlobalCtx;
int main(int argc, char **argv) {

	// Print a stack trace if we signal out.
	sys::PrintStackTraceOnErrorSignal(argv[0]);
	PrettyStackTraceProgram X(argc, argv);

	llvm_shutdown_obj Y;  // Call llvm_shutdown() on exit.

	cl::ParseCommandLineOptions(argc, argv, "global analysis\n");
	SMDiagnostic Err;
	// std::string cfgfile = CFGFile;
	// std::string resultfile = ResultFile;
	// std::string pdfile = PDFile;
	// std::string cfgpyPath = CFGPythonFile;
	
	// Loading modules
	// errs() << "Total " << InputFilenames.size() << " file(s)\n";
	for (unsigned i = 0; i < InputFilenames.size(); ++i) {
                                                                                 
		LLVMContext *LLVMCtx = new LLVMContext();
		std::unique_ptr<Module> M = parseIRFile(InputFilenames[i], Err, *LLVMCtx);

		if (M == NULL) {
			errs() << argv[0] << ": error loading file '"
				<< InputFilenames[i] << "'\n";
			continue;
		}

		Module *Module = M.release();
		StringRef MName = StringRef(strdup(InputFilenames[i].data()));
		// errs()<<"\n module name is "<<MName<<"\n";
		GlobalCtx.Modules.push_back(std::make_pair(Module, MName));
		errs()<<"processing module:"<<Module->getName()<<"\n";
		errs()<<"globalvariables are: ";
		getModuleglobalvariable(Module);
		errs()<<"functions are: ";
		for(auto &F:*Module){
			if(F.isIntrinsic() || F.isDeclaration()){
				continue;
			}
			std::string funcname = F.getName().str();
			errs()<<funcname<<" ";
		}
		errs()<<"\n";
		// errs()<<"\n";
		// GlobalCtx.Modules.push_back(make_pair(Module, MName));
		// GlobalCtx.ModuleMaps[Module] = InputFilenames[i];
	}
	// TaintAnalysisPass TAPass(&GlobalCtx);
	// errs()<<cfgfile<<"\n";
	// TAPass.run(GlobalCtx.Modules,cfgfile,pdfile,resultfile,cfgpyPath);


	return 0;
}

