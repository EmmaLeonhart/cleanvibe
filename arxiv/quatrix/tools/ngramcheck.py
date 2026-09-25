"""Order-independent faithfulness check: report stretches of the original whose
8-token windows do not occur anywhere in the rebuild (and vice versa).
Float placement therefore does not matter. Usage: python tools/ngramcheck.py A.pdf B.pdf"""
import sys
from textdiff import words

N = 8


def missing(a, b):
    grams = {tuple(b[i:i + N]) for i in range(len(b) - N + 1)}
    bad = [tuple(a[i:i + N]) not in grams for i in range(len(a) - N + 1)]
    spans, i = [], 0
    while i < len(bad):
        if bad[i]:
            j = i
            while j < len(bad) and bad[j]:
                j += 1
            spans.append((i, j + N - 1))
            i = j
        else:
            i += 1
    return spans


wa, wb = words(sys.argv[1]), words(sys.argv[2])
for name, x, y in (("ONLY IN ORIGINAL", wa, wb), ("ONLY IN REBUILD", wb, wa)):
    sp = missing(x, y)
    print(f"== {name}: {len(sp)} spans")
    for i, j in sp:
        print("  ", " ".join(x[max(0, i - 3):i]), "[[", " ".join(x[i + 3:j - 3][:60]) if j - i > 6 else "", "]]")
