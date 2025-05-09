# response_structure.py
from pydantic import BaseModel, Field

FULL_SPEC = """
REQUIRED OUTPUT FORMAT — READ CAREFULLY
=======================================

The LLM must return a JSON object that matches the Response_structure model.
Inside `config.netlist` it must embed *plain-text* Spectre netlist that follows
EXACTLY the template and ordering below.

1. Header comments (KEEP VERBATIM)
   // Library name: MP1
   // Cell name: cs_amp
   // View name: schematic

2. First non-blank subcircuit line (NO leading dot “.”)
   subckt cs_amp VDD VSS vin_a vin_b vout

3. Final subcircuit line (NO leading dot “.”)
   ends cs_amp

4. Footer comments + top-level instance (KEEP VERBATIM)
   // Library name: MP1
   // Cell name: dut
   // View name: schematic
   I0 (net1 net2 net3 net4 net5) cs_amp

5. Absolutely NO extra text:
   • Nothing before the header or after the I1 line.
   • No markdown, JSON, or code fences.
   • No trailing blank lines.

6. Technology lock:
   • All PMOS must keep model name tsmc18dP
   • All NMOS must keep model name tsmc18dN
   
7. Force use of ports:
   • Ensure that VDD VSS vin_a vin_b vout are explicitly used in the transistor gate connections in the subcircuit cs_amp, as they are the differential inputs. 
   • Do not replace or rename the port. 
   
8. Device section 
   • Replace and only replace every placeholder:
       W  → width  in µm (e.g. 3.0u)
       L  → length in µm (e.g. 0.18u)
       M  → integer multiplier (≥1)
       R  → resistance in Ohm (e.g. 1.0k)
   • Do NOT alter node names, model names (tsmc18dP / tsmc18dN),
     or the keyword  region=sat.
   • Do NOT add, delete, or reorder lines.
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


