import argparse
import json
import time
import datetime

import sacn

from _parse_range import parse_range_list, simplify_ranges

parser = argparse.ArgumentParser("Capture sacn at a point in time")

parser.add_argument("-u", "--universes", type=str, help="a comma-separated list of universes to capture")

if __name__ == "__main__":
    args = parser.parse_args()

    #universes = [int(arg.strip()) for arg in args.universes.split(",")]
    universes = parse_range_list(args.universes)
    data: dict[int, tuple[int]] = {}

    receiver = sacn.sACNreceiver()
    receiver.start()  # start the receiving thread

    for u in universes:
        def closure(univ = u):
            @receiver.listen_on('universe', universe=univ)
            def callback(packet: sacn.DataPacket): 
                if packet.dmxStartCode == 0x00:  # ignore non-DMX-data packets
                    if univ not in data:
                        data[univ] = packet.dmxData
            receiver.join_multicast(univ)
        closure()

    print(f"Looking for data from universes {simplify_ranges([int(d) for d in sorted(universes)])}")
    start = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    time.sleep(2)  # receive for 10 seconds

    # optional: if multicast was previously joined
    for u in universes:
        receiver.leave_multicast(u)

    
    if data:
        print(f"Heard data in universes {simplify_ranges([int(d) for d in sorted(data.keys())])}")
        with open(f"dmx_data_{start}.json", "w") as f:
            json.dump(data, f)
    else:
        print(f"No data heard in universes {args.universes}")
    
    receiver.stop()