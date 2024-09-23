import sys

def ReadAsm(filePath):
    asmLines = []
    i = 0
    with open(filePath, 'r', encoding='utf-8') as f:
        for line in f:
            if line[-1] == '\n':
                line = line[0:-1]
            if line == '':
                continue
            asmLines.append(line)
            # print(i, line)
            i += 1
    return asmLines


def Split2Functions(asmLines):
    funcRanges = []
    start = 0
    end = 0

    # 移到第一个函数的开头
    for i in range(len(asmLines)):
        line = asmLines[i]
        if isFunctionEnd(line):
            start = i
            end = i
            break   
    # 遍历函数
    for i in range(start, len(asmLines)):
        line = asmLines[i]
        if isFunctionEnd(line):
            end = i
            if end > start + 1:
                funcRanges.append((start, end)) # 不包括end
            start = i
    # 最后一个
    end = len(asmLines)
    if end > start + 1:
        funcRanges.append((start, end))

    return funcRanges

def Split2BBlocks(asmLines, funcRange):
    start = funcRange[0]
    end = funcRange[1]
    if start == end:
        return []
    
    funcName = asmLines[start]
    
    # 如果输入的文本没有函数头，则会提示no functions并退出程序
    try:
        right = funcName.index(':')
    except:
        print('There are no functions.')
        sys.exit(0)

    funcName = funcName[0:right]
    start += 1

    func = {'funcName': funcName, 'blocks': []}
    blocks = []
    block = {'bName': '', 'id': start}
    name2id = {}
    bStart = start
    bEnd = start
    for i in range(start, end):
        inst = asmLines[i]
        if isBlockEnd(inst, asmLines[i-1]):
            bEnd = i
            block['bRange'] = (bStart, bEnd)
            blocks.append(block)
            if inst[0] == '.':
                try:
                    right = inst.index(':')
                    block = {'bName': inst[0:right], 'id': i+1}
                    name2id[inst[0:right]] = i+1
                    bStart = i+1
                except:
                    block = {'bName': '', 'id': i+1}
                    bStart = i+1
            else:
                block = {'bName': '', 'id': i}
                bStart = i
        
    bEnd = end
    block['bRange'] = (bStart, bEnd)
    blocks.append(block)

    func['blocks'] = blocks
    func['name2id'] = name2id
    return func

def isFunctionEnd(line):
    return line[0] != ' ' and (line[0] != '.' or line.startswith('.omp_')) and (':' in line)

def isBlockEnd(inst, prevInst):
    return (inst[0] == '.' or (' ret' in prevInst) or isJumpInst(prevInst))

def isJumpInst(inst):
    tmp = inst.split()
    mnemonic = tmp[0]
    armJump = ['b','beq','bne','bcs','bhs','bcc','blo','bhi','bls','bge','blt','bgt','ble','brge','brlt','tbnz','tbz','cbnz','cbz']

    return ((mnemonic[0] == 'j') or (mnemonic in armJump))

def ConstructFuncs(filePath):
    asmLines = ReadAsm(filePath)
    funcRanges = Split2Functions(asmLines)
    funcs = []
    for fRange in funcRanges:
        func = Split2BBlocks(asmLines, fRange)
        funcs.append(func)

    jmps = ['jmp', 'b']
    conJmps = ['beq','bne','bcs','bhs','bcc','blo','bhi','bls','bge','blt','bgt','ble','brge','brlt','tbnz','tbz','cbnz','cbz',
               'jz','jnz','jc','jnc','jo','jno','js','jns','jp','jnp','je','jne','jcxz','jecxz','jrcxz','ja','jnbe','jae',
               'jnb','jb','jnae','jbe','jna','jg','jnle','jge','jnl','jl','jnge','jle']
    calls = ['call', 'bl', 'blx','bx']
    name2called = {}
    conFuncs = []
    funcname2lastInst = {}
    name2strData = {}
    strLabel = {}

    for func in funcs:
        conFunc = {'funcname': func['funcName']}
        blocks = []
        bb_addr_list = []
        call = []

        for b in func['blocks']:
            start = b['bRange'][0]
            end = b['bRange'][1]
            block = asmLines[start:end]
            addr_index = start

            # data block
            if b['bName'].startswith('.LC') or b['bName'].startswith('.L.str'):
                if b['bName'].startswith('.LCPI'): # clang-arm中的情况
                    for i in range(len(block)):
                        inst = block[i].split()
                        if inst[0] == '.long':
                            if i == 0:
                                label = b['bName']
                            else:
                                label = b['bName'] + '+' + str(i*4)
                            try:
                                j = inst[1].index('-')
                                strLabel[label] = inst[1][0:j]
                            except:
                                pass
                else:
                    inst = block[0].split()
                    strData = ' '.join(inst[1:])
                    if strData[0] == '"' and strData[-1] == '"':
                        name2strData[b['bName']] = strData[1:-1]
            # canonical block    
            else: 
                modBlock = []
                for i in range(len(block)):
                    inst = block[i].split()

                    if inst[0].startswith('.'):
                        if inst[0] == '.word': # gcc-arm中会出现的情况
                            if i == 0:
                                label = b['bName']
                            else:
                                label = b['bName'] + '+' + str(i*4)
                            if name2strData.get(inst[1]) != None:
                                name2strData[label] = name2strData[inst[1]]
                        addr_index += 1
                        continue

                    if inst[0] in calls: # 记录调用被调用
                        callName = inst[1]
                        if name2called.get(callName) != None:
                            name2called[callName].append(func['funcName'])
                        else:
                            name2called[callName] = [func['funcName']]
                        call.append(callName)

                    inst = ' '.join(inst)
                    modBlock.append(inst)
                    bb_addr_list.append(addr_index)
                    addr_index += 1
                if modBlock != []:
                    blocks.append(modBlock)

        # clang-arm中.long的情况
        if strLabel != {}:
            for key in strLabel:
                if name2strData.get(strLabel[key]) != None:
                    name2strData[key] = name2strData[strLabel[key]]

        if blocks != []:
            conFunc['blocks'] = blocks
            conFunc['bb_addr_list'] = bb_addr_list
            conFunc['call'] = call
            conFunc['bName2addr'] = func['name2id']
            
            conFuncs.append(conFunc)
            funcname2lastInst[func['funcName']] = blocks[-1][-1]


    # 边和被调用
    for conFunc in conFuncs:
        # 被调用
        if name2called.get(conFunc['funcname']) != None:
            conFunc['called'] = name2called[conFunc['funcname']]
        else:
            conFunc['called'] = []

        # 边 edges
        edges = []
        addr_index = 0
        bName2addr = conFunc['bName2addr']
        for block in conFunc['blocks']:
            curAddr = conFunc['bb_addr_list'][addr_index]
            inst = block[-1].split()
            if inst[0] in jmps:
                if bName2addr.get(inst[1]) != None:
                    edges.append((curAddr, bName2addr[inst[1]]))
            elif inst[0] in conJmps:
                if addr_index + len(block) < len(conFunc['bb_addr_list']):
                    edges.append((curAddr, conFunc['bb_addr_list'][addr_index+len(block)]))
                if bName2addr.get(inst[1]) != None:
                    edges.append((curAddr, bName2addr[inst[1]]))
            elif inst[0] in calls:
                if addr_index + len(block) < len(conFunc['bb_addr_list']):
                    if funcname2lastInst.get(inst[1]):
                        lastInst = funcname2lastInst[inst[1]].split()
                        if ('ret' in lastInst[0]) or ('pop' in lastInst[0]) or (lastInst == ['bx', 'lr']):
                            edges.append((curAddr, conFunc['bb_addr_list'][addr_index+len(block)]))
            else:
                if addr_index + len(block) < len(conFunc['bb_addr_list']):
                    edges.append((curAddr, conFunc['bb_addr_list'][addr_index+len(block)]))
            addr_index += len(block)
        
        conFunc['edges'] = edges
        
        del conFunc['bName2addr']
    
    print(name2strData)

    return conFuncs, name2strData
