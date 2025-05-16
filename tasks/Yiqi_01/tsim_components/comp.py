import numpy as np
from . import utils
from typing import Any, Dict, List, Optional, Tuple, Union, Set
# from icbm_DNNProgram import TensorOperator

def get_num_comp_iter(temporal_dim_var_parts:List[List[int]]) -> int:
    num_iter = np.prod(np.max(temporal_dim_var_parts,axis=-1))
    assert(num_iter >= 1), "num_iter should be greater than 1"
    return num_iter


class Compute:

    class OP:
        def __init__(self, 
                     # elementwise or matmul
                     is_ew:bool,
                     # C = A @ B
                     # C [ [[0],[1]], \
                     # A   [[0],[2]], \
                     # B   [[2],[1]] ]
                     # 
                     # Output = conv(Input, Kernel)
                     # O [ [[0],[1],[3  ],[4  ]], \
                     # I   [[0],[2],[3,5],[4,6]], \
                     # K   [[2],[1],[5  ],[6  ]] ]
                     variables:List[List[List[int]]],
                     #  0:m, 1:n, 2:k
                     # [1600, 80, 1600]
                     #
                     #  0:batch, 1:out_chl, 2:in_chl, 3:out_hei, 4:out_wid, 5:ker_hei, 6:ker_wid
                     # [50,      60,        30,       256,       768,       3,         5]
                     dim_lengths:List[int],
                     #  out,   in,    in
                     # [False, False, False]
                     is_ignored_list:List[bool],
                     #  out, in, in
                     # [0,   1,  2]
                     tensor_id_list:List[int]) -> None:
            
            assert len(variables) == len(is_ignored_list), \
                "variables and is_ignored_list should have same length"
            assert len(variables) == len(tensor_id_list), \
                "variables and tensor_id_list should have same length"
            
            self.is_ew = is_ew
            self.variables = variables
            self.dim_lengths = dim_lengths
            self.is_ignored_list = is_ignored_list
            self.tensor_id_list = tensor_id_list

    def __init__(self, 
                 # pad width/shape required by core arch
                 ew_pad_len:int, mm_pad_shape:np.ndarray,
                 # number(s) of data reuse limited by core arch [output, input1, input2] (mmpad shape)
                 ew_reuse_num:int, mm_reuse_list:list, 
                 # flop per cycle limited by core arch 
                 ew_flopc:int, mm_flopc:int,
                
                 # load/store bandwidth limited by core arch - local sram bw
                 load_store_bw_bytepc:float, 
                 # 2 if fp16, 4 if fp32
                 byte_per_elem:int,
                
                 # cycles to init matmul computation
                 mm_init_cycle:int = 0,
                 # whether elementwise and matmul computations can overlap
                 ew_mm_overlap:bool = True) -> None:
        
        # self.tensor_id = 0 # track highest assigned tensor id.
        
        self.ew_pad_len = ew_pad_len
        self.mm_pad_shape = mm_pad_shape
        self.ew_reuse_num = ew_reuse_num
        self.mm_reuse_list = mm_reuse_list
        self.ew_flopc = ew_flopc
        self.mm_flopc = mm_flopc
        self.load_store_bw_bytepc = load_store_bw_bytepc
        self.byte_per_elem = byte_per_elem

        self.mm_init_cycle = mm_init_cycle
        self.ew_mm_overlap = ew_mm_overlap

        #State for marking unconditional writes

    def get_area(self):
        '''Return the compute logic area for a core. We currently assume area contributions
        from parts other than SA/VU are negligible.'''
        sa_128_128_sq_mm = 65.17333 # 128 x 128 systolic array, TSMC N7
        vu_128_8_2_sq_mm = 11.3942 # 128 x 8 x 2 vector unit, TSMC N7 (128 x 8 x 2 ALUs <- = ops per cycle)
        
        sa_scale_factor = (self.mm_pad_shape[-1] / 128) ** 2
        vu_scale_factor = self.ew_flopc / 2048

        sa_area = sa_128_128_sq_mm * sa_scale_factor
        vu_area = vu_128_8_2_sq_mm * vu_scale_factor
        return sa_area + vu_area, sa_area, vu_area

    # get per tensor load/store cycles for elementwise
    # return: np.ndarray for cycles [56 cycles, 70 cycles, 80 cycles]
    def get_ew_load_store_cycles_from_padded_tile(self, 
                                                  variables:List[List[List[int]]],
                                                  dim_lengths:List[int]) -> np.ndarray:
        # format variables and dim_lengths to np array
        variables_np = []
        for var in variables:
            variables_np.append(utils.pad_to_dense(var))
        dim_lengths_np = np.append(dim_lengths,0)

        # get tensor sizes
        sizes = [utils.shape_to_size(utils.var_to_shape(dim_lengths_np, var)) for var in variables_np]
        sizes = np.array(sizes)

        # get max reuse bounded by tile
        tile_flop = np.prod(dim_lengths_np[:-1])
        tile_reuses = tile_flop//sizes

        # get number of repeated load/stores by applying max hardware reuse
        load_store_times = np.ceil(tile_reuses/min(self.ew_reuse_num,tile_flop))

        # get number of bytes to load/store
        load_store_bytes = sizes*load_store_times*self.byte_per_elem

        # get number of cycles to load/store
        load_store_cycles = load_store_bytes/self.load_store_bw_bytepc
        return load_store_cycles
    
    # get per tensor compute cycles for matmul
    def get_mm_load_store_cycles_from_padded_tile(self,
                                                  variables:List[List[List[int]]],
                                                  dim_lengths:List[int]) -> np.ndarray:
        bkmn = utils.dim_var_to_bkmn(dim_lengths, variables)
        return self.get_mm_load_store_cycles_from_padded_bkmn(bkmn)
    
    def get_mm_load_store_cycles_from_padded_bkmn(self,
                                                  bkmn:Tuple[int,int,int,int]) -> np.ndarray:
        b, k, m, n = bkmn

        # get hardware reuses of out in in
        arch_reuse_list_out_in_in = []
        for reuse_factor in self.mm_reuse_list:
            if reuse_factor == "k":
                arch_reuse_list_out_in_in.append(k)
            elif reuse_factor == "m":
                arch_reuse_list_out_in_in.append(m)
            elif reuse_factor == "n":
                arch_reuse_list_out_in_in.append(n)
            else:
                assert int(reuse_factor), "reuse factor should be positive int or k,m,n"
                arch_reuse_list_out_in_in.append(int(reuse_factor))
        arch_reuse_np_out_in_in = np.array(arch_reuse_list_out_in_in)

        # get max reuse bounded by tile
        tile_reuse_np_out_in_in = np.array([k, n, m])

        # get number of repeated load/stores by applying max hardware reuse
        tile_flop = np.prod(bkmn)
        load_store_times = np.ceil(tile_reuse_np_out_in_in/arch_reuse_np_out_in_in)

        # get number of bytes to load/store
        sizes = np.array([b*m*n, b*m*k, b*k*n])
        load_store_bytes = sizes*load_store_times*self.byte_per_elem

        # get number of cycles to load/store
        load_store_cycles = load_store_bytes/self.load_store_bw_bytepc
        return load_store_cycles

    def get_peak_flopc(self):
        # Return the peak flop/c for the systolic array and vector unit.
        return self.mm_flopc, self.ew_flopc

    # get compute cycles for elementwise
    def get_ew_compute_cycle_from_padded_tile(self, 
                                              dim_lengths:List[int]) -> float:
        assert 0 not in dim_lengths, "0 dimension is not allowed"
        return np.prod(dim_lengths)/self.ew_flopc
    
    # get compute cycles for matmul
    def get_mm_compute_cycle_from_padded_tile(self, 
                                              dim_lengths:List[int]) -> float:
        # assert 0 not in dim_lengths, "0 dimension is not allowed"
        # print(f"MM cycle (single op): {np.prod(dim_lengths)/self.mm_flopc + self.mm_init_cycle}, dim len = {dim_lengths}")
        return 2*np.prod(dim_lengths)/self.mm_flopc + self.mm_init_cycle

    # get total cycles for a set of fused ops
    def get_total_cycle_for_fused_op(self,
                                     ops:List[OP], temporal_for_ops) -> Tuple[float, float, float, float, float]:
        # get total cycle for compute
        assert(len(ops) == len(temporal_for_ops)), "each op should have a corresponding temporal config"
        # print("EW LIST:", [self.get_ew_compute_cycle_from_padded_tile(op.dim_lengths)
        #                            for temporal, op in zip(temporal_for_ops, ops) if op.is_ew])
        # print("MM LIST:", [self.get_mm_compute_cycle_from_padded_tile(op.dim_lengths)
        #                            for temporal, op in zip(temporal_for_ops, ops) if not op.is_ew])
        # print("EW LIST:", [self.get_ew_compute_cycle_from_padded_tile(op.dim_lengths) * get_num_comp_iter(temporal)
        #                            for temporal, op in zip(temporal_for_ops, ops) if op.is_ew])
        # print("MM LIST:", [self.get_mm_compute_cycle_from_padded_tile(op.dim_lengths) * get_num_comp_iter(temporal)
        #                            for temporal, op in zip(temporal_for_ops, ops) if not op.is_ew])
        ew_compute_cycle = np.sum([self.get_ew_compute_cycle_from_padded_tile(op.dim_lengths) * get_num_comp_iter(temporal)
                                   for temporal, op in zip(temporal_for_ops, ops) if op.is_ew])
        mm_compute_cycle = np.sum([self.get_mm_compute_cycle_from_padded_tile(op.dim_lengths) * get_num_comp_iter(temporal)
                                   for temporal, op in zip(temporal_for_ops, ops) if not op.is_ew])
        # print(f"total mm cycles (fused op): {mm_compute_cycle}")
        # print(f"total ew cycles (fused op): {ew_compute_cycle}")
        if self.ew_mm_overlap:
            compute_cycle = max(ew_compute_cycle, mm_compute_cycle)
        else:
            compute_cycle = ew_compute_cycle + mm_compute_cycle

        # get total cycle for load/store
        tensor_id_to_ldst_cycle_dict:Dict[int, List[Tuple[float, bool]]] = {}
        for op in ops:
            # get load/store cycles for each tensor
            if op.is_ew:
                load_store_cycles = self.get_ew_load_store_cycles_from_padded_tile(op.variables, op.dim_lengths)
            else:
                load_store_cycles = self.get_mm_load_store_cycles_from_padded_tile(op.variables, op.dim_lengths)
            
            # update tensor_id_to_ldst_cycle_dict
            for is_input, (tensor_id, cycle) in enumerate(zip(op.tensor_id_list, load_store_cycles)):
                if tensor_id not in tensor_id_to_ldst_cycle_dict:
                    tensor_id_to_ldst_cycle_dict[tensor_id] = []
                if is_input:
                    # load is negative
                    tensor_id_to_ldst_cycle_dict[tensor_id].append((-cycle, op.is_ew))
                else:
                    # store is positive
                    tensor_id_to_ldst_cycle_dict[tensor_id].append((cycle, op.is_ew))

        # analyze load/store cycles for each tensor
        total_load_cycle = 0
        total_store_cycle = 0
        for tensor_id, cycle_list in tensor_id_to_ldst_cycle_dict.items():
            # init with the first occurrence of the tensor
            cycle, is_ew = cycle_list[0]
            assert(not np.isnan(cycle)), "cycle should not be nan!"
            last_is_ew = is_ew
            last_cycle = cycle
            # first occurrence cannot be fused
            if cycle<0:
                total_load_cycle += -cycle
            else:
                total_store_cycle += cycle
            # continue to analyze the rest occurrences of the tensor
            for cycle, is_ew in cycle_list[1:]:
                # nothing to do if both ops are matmul
                if (not last_is_ew) and (not is_ew):
                    if cycle<0:
                        total_load_cycle += -cycle
                    else:
                        total_store_cycle += cycle
                # otherwise, fuse store with its following load
                else:
                    if (last_cycle<0) and (cycle<0):
                        total_load_cycle += -cycle
                    elif (last_cycle>0) and (cycle<0):
                        total_store_cycle -= min(last_cycle, -cycle)
                        total_load_cycle += abs(last_cycle+cycle)
                    else:
                        total_store_cycle += cycle
                # update last cycle and last is_ew
                last_cycle = cycle
                last_is_ew = is_ew
        return max(compute_cycle, total_load_cycle, total_store_cycle), mm_compute_cycle, ew_compute_cycle, total_load_cycle, total_store_cycle
                
    # def new_tensor_id(self)->int:
    #     self.tensor_id += 1
    #     return self.tensor_id
    