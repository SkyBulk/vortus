def wrap_response(addr, msg):
    return  {"addr": addr, "msg": msg}

def get_prompt_text(command_path):
    return "/" + '/'.join([c.capitalize() for c in command_path]) + " > "