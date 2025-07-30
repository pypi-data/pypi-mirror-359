import re
from io import StringIO
from contextlib import closing
from trace_commentor import flags, Commentor

WS = re.compile(" +")

def asserteq_or_print(value, ground_truth):
    if flags.DEBUG or flags.PRINT:
        print(value)
    else:
        value = re.sub(WS, " ", value.strip("\n").rstrip(" ").rstrip("\n"))
        ground_truth = re.sub(WS, " ", ground_truth.strip("\n").rstrip(" ").rstrip("\n"))
        assert value == ground_truth, "\n".join(["\n\n<<<<<<<< VALUE", value, "========================", ground_truth, ">>>>>>>> GROUND\n"])
