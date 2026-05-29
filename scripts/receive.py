import time

import lx

# provide an IP-Address to bind to if you want to receive multicast packets from a specific interface
receiver = lx.sACNreceiver()
receiver.start()  # start the receiving thread

# define a callback function
@receiver.listen_on('universe', universe=8)  # listens on universe 1
def callback(packet):  # packet type: sacn.DataPacket
    if packet.dmxStartCode == 0x00:  # ignore non-DMX-data packets
        print(packet.dmxData)  # print the received DMX data

# optional: if multicast is desired, join with the universe number as parameter
receiver.join_multicast(8)
print("sleeping")

time.sleep(10)  # receive for 10 seconds

# optional: if multicast was previously joined
receiver.leave_multicast(8)

receiver.stop()