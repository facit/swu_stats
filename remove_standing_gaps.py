#!/usr/bin/env python3
"""
Make the first-column IDs consecutive **starting with data row 9** (i.e. row 1
after the header is left alone, as are rows 2-8).  
Rows 1-8 keep whatever value they already have—even if those values are
missing, duplicated, or out of order.

Usage
-----
    python fix_sequence.py input.csv [output.csv]

If *output.csv* is omitted, the input file is overwritten in-place.
"""

from __future__ import annotations
import csv, sys
from pathlib import Path
from tempfile import NamedTemporaryFile

SKIP_ROWS = 8          # data-rows (after the header) that must NOT be touched
ENCODING  = "utf-8"    # change if your CSV uses another encoding

def fix_sequence(in_path: Path, out_path: Path | None = None,
                 skip: int = SKIP_ROWS) -> None:
    """
    Rewrite *in_path* so that, starting after the first *skip* data rows,
    the first column becomes 1, 2, 3 … with no gaps.
    """
    # Choose an output handle (temp file for in-place edits)
    if out_path is None:
        f_out_cm = NamedTemporaryFile("w", newline="", encoding=ENCODING,
                                      delete=False, dir=in_path.parent,
                                      suffix=".csv")
    else:
        f_out_cm = open(out_path, "w", newline="", encoding=ENCODING)

    with open(in_path, newline="", encoding=ENCODING) as f_in, f_out_cm as f_out:
        reader, writer = csv.reader(f_in), csv.writer(f_out)

        # Copy header unchanged
        header = next(reader, None)
        if header is not None:
            writer.writerow(header)

        expected = 1
        for idx, row in enumerate(reader, start=1):  # idx: data-row number
            if idx > skip:
                if row and row[0].isdigit() and int(row[0]) != expected:
                    row[0] = str(expected)
            # even when we skip modification we still progress the sequence
            expected += 1
            writer.writerow(row)

    # Atomically replace original if we were editing in-place
    if out_path is None:
        Path(f_out_cm.name).replace(in_path)

if __name__ == "__main__":
    match sys.argv[1:]:
        case [inp]:
            fix_sequence(Path(inp))
        case [inp, outp]:
            fix_sequence(Path(inp), Path(outp))
        case _:
            sys.exit("Usage: python fix_sequence.py input.csv [output.csv]")
