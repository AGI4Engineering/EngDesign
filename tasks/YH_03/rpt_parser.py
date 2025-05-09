from typing import Dict, Any

def parse_rpt_file(rpt_file: str) -> Dict[str, Any]:
    with open(rpt_file, 'r') as f:
        lines = f.readlines()
    
    result = {
        'General_Information': {},
        'Performance_Metrics': {},
        'Synthesis_Summary': {}
    }
    
    # Find section boundaries
    sections = {
        'General_Information': None,
        'Performance_Metrics': None,
        'Synthesis_Summary': None
    }
    
    for i, line in enumerate(lines):
        if 'Synthesis Summary Report' in line:
            sections['Synthesis_Summary'] = i
        elif 'Performance & Resource Estimates' in line:
            sections['Performance_Metrics'] = i
    
    # Parse each section
    if sections['Synthesis_Summary']:
        # Find the end of the Synthesis Summary section
        next_section = None
        for i, line in enumerate(lines[sections['Synthesis_Summary']:], sections['Synthesis_Summary']):
            if 'Performance & Resource Estimates' in line:
                next_section = i
                break
        
        # Extract the synthesis summary information
        summary_lines = lines[sections['Synthesis_Summary']:next_section] if next_section else lines[sections['Synthesis_Summary']:]
        for line in summary_lines:
            line = line.strip()
            if line.startswith('*'):
                # Remove the asterisk and split by colon
                parts = line[1:].strip().split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    result['Synthesis_Summary'][key] = value
    
    if sections['Performance_Metrics']:
        next_section = None
        for i, line in enumerate(lines[sections['Performance_Metrics']:], sections['Performance_Metrics']):
            if '================================================================' in line:
                next_section = i
                break
        section_lines = lines[sections['Performance_Metrics']:next_section] if next_section else lines[sections['Performance_Metrics']:]
        result['Performance_Metrics'] = parse_performance_metrics(section_lines)
    
    return result 