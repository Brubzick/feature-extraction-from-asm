import networkx as nx
from graph_analysis_asm import *

def get_cfg_asm(func, name2strData):
    cfg = nx.DiGraph()
    addr2node_id = {}
    addrIndex = 0
    for block in func['blocks']:
        node_id = len(cfg)
        cfg.add_node(node_id)
        bb_addr = func['bb_addr_list'][addrIndex]
        addr2node_id[bb_addr] = node_id
        cfg.nodes[node_id]['addr'] = bb_addr
        cfg.nodes[node_id]['ins_addr_list'] = func['bb_addr_list'][addrIndex : addrIndex+len(block)]
        cfg.nodes[node_id]['block'] = block
        cfg.nodes[node_id]['suc'] = []
        cfg.nodes[node_id]['pre'] = []
        
        addrIndex += len(block)

    for edge in func['edges']:
        if (addr2node_id.get(edge[0]) == None or addr2node_id.get(edge[1]) == None):
            continue
        node1 = addr2node_id[edge[0]]
        node2 = addr2node_id[edge[1]]
        cfg.add_edge(node1, node2)
        cfg.nodes[node1]['suc'].append(node2)
        cfg.nodes[node2]['pre'].append(node1)
    
    cfg = attributingRe(cfg, func, name2strData)

    return cfg
        

def attributingRe(cfg, func, name2strData):  # 为每个基本块生成自定义的属性
    call = func['call'].copy()
    call.reverse()
    for node_id in cfg:
        bl = cfg.nodes[node_id]['block']
        numIns = calInsts(bl)  # No. of Instruction
        cfg.nodes[node_id]['numIns'] = numIns
        numCalls = calCalls(bl)  # No. of Calls
        cfg.nodes[node_id]['numCalls'] = numCalls
        numLIs = calLogicInstructions(bl)  # 这个不再Genius的范围内
        cfg.nodes[node_id]['numLIs'] = numLIs
        numAs = calArithmeticIns(bl)  # No. of Arithmetic Instructions
        cfg.nodes[node_id]['numAs'] = numAs
        strings = getBBstrings(bl, name2strData)  # String and numeric constants
        consts = getBBconsts(bl)
        cfg.nodes[node_id]['numNc'] = len(strings) + len(consts)
        cfg.nodes[node_id]['consts'] = consts
        cfg.nodes[node_id]['strings'] = strings
        externs = retrieveExterns(bl, call)
        cfg.nodes[node_id]['externs'] = externs
        numTIs = calTransferIns(bl)  # No. of Transfer Instruction
        cfg.nodes[node_id]['numTIs'] = numTIs
    return cfg