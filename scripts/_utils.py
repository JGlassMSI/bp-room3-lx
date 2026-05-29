import contextlib

import sacn

@contextlib.contextmanager
def drive_device(device: sacn.sACNsender):
    device.start()
    try:
        yield
    finally:
        device.stop()
