import threading
import time
from collections import defaultdict

from dexter_controller import Finger, FingerData, LoadCellDevice


class DexterHandController:
    def __init__(self, mapping):
        if not mapping:
            raise ValueError("mapping cannot be empty")
        self._finger_to_device = {}
        self.finger_data = defaultdict(lambda: FingerData([0, 0, 0, 0]))
        self._devices = []
        self._callbacks = defaultdict(list)  # {Finger: [callback, ...]}
        self._stop_event = threading.Event()

        for com_port, fingers in mapping.items():
            device = LoadCellDevice(com_port, start_thread=False)
            self._devices.append(device)
            for i, finger in enumerate(fingers):
                self._finger_to_device[finger] = (device, i)

        self._poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._poll_thread.start()

    def _poll_loop(self):
        while not self._stop_event.is_set():
            for device in self._devices:
                for event in device.device.get_events():
                    data = event.payload  # 8 values: 4 per finger
                    for i in (0, 1):
                        finger_data = data[i * 4 : (i + 1) * 4]
                        # Find which finger this is
                        for finger, (dev, idx) in self._finger_to_device.items():
                            if dev is device and idx == i:
                                self.finger_data[finger].raw_data = finger_data
                                for cb in self._callbacks[finger]:
                                    cb(finger_data)
            time.sleep(0.001)

    def register_finger_callback(self, finger, callback):
        """Register a callback for a finger. Callback will be called with new data."""
        self._callbacks[finger].append(callback)

    def close(self):
        self._stop_event.set()
        self._poll_thread.join()
        # Close all devices
        for device in self._devices:
            device.close()
        self._callbacks.clear()

    @property
    def thumb(self):
        return self.finger_data[Finger.THUMB]

    @property
    def index(self):
        return self.finger_data[Finger.INDEX]

    @property
    def middle(self):
        return self.finger_data[Finger.MIDDLE]

    @property
    def ring(self):
        return self.finger_data[Finger.RING]

    @property
    def pinky(self):
        return self.finger_data[Finger.PINKY]
