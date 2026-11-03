class Car:
    AGV = 0
    TRAILER = 1

    def __init__(self, type, arrivalTime, serviceTime=None, cargo=1):
        self.type = type
        self.arrivalTime = arrivalTime
        self.systemArrivalTime = arrivalTime
        self.serviceTime = serviceTime
        self.cargo = cargo

    def __str__(self):
        car_type = "AGV" if self.type == Car.AGV else "Trailer"
        return f"{car_type} arrived at {self.arrivalTime}"