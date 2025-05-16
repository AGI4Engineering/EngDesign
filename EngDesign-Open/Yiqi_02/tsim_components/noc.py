import numpy as np
from typing import Any, Dict, List, Optional, Tuple, Union, Set
from enum import Enum
from math import ceil

from collections.abc import Callable


def mesh_contention_function(num_transfers:int) -> float:
    return (1.0 / (2.0*num_transfers))

def torus_contention_function(num_transfers:int) -> float:
    return (1.0 / num_transfers)

def all_contention_function(num_transfers:int) -> float:
    return (1.0 / num_transfers)

class Topo(Enum):
    MESH = 1
    TORUS = 2
    ALL = 3

class NoC:
    def __init__(self, 
                 bandwidth_bytepc:float,
                 topology:Topo,
                 contention_function:Callable=None) -> None:
        self.bandwidth_bytepc = bandwidth_bytepc
        if contention_function == None:
            self.contention_function = self.default_contention_function
        self.topology = topology

    def default_contention_function(self, num_transfers:int) -> float:
        if self.topology == Topo.MESH or self.topology == Topo.MESH.value:
            return mesh_contention_function(num_transfers)
        elif self.topology == Topo.TORUS or self.topology == Topo.TORUS.value:
            return torus_contention_function(num_transfers)
        elif self.topology == Topo.ALL or self.topology == Topo.ALL.value:
            return all_contention_function(num_transfers)
        else:
            assert False, "Unknown topology, no contention function specified."

    def num_cycle_of_access(self, num_bytes:int,
                            num_transfers:int) -> float:
        return num_bytes / self.bandwidth_bytepc / self.contention_function(num_transfers)

    def get_switch_area(self) -> int:
        '''
        Returns the area of a single switch in the NoC in square mm.
        Reference switch has 10-bit input and outputs.
        TODO: scale control logic and datapath logic size separately instead of scaling everything linearly.
        '''
        num_wires = self.bandwidth_bytepc * 8 # One wire for each bit
        reference_num_wires = 10
        reference_switch_area_sq_um = 22545 # https://ieeexplore.ieee.org/document/8358473
        area_scaling_factor_45_to_7 = 8.041 # DeepScaleTool
        noc_switch_area_sq_um = reference_switch_area_sq_um /area_scaling_factor_45_to_7 * num_wires / reference_num_wires 
        noc_switch_area_sq_mm = noc_switch_area_sq_um / (1000 ** 2)
        return noc_switch_area_sq_mm


    # get shift info
    def get_total_cycles_from_expression(self,
                                         tensor_sizes:List[int],
                                         temporal_var_replicas:List[int],
                                         spatial_var_replicas:List[int],
                                         shift_info:tuple,
                                         num_bytes_per_elem:int=2) -> Tuple[float, float, float]:

        total_shift_size, shifted_dim, shifted_iter, shifted_vars, sub_op_var_sizes = shift_info

        all_broadcast_cycles = 0
        all_all_reduce_cycles = 0

        transfer_amount_list = []
        num_of_transfers_list = []
        for (i, (temporal_var_replica, spatial_var_replica, size)) in enumerate(zip(temporal_var_replicas,
                                                                                    spatial_var_replicas,
                                                                                    tensor_sizes)):
            # for each dimension...
            
            # broadcast (if input w/ > 1 spatial)
            # if 1 -> just load from HBM
            if i != 0:
                # add 1x size transfer for every spatial copy
                # number of spatial partitions *realized* is reduced by a factor of temporal_var_replicas
                assert ceil(spatial_var_replica/temporal_var_replica) - 1 >= 0
                broadcast_transfer_amount = size*(ceil(spatial_var_replica/temporal_var_replica) - 1)
            else:
                # first tensor is the output, it will not be broadcast
                broadcast_transfer_amount = 0

            # all-reduce (if output w/ > 1 spatial)
            # if 1 -> just write to HBM
            if i == 0:
                n = ceil(spatial_var_replica/temporal_var_replica)
                assert n > 0
                if n == 1:
                    all_reduce_transfer_amount = 0
                elif n == 2:
                    all_reduce_transfer_amount = size
                elif n > 2:
                    # ring all reduce uses (n-1)/n bandwidth
                    # 1 store to HBM + n-1 shares of size n
                    all_reduce_transfer_amount = size*(1+((n-1)/n)) # data per chunk is 1 / n
                else:
                    assert False, "Dead end branch, unreachable"
            else:
                all_reduce_transfer_amount = 0

            broadcast_cycles = self.num_cycle_of_access(broadcast_transfer_amount, 1)
            all_broadcast_cycles += broadcast_cycles

            all_reduce_cycles = self.num_cycle_of_access(all_reduce_transfer_amount, temporal_var_replica)
            all_all_reduce_cycles += all_reduce_cycles
        
        # shifting (if > 1 temporal partition)
        shift_cycles = 0
        if total_shift_size != 0:
            shifted_sizes = [sum([tensor_sizes[i] for i in vars]) for vars in shifted_vars]
            # this is meant to ensure the loop construction minimizes data movement
            order = np.argsort(-np.array(shifted_sizes))

            iter_count = 1
            for i, o in enumerate(order):
                hops = 1
                if i > 1:
                    # once we reach > 2 dimensions, have to start flattenting
                    # print("here")
                    hops = temporal_var_replicas[order[i-2]]

                shift_size = iter_count*shifted_sizes[o]*shifted_iter[o]*hops
                iter_count *= (shifted_iter[o]+1)

                cycles = self.num_cycle_of_access(shift_size, i+1)
                shift_cycles += cycles

                
        # if shift_cycles > 0:
        # print(f"{broadcast_cycles} + {shift_cycles} + {all_reduce_cycles} = {broadcast_cycles + shift_cycles + all_reduce_cycles}")
        return int(all_broadcast_cycles), int(shift_cycles), int(all_all_reduce_cycles) # broadcast, (compute) shifts, reduce

            
