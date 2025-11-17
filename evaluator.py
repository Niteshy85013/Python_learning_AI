"""
Code evaluator using RestrictedPython.

Notes:
- RestrictedPython helps reduce risk but is NOT perfectly secure.
- For production: run user code in isolated containers (Docker) with CPU/memory/time limits.
"""

import sys
import io
import time
from RestrictedPython import compile_restricted
from RestrictedPython import safe_globals, utility_builtins
from RestrictedPython.Guards import guarded_iter_unpack_sequence, guarded_unpack_sequence
from config import Config

def run_restricted_code(code, stdin_text=''):
    """
    Execute user code in a RestrictedPython environment and capture printed output.
    Returns: dict { 'success': bool, 'output': str, 'error': str }
    """
    # Prepare a print collector
    output_buffer = io.StringIO()
    def _print_(*args, **kwargs):
        print(*args, **kwargs, file=output_buffer)

    # Build restricted builtins / globals
    restricted_globals = dict(safe_globals)
    # Provide a minimal set of builtins
    restricted_globals['_print_'] = _print_
    restricted_globals['_getiter_'] = iter
    restricted_globals['_iter_unpack_sequence_'] = guarded_iter_unpack_sequence
    restricted_globals['_unpack_sequence_'] = guarded_unpack_sequence
    # utility builtins (len, range, etc.)
    for k, v in utility_builtins.items():
        restricted_globals[k] = v

    # Additional safe helpers (no OS, sys, open, etc.)
    # Do not provide __import__ or open
    # Provide a simple input() that reads from stdin_text lines
    input_lines = stdin_text.splitlines()
    input_index = {'i': 0}
    def _input_(prompt=''):
        if input_index['i'] < len(input_lines):
            val = input_lines[input_index['i']]
            input_index['i'] += 1
            return val
        return ''

    restricted_globals['input'] = _input_

    # Compile the code
    try:
        byte_code = compile_restricted(code, '<string>', 'exec')
    except Exception as e:
        return {'success': False, 'output': '', 'error': f'CompileError: {e}'}

    # Execute with time limit
    start = time.time()
    try:
        exec(byte_code, restricted_globals, None)
        elapsed = time.time() - start
        if elapsed > Config.CODE_EXECUTION_TIME:
            return {'success': False, 'output': output_buffer.getvalue(), 'error': 'Timeout: code took too long.'}
        return {'success': True, 'output': output_buffer.getvalue(), 'error': ''}
    except SystemExit:
        return {'success': False, 'output': output_buffer.getvalue(), 'error': 'SystemExit called — disallowed.'}
    except Exception as e:
        # Return traceback-like message but keep it short
        return {'success': False, 'output': output_buffer.getvalue(), 'error': f'RuntimeError: {e}'}
