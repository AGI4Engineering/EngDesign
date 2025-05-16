import instructor
from pydantic import BaseModel, Field
from typing import List
from openai import OpenAI

class ConfigFile(BaseModel):
    # Task 1
    SNRatRm: float = Field(description="The available SNR calculated in Task 1")
    tor1: float = Field(description="The absolute error in Task 1")
    # Task 2
    D0: float = Field(description="The required SNR for a single pulse received from a steady target (Task 2)")
    tor2: float = Field(description="The absolute error in Task 2")
    # Task 3
    D1: float = Field(description="The required SNR for a single pulse received from a fluctuating target (Task 3)")
    tor3: float = Field(description="The absolute error in Task 3")
    # Task 4
    DN: float = Field(description="The required SNR for 10 noncoherently integrated pulses received from a fluctuating target (Task 4)")
    tor4: float = Field(description="The absolute error in Task 4")
    # Task 5
    Gi: float = Field(description="The integration gain calculated in Task 5")
    tor5: float = Field(description="The absolute error in Task 5")
    # Task 6
    Lf: float = Field(description="The fluctuation loss calculated in Task 6")
    tor6: float = Field(description="The absolute error in Task 6")
    # Task 7
    actual_Rm: float = Field(description="The actual maximum range of the system calculated in Task 7")
    tor7: float = Field(description="The absolute error in Task 7")

    # Task 8
    Rmin: float = Field(description="The closest range from which a full pulse can be received calculated in Task 8")
    tor8: float = Field(description="The absolute error in Task 8")
    # Task 9
    Rua: float = Field(description="The unambiguous range of the system calculated in Task 9")
    tor9: float = Field(description="The absolute error in Task 9")

    # Task 10
    scan_sector_loss : float = Field(description="The scan sector loss calculated in Task 10")
    tor10: float = Field(description="The absolute error in Task 10")

    # Task 11
    Lmti_a : float = Field(description="The MTI noise correlation loss calculated in Task 11")
    tor11_a: float = Field(description="The absolute error of the MTI noise correlation loss in Task 11")
    Lmti_b : float = Field(description="The MTI velocity response loss calculated in Task 11")
    tor11_b: float = Field(description="The absolute error of the MTI velocity response loss in Task 11")
    # Task 12
    binary_integration_loss: float = Field(description="The binary integration loss calculated in Task 12")
    tor12: float = Field(description="The absolute error in Task 12")
    # Task 13
    cfar_loss: float = Field(description="The CFAR loss calculated in Task 13")
    tor13: float = Field(description="The absolute error in Task 13")

    # Task 14
    effective_df: float = Field(description="The effective detectability factor gained from Task 14")
    tor14: float = Field(description="The absolute error in Task 14")
    # Task 15
    evaluate_system_feasibility: int = Field(description="1 if the system meets the requirement; otherwise 0")

# Define your desired output structure
class Response_structure(BaseModel):
   reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
   config: ConfigFile

