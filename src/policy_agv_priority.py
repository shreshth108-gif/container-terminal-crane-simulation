from ExtendedModel.Car import Car
from ExtendedModel.FES import FES
from ExtendedModel.Event import Event
from ExtendedModel.SimResults import SimResults
from ExtendedModel.Queues import Queues
from ExtendedModel.Crane import Crane
from scipy import stats
import numpy as np
from tqdm import tqdm

class RealisticModelSim:

    def __init__(self, AGVArrivalDist, AGVServiceDist, TRLArrivalDist, TRLServiceDist,
                 containers_from_AGV=0, containers_from_trailer=0):
        self.AGVArrivalDist = AGVArrivalDist
        self.AGVServiceDist = AGVServiceDist
        self.TRLArrivalDist = TRLArrivalDist
        self.TRLServiceDist = TRLServiceDist
        self.containers_from_AGV = containers_from_AGV
        self.containers_from_trailer = containers_from_trailer

    def simulate(self, T):
        t = 0
        fes = FES()
        queues = Queues()
        crane = Crane()
        res_AGV_unload = SimResults()
        res_TRAILER_unload = SimResults()
        res_AGV_load = SimResults()
        res_TRAILER_load = SimResults()
        res = None  # SojournTime helper not included in the original files; this value was never used

        # Schedule the first AGV arrival event
        a = self.AGVArrivalDist.rvs()
        car1 = Car(type=Car.AGV, arrivalTime=a)
        Event1 = Event(Event.AGV_ARRIVAL, car1.arrivalTime, car1)
        fes.add(Event1)

        # Schedule the first trailer arrival event
        b = self.TRLArrivalDist.rvs()
        car2 = Car(type=Car.TRAILER, arrivalTime=b)
        Event2 = Event(Event.TRAILER_ARRIVAL, car2.arrivalTime, car2)
        fes.add(Event2)

        while t < T:
            event = fes.next()
            car = event.car
            t = event.event_time
            res_AGV_load.registerQueueLength(t, len(queues.AGV_load_queue))
            res_AGV_unload.registerQueueLength(t, len(queues.AGV_unload_queue))
            res_TRAILER_load.registerQueueLength(t, len(queues.TRAILER_load_queue))
            res_TRAILER_unload.registerQueueLength(t, len(queues.TRAILER_unload_queue))

            if event.event_type == Event.AGV_ARRIVAL:
                queues.AGV_unload_queue.append(car)
                if len(queues.AGV_unload_queue) >= 1 and crane.is_idle():  # there is an available server
                    crane.start_operation(Crane.AGV_UNLOADING)
                    res_AGV_unload.registerWaitingTime(t - car.arrivalTime)
                    b = self.AGVServiceDist.rvs()
                    dep = Event(Event.AVG_UNLOAD, t + b, car=car)
                    fes.add(dep)
                a = self.AGVArrivalDist.rvs()  # next arrival time
                next_car = Car(Car.AGV, t + a)
                arr = Event(Event.AGV_ARRIVAL, t + a, car=next_car)
                fes.add(arr)  # schedule next arrival

            elif event.event_type == Event.TRAILER_ARRIVAL:
                queues.TRAILER_unload_queue.append(car)
                if len(queues.TRAILER_unload_queue) >= 1 and crane.is_idle():  # there is an available server
                    crane.start_operation(Crane.TRAILER_UNLOADING)
                    res_TRAILER_unload.registerWaitingTime(t - car.arrivalTime)
                    b = self.TRLServiceDist.rvs()
                    dep = Event(Event.TRAILER_UNLOAD, t + b, car=car)
                    fes.add(dep)
                a = self.TRLArrivalDist.rvs()  # next arrival time
                next_car = Car(Car.TRAILER, t + a)
                arr = Event(Event.TRAILER_ARRIVAL, t + a, car=next_car)
                fes.add(arr)  # schedule next arrival

            elif event.event_type == Event.AVG_UNLOAD:
                queues.AGV_unload_queue.remove(car)
                self.containers_from_AGV += car.cargo
                crane.stop_operation()
                queues.AGV_load_queue.append(car)
                if self.containers_from_trailer > 0:
                    next_car = queues.AGV_load_queue[0]
                    res_AGV_load.registerWaitingTime(t - next_car.arrivalTime)
                    b = self.AGVServiceDist.rvs()
                    dep = Event(Event.AVG_LOAD, t + b, car=next_car)
                    fes.add(dep)
                    crane.start_operation(Crane.AGV_LOADING)
                elif len(queues.AGV_unload_queue) > 0:
                    next_car = queues.AGV_unload_queue[0]
                    res_AGV_unload.registerWaitingTime(t - next_car.arrivalTime)
                    b = self.AGVServiceDist.rvs()
                    dep = Event(Event.AVG_UNLOAD, t + b, car=next_car)
                    fes.add(dep)
                    crane.start_operation(Crane.AGV_UNLOADING)
                elif len(queues.TRAILER_unload_queue) > 0:  # Otherwise, continue unloading trailers
                    next_car = queues.TRAILER_unload_queue[0]
                    res_TRAILER_unload.registerWaitingTime(t - next_car.arrivalTime)
                    b = self.TRLServiceDist.rvs()
                    dep = Event(Event.TRAILER_UNLOAD, t + b, car=next_car)
                    fes.add(dep)
                    crane.start_operation(Crane.TRAILER_UNLOADING)


            elif event.event_type == Event.TRAILER_UNLOAD:
                queues.TRAILER_unload_queue.remove(car)
                self.containers_from_trailer += car.cargo
                crane.stop_operation()
                queues.TRAILER_load_queue.append(car)
                if self.containers_from_AGV > 0:
                    next_car = queues.TRAILER_load_queue[0]
                    res_TRAILER_load.registerWaitingTime(t - next_car.arrivalTime)
                    b = self.TRLServiceDist.rvs()
                    dep = Event(Event.TRAILER_LOAD, t + b, car=next_car)
                    fes.add(dep)
                    crane.start_operation(Crane.TRAILER_LOADING)
                elif len(queues.AGV_unload_queue) > 0:
                    next_car = queues.AGV_unload_queue[0]
                    res_AGV_unload.registerWaitingTime(t - next_car.arrivalTime)
                    b = self.AGVServiceDist.rvs()
                    dep = Event(Event.AVG_UNLOAD, t + b, car=next_car)
                    fes.add(dep)
                    crane.start_operation(Crane.AGV_UNLOADING)
                elif len(queues.TRAILER_unload_queue) > 0:  # Otherwise, continue unloading trailers
                    next_car = queues.TRAILER_unload_queue[0]
                    res_TRAILER_unload.registerWaitingTime(t - next_car.arrivalTime)
                    b = self.TRLServiceDist.rvs()
                    dep = Event(Event.TRAILER_UNLOAD, t + b, car=next_car)
                    fes.add(dep)
                    crane.start_operation(Crane.TRAILER_UNLOADING)


            elif event.event_type == Event.AVG_LOAD:
                queues.AGV_load_queue.remove(car)
                self.containers_from_trailer -= car.cargo
                crane.stop_operation()
                if len(queues.TRAILER_load_queue) > 0 and crane.is_idle() and self.containers_from_AGV > 0:
                    next_car = queues.TRAILER_load_queue[0]
                    res_TRAILER_load.registerWaitingTime(t - next_car.arrivalTime)
                    b = self.TRLServiceDist.rvs()
                    dep = Event(Event.TRAILER_LOAD, t + b, car=next_car)
                    fes.add(dep)
                    crane.start_operation(Crane.TRAILER_LOADING)
                if crane.is_idle():  # nothing left to load: start the next unload instead of idling until the next arrival
                    heads = [q[0] for q in (queues.AGV_unload_queue, queues.TRAILER_unload_queue) if len(q) > 0]
                    next_car = (queues.AGV_unload_queue[0] if len(queues.AGV_unload_queue) > 0 else (queues.TRAILER_unload_queue[0] if len(queues.TRAILER_unload_queue) > 0 else None))
                    if next_car is not None and next_car.type == Car.AGV:
                        res_AGV_unload.registerWaitingTime(t - next_car.arrivalTime)
                        fes.add(Event(Event.AVG_UNLOAD, t + self.AGVServiceDist.rvs(), car=next_car))
                        crane.start_operation(Crane.AGV_UNLOADING)
                    elif next_car is not None:
                        res_TRAILER_unload.registerWaitingTime(t - next_car.arrivalTime)
                        fes.add(Event(Event.TRAILER_UNLOAD, t + self.TRLServiceDist.rvs(), car=next_car))
                        crane.start_operation(Crane.TRAILER_UNLOADING)

            elif event.event_type == Event.TRAILER_LOAD:
                queues.TRAILER_load_queue.remove(car)
                self.containers_from_AGV -= car.cargo
                crane.stop_operation()
                if len(queues.AGV_load_queue) > 0 and crane.is_idle() and self.containers_from_trailer > 0:
                    next_car = queues.AGV_load_queue[0]
                    res_AGV_load.registerWaitingTime(t - next_car.arrivalTime)
                    b = self.AGVServiceDist.rvs()
                    dep = Event(Event.AVG_LOAD, t + b, car=next_car)
                    fes.add(dep)
                    crane.start_operation(Crane.AGV_LOADING)
                if crane.is_idle():  # nothing left to load: start the next unload instead of idling until the next arrival
                    heads = [q[0] for q in (queues.AGV_unload_queue, queues.TRAILER_unload_queue) if len(q) > 0]
                    next_car = (queues.AGV_unload_queue[0] if len(queues.AGV_unload_queue) > 0 else (queues.TRAILER_unload_queue[0] if len(queues.TRAILER_unload_queue) > 0 else None))
                    if next_car is not None and next_car.type == Car.AGV:
                        res_AGV_unload.registerWaitingTime(t - next_car.arrivalTime)
                        fes.add(Event(Event.AVG_UNLOAD, t + self.AGVServiceDist.rvs(), car=next_car))
                        crane.start_operation(Crane.AGV_UNLOADING)
                    elif next_car is not None:
                        res_TRAILER_unload.registerWaitingTime(t - next_car.arrivalTime)
                        fes.add(Event(Event.TRAILER_UNLOAD, t + self.TRLServiceDist.rvs(), car=next_car))
                        crane.start_operation(Crane.TRAILER_UNLOADING)

        return res_AGV_load, res_AGV_unload, res_TRAILER_load, res_TRAILER_unload, res


AGVArrivalDist = stats.expon(scale=2)
AGVServiceDist = stats.expon(scale=1/50)
TRLArrivalDist = stats.expon(scale=2)
TRLServiceDist = stats.expon(scale=1/10)


simulation = RealisticModelSim(AGVArrivalDist, AGVServiceDist, TRLArrivalDist, TRLServiceDist)
T = 100000  # Total simulation time
res_AGV_load, res_AGV_unload, res_TRAILER_load, res_TRAILER_unload, res = simulation.simulate(T)

# Print results
print("AGV Queue Lengths: ", res_AGV_load)
print("AGV Queue Lengths: ", res_AGV_unload)
print("Trailer Queue Lengths: ", res_TRAILER_load)
print("Trailer Queue Lengths: ", res_TRAILER_unload)

nr_runs = 100
res_AGV_loadQL = np.zeros(nr_runs)
res_AGV_unloadQL = np.zeros(nr_runs)
res_TRAILER_loadQL = np.zeros(nr_runs)
res_TRAILER_unloadQL = np.zeros(nr_runs)
for run in tqdm(range(nr_runs)):
    simulation = RealisticModelSim(AGVArrivalDist, AGVServiceDist, TRLArrivalDist, TRLServiceDist)

    res_AGV_load, res_AGV_unload, res_TRAILER_load, res_TRAILER_unload, _ = simulation.simulate(T)
    res_AGV_loadQL[run] = res_AGV_load.getMeanQueueLength()
    res_AGV_unloadQL[run] = res_AGV_unload.getMeanQueueLength()
    res_TRAILER_loadQL[run] = res_TRAILER_load.getMeanQueueLength()
    res_TRAILER_unloadQL[run] = res_TRAILER_unload.getMeanQueueLength()

print(np.mean(res_AGV_loadQL))
print(np.mean(res_AGV_unloadQL))
print(np.mean(res_TRAILER_loadQL))
print(np.mean(res_TRAILER_unloadQL))


