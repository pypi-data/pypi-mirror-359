from datetime import datetime
import tracemalloc
from contextlib import contextmanager
import pandas as pd


@contextmanager
def ExplainBlock(msg, width=50, char="*"):
    """Wraps code in a title block"""
    msg = f" {msg} "
    leftover_chars = width - len(msg)
    left_chars = leftover_chars // 2
    if max(left_chars, 0):
        right_chars = leftover_chars - left_chars
    else:
        right_chars = 0
    title_msg = f"{left_chars*char}{msg}{right_chars*char}"
    print(title_msg)
    yield
    print(char * len(title_msg))


@contextmanager
def MemoryRecorder():
    """
    Prints out peak and current memory usage
    """
    start = datetime.now()
    tracemalloc.start()
    yield
    current_size, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    end = datetime.now()
    div_factor = 1024**2  # Convert to MiB
    current_size /= div_factor
    peak /= div_factor
    print(f"Peak={peak:.2f}MiB, Current={current_size:.2f}MiB, took {end-start}")


if __name__ == "__main__":
    my_list = []

    with MemoryRecorder() as recorder:
        df = pd.DataFrame({"col1": ["A", "B", "A", "C", "B", "C"] * 1000})
        for _ in range(5):
            my_list.append(df.copy())
