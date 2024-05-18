import time
from typing import Any, Callable
import logging

def TimeIt(func: Callable) -> Callable:
    def wrapper(*args, **kwargs) -> Any:
        t1 = time.time()
        val = func(*args, **kwargs)
        t2 = time.time()
        logging.info(f" {func.__name__}: time = {t2 - t1:.6f}")
        return val

    return wrapper
