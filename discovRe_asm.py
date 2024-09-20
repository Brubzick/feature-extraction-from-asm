from graph_analysis_asm import *

def get_discoverRe_feature(func, cfg, name2strData):
	features = []
	FunctionCalls = getFuncCalls(cfg)
	#1
	features.append(FunctionCalls)
	LogicInstr = getLogicInsts(cfg)
	#2
	features.append(LogicInstr)
	Transfer = getTransferInsts(cfg)
	#3
	features.append(Transfer)
	Locals = getLocalVariables(func)
	#4
	features.append(Locals)
	BB = getBasicBlocks(cfg)
	#5
	features.append(BB)
	Edges = len(cfg.edges)
	#6
	features.append(Edges)
	Incoming = getIncommingCalls(func)
	#7
	features.append(Incoming)
	Instrs = getIntrs(cfg)
	#8
	features.append(Instrs)
	between = retrieveGP(cfg)
	#9
	features.append(between)

	strings, consts = getfunc_consts(cfg, name2strData)
	features.append(strings)
	features.append(consts)
	return features