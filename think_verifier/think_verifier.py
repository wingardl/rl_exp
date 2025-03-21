# Reward function
def think_verifier(completions, **kwargs):
    def check_think_tags(completion):
        has_opening = '<think>' in completion
        has_closing = '</think>' in completion
        
        if has_opening and has_closing:
            # Check tag order
            opening_pos = completion.find('<think>')
            closing_pos = completion.find('</think>')
            if opening_pos < closing_pos:
                return 1.0
            else:
                return 0
        elif has_opening or has_closing:
            return 0.5
        else:
            return 0.0
    
    return [check_think_tags(completion) for completion in completions]