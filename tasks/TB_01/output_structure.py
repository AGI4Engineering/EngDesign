# response_structure.py
from pydantic import BaseModel, Field

FULL_SPEC = """
REQUIRED OUTPUT FORMAT — READ CAREFULLY
=======================================

The LLM must return a JSON object that matches the Response_structure model.
Inside `config.netlist` it must embed *plain-text* Spectre netlist that follows
EXACTLY the template and ordering below.

────────────────────  EXACT ORDER  ────────────────────
1. Header comments (KEEP VERBATIM)
   // Library name: MP4
   // Cell name: fc_ota
   // View name: schematic

2. First non-blank subcircuit line (NO leading dot “.”)
   subckt fc_ota VDD VSS ibn10u vin vip vout

3. Device section (27 lines, KEEP ORDER)
   • Replace every placeholder:
       W0…W17  → width  in µm (e.g. 3.0u)
       L0…L17  → length in µm (e.g. 0.18u)
       M0…M17  → integer multiplier (≥1)
       R0, R1  → resistor in Ω (e.g. 10k)
   • Do NOT alter node names, model names (tsmc18dP / tsmc18dN),
     or the keyword  region=sat.
   • Do NOT add, delete, or reorder lines.

4. Final subcircuit line (NO leading dot “.”)
   ends fc_ota

5. Footer comments + top-level instance (KEEP VERBATIM)
   // Top-level instantiation
   // Library name: MP4
   // Cell name: dut
   // View name: schematic
   I1 (net1 net2 net5 net3 net4 net6) fc_ota

6. Absolutely NO extra text:
   • Nothing before the header or after the I1 line.
   • No markdown, JSON, or code fences.
   • No trailing blank lines.

7. Technology lock:
   • All PMOS must keep model name tsmc18dP
   • All NMOS must keep model name tsmc18dN
   • You may modify only W, L, m, and resistor values.

VALIDATION POLICY
-----------------
If any placeholder remains unreplaced, a leading dot appears before “subckt”
or “ends”, required lines are missing, or extra text is present, the submission
receives automatic score = 0.
"""

class ConfigFile(BaseModel):
    # The full specification is passed as the field description
    netlist: str = Field(description=FULL_SPEC)

class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed resoning process to accomplish the task, please solve all the tasks step by step.")
    config: ConfigFile


