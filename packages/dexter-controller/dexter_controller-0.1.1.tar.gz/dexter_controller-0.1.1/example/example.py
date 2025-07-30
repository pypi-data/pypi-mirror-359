import time
from dexter_controller import Finger, DexterHandController

mapping = {
    "COM20": [Finger.THUMB, Finger.INDEX],
    "COM5": [Finger.MIDDLE, Finger.RING],
    "COM8": [Finger.PINKY],
}
controller = DexterHandController(mapping)

event_counts = {
    Finger.THUMB: 0,
    Finger.INDEX: 0,
    Finger.MIDDLE: 0,
    Finger.RING: 0,
    Finger.PINKY: 0,
}


def make_counter(finger):
    def on_next(data):
        event_counts[finger] += 1

    return on_next


# Register direct callbacks for event counting
controller.register_finger_callback(Finger.THUMB, make_counter(Finger.THUMB))
controller.register_finger_callback(Finger.INDEX, make_counter(Finger.INDEX))
controller.register_finger_callback(Finger.MIDDLE, make_counter(Finger.MIDDLE))
controller.register_finger_callback(Finger.RING, make_counter(Finger.RING))
controller.register_finger_callback(Finger.PINKY, make_counter(Finger.PINKY))

start = time.time()
try:
    print("Press Ctrl+C to exit.")
    while True:
        time.sleep(1)
        elapsed = time.time() - start
        thumb_rate = event_counts[Finger.THUMB] / elapsed
        index_rate = event_counts[Finger.INDEX] / elapsed
        middle_rate = event_counts[Finger.MIDDLE] / elapsed
        ring_rate = event_counts[Finger.RING] / elapsed
        pinky_rate = event_counts[Finger.PINKY] / elapsed

        thumb_val = controller.thumb.raw_data
        index_val = controller.index.raw_data
        middle_val = controller.middle.raw_data
        ring_val = controller.ring.raw_data
        pinky_val = controller.pinky.raw_data
        print(
            f"Thumb: {thumb_val} ({thumb_rate:.1f} Hz) | "
            f"Index: {index_val} ({index_rate:.1f} Hz) | "
            f"Middle: {middle_val} ({middle_rate:.1f} Hz) | "
            f"Ring: {ring_val} ({ring_rate:.1f} Hz) | "
            f"Pinky: {pinky_val} ({pinky_rate:.1f} Hz) ",
            end="\r",
            flush=True,
        )
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    controller.close()

# import time
# from dexter_controller import Finger, DexterHandController

# mapping = {"COM8": [Finger.THUMB, Finger.INDEX]}
# controller = DexterHandController(mapping)

# event_counts = {Finger.THUMB: 0, Finger.INDEX: 0}


# def make_counter(finger):
#     def on_next(data):
#         event_counts[finger] += 1

#     return on_next


# controller.thumb_observable.subscribe(make_counter(Finger.THUMB))
# controller.index_observable.subscribe(make_counter(Finger.INDEX))

# start = time.time()
# try:
#     while True:
#         time.sleep(1)
#         elapsed = time.time() - start
#         print(
#             f"Thumb: {event_counts[Finger.THUMB] / elapsed:.1f} Hz | "
#             f"Index: {event_counts[Finger.INDEX] / elapsed:.1f} Hz"
#         )
# except KeyboardInterrupt:
#     controller.close()
