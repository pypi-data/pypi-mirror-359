import inspect

def get_caller_context():
    stack = inspect.stack()
    frame = stack[2].frame
    func = stack[2].function
    self_obj = frame.f_locals.get("self")
    return f"{repr(self_obj)}.{func}()" if self_obj else f"<unknown>.{func}()"