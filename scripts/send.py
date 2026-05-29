import argparse
import json

import sacn

from _parse_range import parse_ranges_str, abbreviate_ranges
from _utils import drive_device


parser = argparse.ArgumentParser("Send sacn lighting data")

parser.add_argument("--debug", action="store_true")
parser.add_argument("-u", "--universes", type=str, help="a comma- or dash-separated list of universes to capture", default="47-69")
parser.add_argument("-f", "--file", help="json data file to open", default=r"C:\Users\trex\Documents\Blue Paradox\dmx_data_u47-69_t20260529_084747.json")

# This is arbitrary UUID but needs to be the same forever
_cid = (0x3b, 0xc6, 0x7d, 0x92, 0x99, 0x5f, 0x19, 0xdc, 0x6, 0x67, 0x7e, 0x5e, 0xf4, 0x95, 0xd5, 0x2c)
sender = sacn.sACNsender(source_name="BP-Room-4-NUC", cid=_cid)


if __name__ == "__main__":
    args = parser.parse_args()
    universes = parse_ranges_str(args.universes)
    if args.debug:
        data = {str(u): [20] * 512 for u in universes}
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
        raise ValueError(f"Cannot find data for universes {abbreviate_ranges(not_found)}")


    for universe in universes:
        sender.activate_output(universe)
        sender[universe].multicast = True  # set multicast to True
        sender[universe].dmx_data = data[str(universe)]
        sender[universe].priority = 200

    print(f"Sending dmx data on universes {args.universes}")
    print(f"Press ctrl+c to exit")
    with drive_device(sender):
        while True:
            pass
