# response_structure.py
from pydantic import BaseModel, Field

FULL_SPEC = """
REQUIRED OUTPUT FORMAT — READ CAREFULLY
=======================================

The LLM must return a JSON object that matches the Response_structure model.
Inside `config.netlist` it must embed *plain-text* Spectre netlist that follows
EXACTLY the template and ordering below.

1. Header comments (KEEP VERBATIM)
   // Library name: MP3
   // Cell name: ota
   // View name: schematic

2. First non-blank subcircuit line (NO leading dot “.”)
   subckt ota VDD VSS ibp10u vin vip vout

3. Final subcircuit line (NO leading dot “.”)
   ends ota

4. Footer comments + top-level instance (KEEP VERBATIM)
   // Library name: MP3
   // Cell name: dut
   // View name: schematic
   I16 (net1 net2 net6 net4 net3 net5) ota

5. Absolutely NO extra text:
   • Nothing before the header or after the I1 line.
   • No markdown, JSON, or code fences.
   • No trailing blank lines.

6. Technology lock:
   • All PMOS must keep model name tsmc18dP
   • All NMOS must keep model name tsmc18dN
   • You may modify only W, L, and m values.
   
7. Force use of ports:
   • Ensure that vin, vip, vout, VSS, VDD and ibp10u are explicitly used in the transistor gate connections in the subcircuit ota, as they are the differential inputs. 
   • Do not replace or rename the port. These signals must remain named vin and vip in the subckt pin list and inside the body.

8. Device section 
   • Replace every placeholder:
       W  → width  in µm (e.g. 3.0u)
       L  → length in µm (e.g. 0.18u)
       M  → integer multiplier (≥1)
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


