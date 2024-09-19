import networkx as nx

# No. of calls
def getFuncCalls(cfg, arch):
    sumcall = 0
    for node in cfg.nodes:
        block = cfg.nodes[node]['block']
        callmun = calCalls(block, arch)
        sumcall += callmun
    return sumcall

def calCalls(block, arch):
    if arch == 'x86':
        calls = {'call': 1}
    elif arch == 'arm':
        calls = {'bl': 1, 'blx': 1, 'bx': 1}
    else:
        calls = {'jal': 1, 'jalr': 1}

    callnum = 0
    for ins in block:
        ins = ins.split()
        if ins[0] in calls:
            callnum += 1

    return callnum

# No. of logic instructions
def getLogicInsts(cfg,arch):
    sumInsts = 0
    for node in cfg.nodes:
        block = cfg.nodes[node]['block']
        instNum = calLogicInstructions(block,arch)
        sumInsts += instNum
    return sumInsts

def calLogicInstructions(bl, arch):
    if arch == 'x86':
        calls = {'and': 1, 'andn': 1, 'andnpd': 1, 'andpd': 1, 'andps': 1, 'andnps': 1, 'test': 1, 'xor': 1, 'xorpd': 1,
                'pslld': 1}
    elif arch == 'arm':
        calls = {'and': 1, 'orr': 1, 'eor': 1, 'bic': 1, 'mvn': 1, 'tst': 1, 'teq': 1, 'cmp': 1, 'cmn': 1}
    else:
        calls = {'and': 1, 'andi': 1, 'or': 1, 'ori': 1, 'xor': 1, 'nor': 1, 'slt': 1, 'slti': 1, 'sltu': 1}

    invoke_num = 0
    for ins in bl:
        ins = ins.split()
        if ins[0] in calls:
            invoke_num += 1

    return invoke_num

# No. of transfer instructions
def getTransferInsts(cfg,arch):
    sumInsts = 0
    for node in cfg.nodes:
        block = cfg.nodes[node]['block']
        instNum = calTransferIns(block,arch)
        sumInsts += instNum
    return sumInsts

def calTransferIns(bl, arch):
    if arch == 'x86':
        calls = {'jmp': 1, 'jz': 1, 'jnz': 1, 'js': 1, 'je': 1, 'jne': 1, 'jg': 1, 'jle': 1, 'jge': 1, 'ja': 1, 'jnc': 1,
                'call': 1}
    elif arch == 'arm':
        calls = {'mvn': 1, "mov": 1}
    else:
        calls = {'beq': 1, 'bne': 1, 'bgtz': 1, "bltz": 1, "bgez": 1, "blez": 1, 'j': 1, 'jal': 1, 'jr': 1, 'jalr': 1}

    invoke_num = 0
    for ins in bl:
        ins = ins.split()
        if ins[0] in calls:
            invoke_num += 1

    return invoke_num

# No. basic blocks
def getBasicBlocks(cfg):
    nodes = cfg.nodes
    return len(nodes)

# Between
def retrieveGP(g):
    bf = betweeness(g)
    x = sorted(bf.values())
    if len(x) == 0:
        value = sum(x)
    else:
        value = sum(x)/len(x)
    return round(value,5)

def betweeness(g):
	#pdb.set_trace()
	betweenness = nx.betweenness_centrality(g)
	return betweenness

# No. of instructions
def getIntrs(cfg):
    sumIns = 0
    for node in cfg.nodes:
        ins_addr_list = cfg.nodes[node]['ins_addr_list']
        insNum = calInsts(ins_addr_list)
        sumIns += insNum
    return sumIns

def calInsts(insts):
    num = len(insts)
    return num

# No. of local variables
def getLocalVariables(func):
    return func['argsNum']

# No. of being called
def getIncommingCalls(func):
    return len(func['called'])

# constants
def getfunc_consts(cfg,arch):
    strings = []
    consts = []
    for node in cfg.nodes:
        block = cfg.nodes[node]['block']
        strs = getBBstrings(block, arch)
        cons = getBBconsts(block, arch)
        strings += strs
        consts += cons
    
    return strings, consts

def getBBstrings(block, arch):
    if arch == 'x86':
        calls = ['jz','jnz','jc','jnc','jo','jno','js','jns','jp','jnp','je','jne','jcxz','jecxz','jrcxz',
                'ja','jnbe','jae','jnb','jb','jnae','jbe','jna','jg','jnle','jge','jnl','jl','jnge','jle',
                'jmp','call','mov']
    elif arch == 'arm':
        calls = ['beq','bne','bcs','bcc','bmi','bpl','bvs','bvc','bhi','bls','bge','blt','bgt','ble','bal',
                 'bxeq','bxne','bxcs','bxcc','bxmi','bxpl','bxvs','bxvc','bxhi','bxls','bxge','bxlt','bxgt','bxle','bxal',
                 'bleq','blne','blcs','blcc','blmi','blpl','blvs','blvc','blhi','blls','blge','bllt','blgt','blle','blal',
                 'blxeq','blxne','blxcs','blxcc','blxmi','blxpl','blxvs','blxvc','blxhi','blxls','blxge','blxlt','blxgt','blxle','blxal',
                 'str', 'mov', 'bl', 'b', 'bx', 'blx']
    else:
        calls = ['la', 'jalr', 'call', 'jal']

    strings = []
    for ins in block:
        ins = ins.split()
        if ins[0] in calls:
            continue
        
        datas = []
        for i in range(len(ins)):
            if ins[i][0] == '{':
                if ins[i][-1] == '}':
                    data = ins[i]
                    datas.append(data)
                else:
                    start = i
            elif ins[i][-1] == '}':
                end = i
                data = ' '.join(ins[start:end+1])
                datas.append(data)
    
        for data in datas:
            if '"' in data:
                start = data.find('"')
                end = data.rfind('"')
                if start < end:
                    s = data[start+1:end]
                strings.append(s)
    return strings

def getBBconsts(opcode, arch):
    if arch == 'x86':
        calls = ['jz','jnz','jc','jnc','jo','jno','js','jns','jp','jnp','je','jne','jcxz','jecxz','jrcxz',
                'ja','jnbe','jae','jnb','jb','jnae','jbe','jna','jg','jnle','jge','jnl','jl','jnge','jle',
                'jmp','call','mov']
    elif arch == 'arm':
        calls = ['beq','bne','bcs','bcc','bmi','bpl','bvs','bvc','bhi','bls','bge','blt','bgt','ble','bal',
                 'bxeq','bxne','bxcs','bxcc','bxmi','bxpl','bxvs','bxvc','bxhi','bxls','bxge','bxlt','bxgt','bxle','bxal',
                 'bleq','blne','blcs','blcc','blmi','blpl','blvs','blvc','blhi','blls','blge','bllt','blgt','blle','blal',
                 'blxeq','blxne','blxcs','blxcc','blxmi','blxpl','blxvs','blxvc','blxhi','blxls','blxge','blxlt','blxgt','blxle','blxal',
                 'moveq','movne','movcs','movcc','movmi','movpl','movvs','movvc','movhi','movls','movge','movlt','movgt','movle','moval',
                 'ldr', 'str', 'mov', 'bl', 'b', 'bx', 'blx']
    else:
        calls = ['la', 'jalr', 'call', 'jal']

    consts = []
    for ins in opcode:
        ins = ins.split()
        if ins[0] in calls:
            continue
        for op in ins:
            if op[-1] == ',':
                op = op[:-1]
            
            if arch == 'x86':
                if op.isdigit():
                    consts.append(int(op))
                elif op.startswith('0x'):
                    op = op[2:]
                    try:
                        con = int(op,16)
                        consts.append(con)
                    except:
                        pass
            
            elif arch == 'arm':
                if op.startswith('#0x'):
                    op = op[3:]
                    try:
                        con = int(op,16)
                        consts.append(con)
                    except:
                        pass
                elif op.startswith('#'):
                    op = op[1:]
                    if op.isdigit():
                        consts.append(int(op))
    
    return consts
        
def calArithmeticIns(bl,arch):
    # 定义各架构中的算术指令
    if arch == 'x86':
        calls = {'add': 1, 'sub': 1, 'div': 1, 'imul': 1, 'idiv': 1, 'mul': 1, 'shl': 1, 'dec': 1, 'inc': 1}
    elif arch == 'arm':
        calls = {'add': 1, 'sub': 1, 'mul': 1, 'mla': 1, 'mls': 1, 'sdiv': 1, 'udiv': 1, 'rsb': 1, 'rsc': 1}  # ARM 架构中的算术指令
    else:
        calls = {'add': 1, 'addu': 1, 'addi': 1, 'addiu': 1, 'mult': 1, 'multu': 1, 'div': 1, 'divu': 1}

    invoke_num = 0
    for ins in bl:
        ins = ins.split()
        if ins[0] in calls:
            invoke_num += 1

    return invoke_num

def retrieveExterns(bl, call):
    externs = []
    for ins in bl:
        if call == []: break
        extern = call[-1]
        if extern in ins:
            externs.append(extern)
            call.pop()
    return externs