class Crane:
    IDLE = 0
    AGV_UNLOADING = 1
    AGV_LOADING = 2
    TRAILER_UNLOADING = 3
    TRAILER_LOADING = 4

    def __init__(self):
        self.status = Crane.IDLE

    def start_operation(self, operation_type):
        self.status = operation_type

    def stop_operation(self):
        self.status = Crane.IDLE

    def is_idle(self):
        return self.status == Crane.IDLE

    def __str__(self):
        status_dict = {
            Crane.IDLE: "Crane is idle",
            Crane.AGV_UNLOADING: "Crane is unloading AGV",
            Crane.AGV_LOADING: "Crane is loading AGV",
            Crane.TRAILER_UNLOADING: "Crane is unloading trailer",
            Crane.TRAILER_LOADING: "Crane is loading trailer"
        }
        return status_dict[self.status]