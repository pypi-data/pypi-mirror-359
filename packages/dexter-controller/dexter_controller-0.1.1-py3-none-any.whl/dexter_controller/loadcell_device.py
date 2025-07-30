import threading
from typing import Optional

from harp.devices.loadcells import LoadCellEvents, LoadCells
from harp.protocol import OperationMode


class LoadCellDevice:
    def __init__(self, com_port, start_thread=True):
        if not com_port:
            raise ValueError("com_port cannot be empty")
        self.com_port = com_port
        self.device = LoadCells(com_port)
        self.device.set_mode(OperationMode.ACTIVE)
        # set to only receive events from the load cells
        self.device.write_enable_events(LoadCellEvents.LOAD_CELL_DATA)
        self._finger_callbacks = {
            0: [],
            1: [],
        }  # 0: first finger, 1: second finger
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        if start_thread:
            self._thread = threading.Thread(target=self._event_loop)
            self._thread.daemon = True
            self._thread.start()

    def register_callback(self, finger_index, callback):
        if finger_index not in (0, 1):
            raise IndexError("finger_index must be 0 or 1")
        self._finger_callbacks[finger_index].append(callback)

    def _event_loop(self):
        with self.device as dev:
            while not self._stop_event.is_set():
                for event in dev.get_events():
                    data = event.payload  # Should be a list of 8 values
                    # Each finger gets 4 values: [0:4] and [4:8]
                    for i in (0, 1):
                        finger_data = data[i * 4 : (i + 1) * 4]
                        for cb in self._finger_callbacks[i]:
                            cb(finger_data)

    def close(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()
