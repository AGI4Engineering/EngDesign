# response_structure.py
from pydantic import BaseModel, Field

FULL_SPEC = """
REQUIRED OUTPUT FORMAT — READ CAREFULLY
=======================================

The LLM must return a JSON object that matches the Response_structure model.
Inside `config.netlist` it must embed *plain-text* Spectre netlist that follows
EXACTLY the template and ordering below.

1. Header comments (KEEP VERBATIM)
   // Library name: MP4
   // Cell name: fc_ota
   // View name: schematic

2. First non-blank subcircuit line (NO leading dot “.”)
   subckt fc_ota VDD VSS ibn10u vin vip vout

3. Final subcircuit line (NO leading dot “.”)
   ends fc_ota

4. Footer comments + top-level instance (KEEP VERBATIM)
   // Top-level instantiation
   // Library name: MP4
   // Cell name: dut
   // View name: schematic
   I1 (net1 net2 net5 net3 net4 net6) fc_ota

5. Absolutely NO extra text:
   • Nothing before the header or after the I1 line.
   • No markdown, JSON, or code fences.
   • No trailing blank lines.

6. Technology lock:
   • All PMOS must keep model name tsmc18dP
   • All NMOS must keep model name tsmc18dN

7. Force use of ports:
   • Ensure that vin, vip, vout, VSS, VDD and ibn10u are explicitly used in the transistor gate connections in the subcircuit fc_ota, as they are the differential inputs. 
   • Do not replace or rename them as net3, net4, or similar. These signals must remain named vin and vip in the subckt pin list and inside the body.

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


