import argparse
import json
import time
import datetime
from pathlib import Path

import sacn

from _parse_range import parse_ranges_str, abbreviate_ranges
from _utils import drive_device

parser = argparse.ArgumentParser("Capture sacn at a point in time")

parser.add_argument("-u", "--universes", required=True, type=str, help="a comma-separated list of universes to capture")
parser.add_argument("-t", "--time", type=int, help="How long to record data for")

if __name__ == "__main__":
    args = parser.parse_args()

    universes = parse_ranges_str(args.universes)
    printable_ranges = abbreviate_ranges([int(d) for d in sorted(universes)])
    data: dict[int, tuple[int]] = {}

    receiver = sacn.sACNreceiver()

    for u in universes:
        def closure(univ = u):
            def callback(packet: sacn.DataPacket): 
                if packet.dmxStartCode == 0x00:  # ignore non-DMX-data packets
                    if univ not in data:
                        data[univ] = packet.dmxData
            receiver.register_listener('universe', callback, universe=univ)
            receiver.join_multicast(univ)
        closure()

    print(f"Looking for data from universes {printable_ranges}")
    print(f"Gathering data for {args.time} seconds")
    start = datetime.datetime.now()
    with drive_device(receiver):
        while datetime.datetime.now() - start < datetime.timedelta(seconds=args.time):
            for seen in data.keys():
                if receiver._callbacks[seen]:
                    print(f"Removing callback from universe {seen}")
                    receiver._callbacks[seen] = []
                    receiver.leave_multicast(seen)
            time.sleep(.1)


    # optional: if multicast was previously joined
    for u in universes:
        receiver.leave_multicast(u)

    
    if data:
        heard_universe_string = abbreviate_ranges([int(d) for d in sorted(data.keys())])
        print(f"-\nHeard data in universes {heard_universe_string}")

        filename = f"dmx_data_u{heard_universe_string.replace(",","u")}_t{start.strftime("%Y%m%d_%H%M%S")}.json"
        print(f"Saving to {Path(filename)}")
        with open(str(Path(filename)), "w") as f:
            json.dump(data, f)
    else:
        print(f"-\nNo data heard in any universes ({printable_ranges})")
    
    receiver.stop()