import numpy as np
import math
import os
import sys
from typing import Tuple, Dict, Any

PTE_SIZE = 8

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Helper functions to evaluate the page table designed by LLM
def is_power_of_two(n: int):
    return n > 0 and (n & (n - 1)) == 0

def compute_page_table_memory(physical_memory_bytes: int,
                              page_size: int,
                              entries_per_level: list[int]) -> int:
    """
    Precisely calculates the total memory used by on‑demand allocated page tables:
    - PTE_SIZE: size of a page table entry in bytes (8)
    - page_size: physical page size in bytes
    - entries_per_level: number of entries per page table page at each level
    """
    # Calculate the number of physical pages that need mapping
    physical_pages = math.ceil(physical_memory_bytes / page_size)
    level_pages = physical_pages
    total_bytes = 0

    # Iterate from the lowest level up to the root level
    for entries in reversed(entries_per_level):
        # Bytes required for one page‑table page (entries × PTE_SIZE)
        bytes_per_pt_page = entries * PTE_SIZE
        # Physical pages needed to store that page‑table page
        pages_per_pt_page = math.ceil(bytes_per_pt_page / page_size)

        # Number of page‑table pages required at this level
        num_pt_pages = math.ceil(level_pages / entries)
        # Add this level’s memory usage
        total_bytes += num_pt_pages * pages_per_pt_page * page_size

        # For the next higher level, the “pages” to map are these page‑table pages
        level_pages = num_pt_pages

    return total_bytes

def compute_avg_translation_time(page_size: int, levels: int):
    """
    TLB hit rate model: h = exp(-0.1542*(page_size/1024 - 5.82)^2)
    Avg time = TLB_access (20ns) + (1 - h) * levels * PTE_access (100ns)
    """
    h = math.exp(-0.1542 * ((page_size / 1024) - 5.82) ** 2)
    return 20.0 + (1.0 - h) * levels * 100.0

def evaluate_llm_response(llm_response):
    try:
        details: Dict[str, Any] = {}
        score = 0

        a = llm_response.config.DeviceA
        b = llm_response.config.DeviceB

        # 1. Consistency of design (10 pts)
        if (a.page_size == b.page_size and a.levels == b.levels and a.entries_per_level == b.entries_per_level):
            score += 10
            details['For Device A and Device B the design is consistent'] = True
        else:
            details['For Device A and Device B the design is consistent'] = False

        # 2. Address‑bit.check (15 pts)
        bits_offset = round(math.log2(a.page_size))
        bits_indexes = sum(round(math.log2(e)) for e in a.entries_per_level)
        if bits_offset + bits_indexes == 40:
            score += 15
            details['Virtual addresses are 40 bits'] = True
        else:
            details['Virtual addresses are 40 bits'] = False

        # 3. Page size is power of two (5 pts)
        if is_power_of_two(a.page_size):
            score += 5
            details['Page size is power of two'] = True
        else:
            details['Page size is power of two'] = False

        # 4. Entries per level are powers of two (5 pts)
        if all(is_power_of_two(e) for e in a.entries_per_level):
            score += 5
            details['Entries per level are powers of two'] = True
        else:
            details['Entries per level are powers of two'] = False

        # 5. Number of entries matches levels (5 pts)
        if len(a.entries_per_level) == a.levels:
            score += 5
            details['Number of entries matches levels'] = True
        else:
            details['Number of entries matches levels'] = False

        # 6. Device A metrics (30 pts)
        # Check whether the calculated memory matches the LLM_calculated memory
        phyA = 150 * 1024 * 1024
        memA_calc = compute_page_table_memory(phyA, a.page_size, a.entries_per_level)
        if memA_calc == a.page_table_memory:
            score += 5
            details['LLM correctly calculate the page_table_memory of Deive A'] = True
        else:
            details['LLM correctly calculate the page_table_memory of Deive A'] = False

        # Check whether the calculated memory is within the limit
        if memA_calc <= 320 * 1024:
            score += 10
            details['The page_table_memory of the designed Device A meets the specified limit'] = True
        else:
            details['The page_table_memory of the designed Device A meets the specified limit'] = False

        # Check whether the calculated time matches the LLM_calculated time
        tA_calc = compute_avg_translation_time(a.page_size, a.levels)
        if abs(tA_calc - a.avg_translation_time) < 1e-6:
            score += 5
            details['LLM correctly calculate the avg_translation_time of Deive A'] = True
        else:
            details['LLM correctly calculate the avg_translation_time of Deive A'] = False

        # Check whether the calculated time is within the limit
        if tA_calc <= 150.0:
            score += 10
            details['The avg_translation_time of the designed Device A meets the specified limit'] = True
        else:
            details['The avg_translation_time of the designed Device A meets the specified limit'] = False

        # 7. Device B metrics (30 pts)
        # Check whether the calculated memory matches the LLM_calculated memory
        phyB = 2 * 1024 * 1024 * 1024
        memB_calc = compute_page_table_memory(phyB, b.page_size, b.entries_per_level)
        if memB_calc == b.page_table_memory:
            score += 5
            details['LLM correctly calculate the page_table_memory of Deive B'] = True
        else:
            details['LLM correctly calculate the page_table_memory of Deive B'] = False

        # Check whether the calculated memory is within the limit
        if memB_calc <= 4.05 * 1024 * 1024:
            score += 10
            details['The page_table_memory of the designed Device B meets the specified limit'] = True
        else:
            details['The page_table_memory of the designed Device B meets the specified limit'] = False

        # Check whether the calculated time matches the LLM_calculated time
        tB_calc = compute_avg_translation_time(b.page_size, b.levels)
        if abs(tB_calc - b.avg_translation_time) < 1e-6:
            score += 5
            details['LLM correctly calculate the avg_translation_time of Deive B'] = True
        else:
            details['LLM correctly calculate the avg_translation_time of Deive B'] = False

        # Check whether the calculated time is within the limit
        if tB_calc <= 150.0:
            score += 10
            details['The avg_translation_time of the designed Device B meets the specified limit'] = True
        else:
            details['The avg_translation_time of the designed Device B meets the specified limit'] = False

        passed = (score == 100)
        confidence = 100
        return passed, details, score, confidence
 
    except Exception as e:
        return False, {"error": str(e)}, 0, 0