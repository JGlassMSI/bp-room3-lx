# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "sacn>=1.11.0",
# ]
# ///
import argparse
import json

import sacn

from _parse_range import parse_ranges_str, abbreviate_ranges
from _utils import drive_device


parser = argparse.ArgumentParser("Send sacn lighting data")

parser.add_argument(
    "--debug", action="store_true", help="Send a fixed blue value to all universes"
)
parser.add_argument(
    "--color",
    choices=["red", "green", "blue"],
    help="debug color (only valid with --debug)",
)
parser.add_argument(
    "-u",
    "--universes",
    type=str,
    help="a comma- or dash-separated list of universes to capture (e.g. 1,2,3-5)",
    default="1-160",
)
parser.add_argument(
    "-f",
    "--file",
    help="json data file to open",
    default=r"C:\Users\trex\Documents\Blue Paradox\dmx_data_u47-69_t20260529_084747.json",
)

# This is arbitrary UUID but needs to be the same forever
_cid = (
    0x3B,
    0xC6,
    0x7D,
    0x92,
    0x99,
    0x5F,
    0x19,
    0xDC,
    0x6,
    0x67,
    0x7E,
    0x5E,
    0xF4,
    0x95,
    0xD5,
    0x2C,
)
sender = sacn.sACNsender(source_name="BP-Room-4-NUC", cid=_cid)

DEBUG_LEVEL = 200
DEBUG_DATA = {
    "red": [DEBUG_LEVEL, 0, 0],
    "green": [0, DEBUG_LEVEL, 0],
    "blue": [0, 50, DEBUG_LEVEL],
}


if __name__ == "__main__":
    args = parser.parse_args()
    if args.color and not args.debug:
        raise argparse.ArgumentError("--color is only valid with --debug")
    if args.debug and not args.color:
        args.color = "blue"
    universes = parse_ranges_str(args.universes)
    if args.debug:
        data = {
            str(u): [*DEBUG_DATA[args.color] * (int(512 / 3) + 1)][:512]
            for u in universes
        }
    else:
        DATA_FILE = args.file

        with open(DATA_FILE, "r") as f:
            data = json.load(f)

    # make sure we have data for all universes we want to send
    not_found: list[int] = []
    for universe in universes:
        if not str(universe) in data:
            not_found.append(universe)
    if not_found:
        raise ValueError(
            f"Cannot find data for universes {abbreviate_ranges(not_found)}"
        )

    for universe in universes:
        sender.activate_output(universe)
        sender[universe].multicast = True  # set multicast to True
        sender[universe].dmx_data = data[str(universe)]
        sender[universe].priority = 190

    print(f"Sending dmx data on universes {args.universes}")
    print(f"Press ctrl+c to exit")
    with drive_device(sender):
        while True:
            pass
