import networkx as nx
import itertools
import sys
sys.setrecursionlimit(10000)

class raw_graph:
    def __init__(self, funcname, g, func_f):
        '''
		funcname:函数名
		g: Genius的ACFG
		func_f:DiscovRe的特征
		'''
        self.funcname = funcname
        self.old_g = g
        self.g = nx.DiGraph()
        self.discovre_features = func_f
        self.attributing()

    def __len__(self):
        return len(self.g)

    def attributing(self):
        self.obtainOffsprings(self.old_g)
        for node in self.old_g:
            fvector = self.retrieveVec(node, self.old_g)
            self.g.add_node(node)
            self.g.nodes[node]['v'] = fvector

        for edge in self.old_g.edges():
            node1 = edge[0]
            node2 = edge[1]
            self.g.add_edge(node1, node2)

    def obtainOffsprings(self, g):
        nodes = g.nodes()
        for node in nodes:
            offsprings = {}
            self.getOffsprings(g, node, offsprings)
            g.nodes[node]['offs'] = len(offsprings)
        return g

    def getOffsprings(self, g, node, offsprings):
        node_offs = 0
        sucs = g.successors(node)
        for suc in sucs:
            if suc not in offsprings:
                offsprings[suc] = 1
                self.getOffsprings(g, suc, offsprings)


    def retrieveVec(self, id_, g):
        feature_vec = []
        # numC0
        numc = g.nodes[id_]['consts']
        feature_vec.append(numc)
        # nums1
        nums = g.nodes[id_]['strings']
        feature_vec.append(nums)
        # offsprings2
        offs = g.nodes[id_]['offs']
        feature_vec.append(offs)
        # numAs3
        numAs = g.nodes[id_]['numAs']
        feature_vec.append(numAs)
        # of calls4
        calls = g.nodes[id_]['numCalls']
        feature_vec.append(calls)
        # of insts5
        insts = g.nodes[id_]['numIns']
        feature_vec.append(insts)
        # of LIs6
        insts = g.nodes[id_]['numLIs']
        feature_vec.append(insts)
        # of TIs7
        insts = g.nodes[id_]['numTIs']
        feature_vec.append(insts)
        return feature_vec

    def enumerating(self, n):
        subgs = []
        # pdb.set_trace()
        for sub_nodes in itertools.combinations(self.g.nodes(), n):
            subg = self.g.subgraph(sub_nodes)
            u_subg = subg.to_undirected()
            if nx.is_connected(u_subg):
                subgs.append(subg)
        return subgs

    def genMotifs(self, n):
        motifs = {}
        subgs = self.enumerating(n)
        for subg in subgs:
            if len(motifs) == 0:
                motifs[subg] = [subg]
            else:
                nomatch = True
                for mt in motifs:
                    if nx.is_isomorphic(mt, subg):
                        motifs[mt].append(subg)
                        nomatch = False
                if nomatch:
                    motifs[subg] = [subg]
        return motifs
    
class raw_graphs:  # 二进制文件内的所有原生控制流图
    def __init__(self, binary_name):
        self.binary_name = binary_name
        self.raw_graph_list = []

    def append(self, raw_g):
        self.raw_graph_list.append(raw_g)

    def __len__(self):
        return len(self.raw_graph_list)    