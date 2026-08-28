from time import time_ns as ns

# Date/Time stuff
def ms_now() -> int:
    return ns() // 1000000
