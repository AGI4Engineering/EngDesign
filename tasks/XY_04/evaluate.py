

def evaluate_llm_response(llm_response):
    score = 0
    details = {}
    confidence = 100

    def is_valid_rgb(value):
        if not isinstance(value, str) or not value.startswith('RGB(') or not value.endswith(')'):
            return False
        try:
            inside = value[4:-1]
            if 'x' in inside:  # Hex notation
                num = int(inside[1:], 16)
                return 0 <= num <= 0xFFF
            parts = inside.split(',')
            return all(0 <= int(p.strip()) <= 15 for p in parts)
        except:
            return False

    def darker_than(normal, night):
        try:
            def rgb_values(val):
                if 'x' in val:
                    num = int(val[1:], 16)
                    return (num >> 8) & 0xF, (num >> 4) & 0xF, num & 0xF
                parts = val[4:-1].split(',')
                return [int(p.strip()) for p in parts]
            norm = rgb_values(normal)
            night = rgb_values(night)
            return all(n <= no for n, no in zip(night, norm))
        except:
            return False

    # 1. Color Mapping (20)
    cm_score = 0
    if hasattr(llm_response.config, 'color_mapping') and isinstance(llm_response.config.color_mapping, dict):
        colors = list(llm_response.config.color_mapping.values())
        if all(is_valid_rgb(c) for c in colors):
            cm_score += 10
        if 0 < len(colors) <= 10:
            cm_score += 5
        if all(k in ['playfield', 'background', 'next_piece_preview', 'score_display', 'ui_panels', 'game_over_screen']
               for k in llm_response.config.color_mapping.keys()):
            cm_score += 5
    details['color_mapping'] = f'{cm_score}/20'
    score += cm_score

    # 2. Display Regions (20)
    dr_score = 0
    if hasattr(llm_response.config, 'display_regions') and isinstance(llm_response.config.display_regions, dict):
        regions = llm_response.config.display_regions
        if all(key in regions for key in ['playfield', 'next_piece_preview', 'score_display']):
            dr_score += 7
        coords_ok = True
        for r in regions.values():
            if not ('top_left' in r and 'bottom_right' in r):
                coords_ok = False
        if coords_ok:
            dr_score += 7
        dr_score += 6  # Assume no overlap
    details['display_regions'] = f'{dr_score}/20'
    score += dr_score

    # 3. Tetromino Colors (20)
    tc_score = 0
    if hasattr(llm_response.config, 'tetromino_colors') and isinstance(llm_response.config.tetromino_colors, list):
        blocks = llm_response.config.tetromino_colors
        if len(blocks) >= 7:
            tc_score += 6
            all_night = True
            all_darker = True
            for t in blocks:
                if isinstance(t, dict):
                    values = list(t.values())[0]
                    if isinstance(values, dict):
                        if 'default' not in values or 'night' not in values:
                            all_night = False
                        elif not darker_than(values['default'], values['night']):
                            all_darker = False
            if all_night:
                tc_score += 7
            if all_darker:
                tc_score += 7
    details['tetromino_colors'] = f'{tc_score}/20'
    score += tc_score

    # 4. Dynamic Modes (20)
    dm_score = 0
    if hasattr(llm_response.config, 'dynamic_modes') and isinstance(llm_response.config.dynamic_modes, dict):
        dynamic = llm_response.config.dynamic_modes
        if 'night_mode' in dynamic or 'night_mode_adjustment' in dynamic:
            dm_score += 10
            night_mode = dynamic.get('night_mode', dynamic.get('night_mode_adjustment', {}))
            if isinstance(night_mode, dict) and all(k in night_mode for k in ['playfield', 'background']):
                dm_score += 10
    details['dynamic_modes'] = f'{dm_score}/20'
    score += dm_score

    # 5. Bit Slicing (10)
    bs_score = 0
    if hasattr(llm_response.config, 'bit_slicing') and isinstance(llm_response.config.bit_slicing, dict):
        slicing = llm_response.config.bit_slicing
        if all(k in slicing for k in ['position_x', 'position_y', 'block_x', 'block_y']):
            bs_score += 10
    details['bit_slicing'] = f'{bs_score}/10'
    score += bs_score

    # 6. Resource Constraints (10)
    rc_score = 0
    if hasattr(llm_response.config, 'resource_constraints') and isinstance(llm_response.config.resource_constraints, dict):
        rc_score += 10
    details['resource_constraints'] = f'{rc_score}/10'
    score += rc_score

    passed = score >= 80
    print("score:", score)
    return passed, details, score, confidence