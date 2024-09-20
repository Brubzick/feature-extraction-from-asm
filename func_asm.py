from read_asm import ConstructFuncs
from cfg_constructor_asm import get_cfg_asm
from discovRe_asm import get_discoverRe_feature
from raw_graphs import *
from graph_analysis_asm import *

def get_func_cfgs_disasm(filePath, fileName):

    funcs, name2strData = ConstructFuncs(filePath)

    raw_cfgs = raw_graphs(fileName)

    for func in funcs:
        func_name = func['funcname']
        cfg = get_cfg_asm(func, name2strData)
        func_f = get_discoverRe_feature(func, cfg, name2strData)
        raw_g = raw_graph(func_name, cfg, func_f)
        raw_cfgs.append(raw_g)

    return raw_cfgs
