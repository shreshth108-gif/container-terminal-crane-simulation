from collections import deque

class Queues:
    def __init__(self):
        self.AGV_unload_queue = deque()
        self.TRAILER_unload_queue = deque()
        self.AGV_load_queue = deque()
        self.TRAILER_load_queue = deque()

