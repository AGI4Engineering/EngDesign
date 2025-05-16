from pydantic import BaseModel, Field
from typing import Dict, List

class Introduction(BaseModel):
    """Overall context and significance of the design problem"""
    background: str = Field(..., min_length=200, description="Historical context and motivation for the task")
    objectives: List[str] = Field(..., min_items=1, description="List of primary design objectives")
    significance: str = Field(..., description="Real-world impact of successful design")

class TaskAnalysis(BaseModel):
    """Detailed breakdown of problem requirements"""
    task_description: str = Field(..., min_length=200, description="Detailed description of the task")
    key_requirements: Dict[str, str] = Field(
        ...,
        description="Mapping of requirement IDs to descriptions",
        example={"REQ1": "Max operating temperature: 150°C"}
    )

class Methodology(BaseModel):
    """Design approach and tools"""
    framework: str = Field(..., description="Overall design philosophy/method")
    design_process: str = Field(..., min_length=200, description="Detailed description of the design process, including all the calculations and derivations and the reasoning process")

class Results(BaseModel):
    """Quantitative design outcomes"""
    parameters: str = Field(
        ...,
        description="Key design parameters with values",
        example={"Transfer function of the controller to achieve the desired performance": "G(s) = 10/(s+1)"}
    )

class Discussion_Conclusion(BaseModel):
    """Critical analysis of design outcomes"""
    discussion: str = Field(
        ...,
        description="Design compromises and their justification",
        example={"Cost vs Performance": "Selected aluminum over titanium..."}
    )
    conclusion: str = Field(
        ...,
        min_length=100,
        description="Key conclusions from the design process"
    )


class EngineeringReport(BaseModel):
    """Comprehensive design documentation structure"""
    introduction: Introduction
    task_analysis: TaskAnalysis
    methodology: Methodology
    results: Results
    discussion_conclusion: Discussion_Conclusion
