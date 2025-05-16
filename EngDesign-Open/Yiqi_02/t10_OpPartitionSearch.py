#!/usr/bin/env python3

from typing import List, Optional, Tuple
import numpy as np

class OpSpatialPartitionSearch:
    class Node:
        def __init__(self, value: int = 1, parent = None, children = None):
            self.value: int = value
            self.parent = parent
            if self.parent == None:
                self.agg_value: int = self.value
            else:
                self.agg_value: int = self.parent.agg_value * self.value
            if children is None:
                self.children: List[OpSpatialPartitionSearch.Node] = []
            else:
                self.children = children
        
        def isRoot(self) -> bool:
            return self.parent is None
        
        def isLeaf(self) -> bool:
            return len(self.children) == 0
        
        def getPathToRoot(self) -> List[int]:
            path = []
            cur_node = self
            while cur_node is not None:
                path.append(cur_node.value)
                cur_node = cur_node.parent
            return path
            
        def getConfig(self) -> List[int]:
            return list(reversed(self.getPathToRoot()[:-1]))    # remove the redundant root value
    
    def __init__(self, depth: int = 7, tot_dim_size: List = [], filter_func_high = None, filter_func_low = None, dim_size_TH: float = 0.9, num_core: int = 0):
        self.root = OpSpatialPartitionSearch.Node()
        self.depth: int = depth
        self.dim_size_TH: float = dim_size_TH
        self.tot_dim_size: List[int] = tot_dim_size
        self.num_core: int = num_core
        if filter_func_high is None:
            # filter_func(cur_node_value, parent_node, tot_dim_size) -> bool
            self.filter_func_high = self.filter_by_tot_dim_size_high
        else:
            self.filter_func_high = filter_func_high
        if filter_func_low is None:
            # filter_func(cur_node_value, parent_node, tot_dim_size) -> bool
            self.filter_func_low = self.filter_by_tot_dim_size_low
        else:
            self.filter_func_low = filter_func_low

    # use this instead of lambda to avoid pickling error in __init__()
    # def dummy_noop_filter(self, x, y, z):
    #     return True

    # def generate_spatial_search_tree_helper(self, tot_dim_size, search_depth, cur_depth, cur_node: Node):
    #     if cur_depth >= search_depth:
    #         return
    #     for i in range(1, tot_dim_size + 1):
    #         if self.filter_func_low(i, cur_node, tot_dim_size) == False:
    #             continue
    #         if self.filter_func_high(i, cur_node, tot_dim_size) == False:
    #             break
    #         new_node = OpSpatialPartitionSearch.Node(value = i, parent = cur_node)
    #         cur_node.children.append(new_node)
    #         self.generate_spatial_search_tree_helper(tot_dim_size, search_depth, cur_depth + 1, new_node)

    # def generateSpatialSearchTreeRecursive(self, tot_dim_size):
    #     self.generate_spatial_search_tree_helper(tot_dim_size, self.depth, 0, self.root)

    def generateSpatialSearchTreeIterative(self):
        cur_level_nodes = [self.root]
        cur_depth = 0
        while cur_depth < self.depth:
            next_level_nodes = []
            for node in cur_level_nodes:
                max_remaining_dim_size = np.prod(self.tot_dim_size[cur_depth + 1:])
                min_start = np.floor(self.num_core*self.dim_size_TH / node.agg_value / max_remaining_dim_size)
                min_start = int(max(min_start, 1))
                min_start = int(min(min_start, self.tot_dim_size[cur_depth]))
                for i in range(min_start, self.tot_dim_size[cur_depth]+1):
                    if self.filter_func_high(i, node, cur_depth) == False:
                        break
                    new_node = OpSpatialPartitionSearch.Node(value = i, parent = node)
                    node.children.append(new_node)
                    next_level_nodes.append(new_node)
            cur_level_nodes = next_level_nodes
            cur_depth += 1
            print("cur_depth: ", cur_depth, "cur level num_nodes: ", len(cur_level_nodes))

    def generateSearchTree(self):
        self.generateSpatialSearchTreeIterative()

    # print the tree from root
    # each level of the tree is printed in a new line
    def printSearchTree(self):
        cur_level_nodes = [self.root]
        while len(cur_level_nodes) > 0:
            next_level_nodes = []
            cur_parent = cur_level_nodes[0].parent
            for node in cur_level_nodes:
                if node.parent != cur_parent:
                    print("; ")
                    cur_parent = node.parent
                print(node.value, end = " ")
                next_level_nodes.extend(node.children)
            print()
            cur_level_nodes = next_level_nodes
    
    # count number of leaf nodes
    def num_leaf_nodes(self, filter_func = None) -> int:
        if filter_func is None:
            filter_func = lambda x: True
        def num_leaf_nodes_helper(cur_node: OpSpatialPartitionSearch.Node) -> int:
            if cur_node.isLeaf() and filter_func(cur_node):
                return 1
            else:
                return sum([num_leaf_nodes_helper(child) for child in cur_node.children])
        return num_leaf_nodes_helper(self.root)

    def filter_by_tot_dim_size_high(self, cur_node_value, parent_node: Node, cur_depth) -> bool:
        return cur_node_value * parent_node.agg_value <= self.num_core

    def filter_by_tot_dim_size_low(self, cur_node_value, parent_node: Node, cur_depth) -> bool:
        return True
        # if parent_node.isRoot():
        #     return True
        # return tot_dim_size * dim_size_TH <= cur_node_value * parent_node.agg_value

    def filter_config_by_min_dim_size(self, node) -> bool:
        return True
        # return self.num_core * self.dim_size_TH <= node.agg_value

    # return List of configs, each config is a List of dims]
    def get_all_configs(self, filter_func = None) -> List[List[int]]:
        if filter_func is None:
            filter_func = self.filter_config_by_min_dim_size
        spatial_configs = []
        def get_config_from_leaf_node(node):
            if filter_func(node):
                spatial_configs.append(node.getConfig())
                return True
            else:
                return False
        self.num_leaf_nodes(get_config_from_leaf_node)
        return spatial_configs

# @lru_cache(maxsize=None)
def build_spatial_search_tree(depth: int = 7, tot_dim_size: List[int] = [], filter_func_high = None, filter_func_low = None,
                              dim_size_TH: float = 0.9, num_core: int = 0) -> Tuple[float, OpSpatialPartitionSearch]:
    import time
    start = time.perf_counter()
    search_tree = OpSpatialPartitionSearch(
        depth, tot_dim_size, filter_func_high, filter_func_low, dim_size_TH, num_core
    )
    search_tree.generateSearchTree()
    end = time.perf_counter()

    search_time = end - start
    print("Time to build spatial search tree:", search_time, "seconds; Threshold:", dim_size_TH, flush=True)

    return search_time, search_tree

class OpTemporalPartitionSearch:
    class Node:
        def __init__(self, value: Optional[List[int]] = None, parent = None, children = None):
            if value is None:
                self.value: List[int] = []
            else:
                self.value: List[int] = value
            self.parent = parent
            if self.parent == None:
                self.agg_value: List[int] = self.value
            else:
                self.agg_value: List[int] = [x * y for x, y in zip(self.parent.agg_value, self.value)]
            if children is None:
                self.children: List[OpTemporalPartitionSearch.Node] = []
            else:
                self.children = children
            self._config: Optional[List[List[int]]] = None  # memoization for self.getConfig()
        
        def isRoot(self) -> bool:
            return self.parent is None
        
        def isLeaf(self) -> bool:
            return len(self.children) == 0
        
        def getPathToRoot(self) -> List[List[int]]:
            path: List[List[int]] = []
            cur_node = self
            while cur_node is not None:
                path.append(cur_node.value)
                cur_node = cur_node.parent
            return path
            
        def getConfig(self) -> List[List[int]]:
            if self._config is None:
                self._config = list(reversed(self.getPathToRoot()[:-1])) # remove the redundant root value
            return self._config

    def __init__(self, depth: int = 7, search_space: Optional[List[List[List[int]]]] = None, num_replicas: Optional[List[int]] = None, filter_func = None):
        self.root = OpTemporalPartitionSearch.Node()
        self.depth: int = depth
        if search_space is None:
            self.search_space: List[List[List[int]]] = [[] for _ in range(depth)]
        else:
            self.search_space: List[List[List[int]]] = search_space
        self.search_space.sort()
        if num_replicas is None:
            self.num_replicas: List[int] = []
        else:
            self.num_replicas: List[int] = num_replicas
        if filter_func is None:
            # filter_func(cur_node_value, parent_node) -> bool
            self.filter_func = self.filter_by_dim_size

    def generateSearchTreeIterative(self):
        cur_level_nodes = [self.root]
        cur_depth = 0
        while cur_depth < self.depth:
            next_level_nodes = []
            for node in cur_level_nodes:
                for i in self.search_space[cur_depth]:
                    if self.filter_func(i, node) == False:
                        continue
                    new_node = OpTemporalPartitionSearch.Node(value = i, parent = node)
                    node.children.append(new_node)
                    next_level_nodes.append(new_node)
            cur_level_nodes = next_level_nodes
            cur_depth += 1
            # print("cur_depth: ", cur_depth, "cur level num_nodes: ", len(cur_level_nodes))

    def generateSearchTree(self):
        self.generateSearchTreeIterative()

    # print the tree from root
    # each level of the tree is printed in a new line
    def printSearchTree(self):
        print("#replicas: ", self.num_replicas)
        cur_level_nodes = [self.root]
        while len(cur_level_nodes) > 0:
            next_level_nodes = []
            cur_parent = cur_level_nodes[0].parent
            for node in cur_level_nodes:
                if node.parent != cur_parent:
                    print(";", end = " ")
                    cur_parent = node.parent
                print(node.value, end = " ")
                next_level_nodes.extend(node.children)
            print()
            cur_level_nodes = next_level_nodes
    
    # count number of leaf nodes
    def num_leaf_nodes(self, filter_func = None) -> int:
        if filter_func is None:
            filter_func = lambda x: True
        def num_leaf_nodes_helper(cur_node: OpTemporalPartitionSearch.Node) -> int:
            if cur_node.isLeaf() and filter_func(cur_node):
                return 1
            else:
                return sum([num_leaf_nodes_helper(child) for child in cur_node.children])
        return num_leaf_nodes_helper(self.root)

    def filter_by_dim_size(self, cur_node_value: List[int], parent_node: Node) -> bool:
        if parent_node.isRoot():
            return True

        for x, y, z in zip(cur_node_value, parent_node.agg_value, self.num_replicas):
            if x * y > z:
                return False
        
        return True

    # return List of configs, each config is a List of dims]
    def get_all_configs(self, filter_func = None) -> List[List[List[int]]]:
        if filter_func is None:
            filter_func = lambda x: True
        configs = []
        def get_config_from_leaf_node(node: OpTemporalPartitionSearch.Node):
            if filter_func(node):
                configs.append(node.getConfig())
                return True
            else:
                return False
        self.num_leaf_nodes(get_config_from_leaf_node)
        return configs

if __name__ == "__main__":
    op_partition_search = OpTemporalPartitionSearch(7, [[[1,1]],[[1,2]],[[2,1]],[[2,2]]], [2,2])
    op_partition_search.generateSearchTree()
    # op_partition_search.printSearchTree()
    configs = op_partition_search.get_all_configs()

    print("num configs: ", len(configs))

    # print spatial configs line by line
    for config in configs:
        print(config)

if False:
    op_partition_search = OpSpatialPartitionSearch(7, 1472)
    op_partition_search.generateSearchTree()
    # op_partition_search.printSearchTree()
    spatial_configs = op_partition_search.get_all_configs()

    print("num configs: ", len(spatial_configs))

    # print spatial configs line by line
    for config in spatial_configs:
        print(config)