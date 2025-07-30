import time
import functools
from typing import Any, Callable, List, Dict, Optional

class Tracer:
    """
    A tracer that captures execution data and sends it to a configured recorder.
    It now supports injecting extra metadata at the time of a traced function call.
    """
    def __init__(self, recorder, run_id: str):
        """
        Args:
            recorder: A configured recorder instance (e.g., DynamoDBRecorder).
            run_id: The unique identifier for the execution run.
        """
        if not hasattr(recorder, 'record'):
            raise TypeError("Recorder must have a 'record' method.")
        self._recorder = recorder
        self._run_id = run_id

    def trace(self, step_name: str) -> Callable:
        """
        A decorator to trace a function's execution.
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                """
                The wrapper that executes the function and records the trace.

                It inspects the kwargs for a special '_extra_metadata' key,
                separates it, and merges it into the final trace record.
                """
                
                # --- FIX: Pop the special metadata argument from kwargs ---
                # The .pop() method safely removes the key and returns its value.
                # If the key doesn't exist, it returns the default value (None).
                # This ensures `_extra_metadata` is NOT passed to the original function,
                # preventing "unexpected keyword argument" errors.
                extra_metadata = kwargs.pop('_extra_metadata', None)
                
                start_time = time.time()
                try:
                    # Now, call the original function with only its intended arguments.
                    output = func(*args, **kwargs)
                    status = "success"
                    return output
                except Exception as e:
                    status = "error"
                    output = {"error": type(e).__name__, "message": str(e)}
                    raise
                finally:
                    end_time = time.time()
                    
                    # Start with the base trace data.
                    # We capture the original, unaltered kwargs here for the log.
                    original_kwargs = kwargs.copy()
                    if extra_metadata:
                        original_kwargs['_extra_metadata'] = extra_metadata
                        
                    trace_data = {
                        "run_id": self._run_id,
                        "name": step_name,
                        "start_time": start_time,
                        "end_time": end_time,
                        "status": status,
                        "inputs": {"args": args, "kwargs": original_kwargs},
                        "outputs": output
                    }
                    
                    # Merge the extracted metadata into the final record.
                    if extra_metadata and isinstance(extra_metadata, dict):
                        trace_data.update(extra_metadata)
                    
                    # The recorder receives the final, merged trace data object.
                    self._recorder.record(trace_data)
            return wrapper
        return decorator