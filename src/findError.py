import linecache
import os

def foo(code):
    exec(code)

def frames_to_tb(frames, code):
    tb = []
    for frame in frames:
        filename = frame.tb_frame.f_code.co_filename
        if not filename.startswith("<"):
            filename = os.path.basename(filename)
        lineno = frame.tb_lineno
        function = frame.tb_frame.f_code.co_name
        line = linecache.getline(filename, lineno).strip()
        if line == "":
            try:
                line = code.split("\n")[lineno-1]
            except:
                pass
        tb.append((filename, lineno, function, line))
    return tuple(tb)


def format_list(frames):
    extracted_list = []
    for frame in frames:
        if isinstance(frame, tuple):
            filename, lineno, name, line = frame
        else:
            filename = frame['filename']
            lineno = frame['lineno']
            name = frame['name']
            line = frame['line']
        extracted_list.append('  File "{}", line {}, in {}\n    {}\n'.format(
            filename, lineno, name, line.strip()))
    return extracted_list

def calcException(e, code):
    tb = e.__traceback__    
    while tb is not None:
        if tb.tb_frame.f_code.co_name == '<module>' and tb.tb_frame.f_back is not None:
            print("hi")
            break
        tb = tb.tb_next

    if isinstance(e, SyntaxError):
        # TODO fix syntax errors that are embedded down the callstack, as this only works for ones in the calling block.
        tb_tuple = []
        # Handle syntax errors
        filename = "<string>"
        lineno = e.lineno
        function = "<module>"
        line = code.split("\n")[lineno-1]
        tb_tuple.append((filename, lineno, function, line))
        tb_tuple = tuple(tb_tuple)
    else:
        frames = []
        while tb is not None:
            frames.append(tb)
            tb = tb.tb_next
    
        tb_tuple = frames_to_tb(frames, code)

    bottomerror = f"{type(e).__name__}: {e}"
    
    texterror = "".join(format_list(tb_tuple))+bottomerror
    return tb_tuple[0][1], texterror, bottomerror
