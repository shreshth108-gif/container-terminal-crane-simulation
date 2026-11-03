import heapq

class Event:
    AGV_ARRIVAL = 0
    AVG_UNLOAD = 1
    AVG_LOAD = 2
    TRAILER_ARRIVAL = 3
    TRAILER_UNLOAD = 4
    TRAILER_LOAD = 5

    def __init__(self, event_type, event_time, car=None):
        self.event_type = event_type
        self.event_time = event_time
        self.car = car

    def __lt__(self, other):
        return self.event_time < other.event_time

    def __str__(self):
        event_type_str = {
            Event.AGV_ARRIVAL: "AGV Arrival",
            Event.AVG_UNLOAD: "AVG Unload",
            Event.AVG_LOAD: "AVG Load",
            Event.TRAILER_ARRIVAL: "Trailer Arrival",
            Event.TRAILER_UNLOAD: "Trailer Unload",
            Event.TRAILER_LOAD: "Trailer Load"
        }
        return f"{event_type_str[self.event_type]} at {self.event_time}"

