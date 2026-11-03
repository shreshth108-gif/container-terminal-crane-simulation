import numpy as np
import matplotlib.pyplot as plt

def simulation(pA, pT, q, simulation_time, max_capacity):
    xA, xT = 0, 0  # Initial state

    states = [(xA, xT)]

    for t in range(simulation_time):
        if (xA, xT) == (0, 0):
            transitions = [(1, 0), (0, 1)]
            probs = [pA, pT]
        elif (xA, xT) == (max_capacity, max_capacity):
            transitions = [(max_capacity - 1, max_capacity), (max_capacity, max_capacity - 1)]
            probs = [q, 1 - q]
        elif xA == 0 and 0 < xT < max_capacity:
            transitions = [(1, xT), (0, xT + 1), (0, xT - 1)]
            probs = [0.5 * pA, 0.5 * pT, 0.5]
        elif xT == 0 and 0 < xA < max_capacity:
            transitions = [(xA + 1, 0), (xA, 1), (xA - 1, 0)]
            probs = [0.5 * pA, 0.5 * pT, 0.5]
        elif xA == max_capacity and 0 < xT < max_capacity:
            transitions = [(max_capacity - 1, xT), (max_capacity, xT + 1), (max_capacity, xT - 1)]
            probs = [0.5 * q, 0.5, 0.5 * (1 - q)]
        elif xT == max_capacity and 0 < xA < max_capacity:
            transitions = [(xA + 1, max_capacity), (xA - 1, max_capacity), (xA, max_capacity - 1)]
            probs = [0.5, 0.5 * q, 0.5 * (1 - q)]
        else:  # General case
            transitions = [(xA + 1, xT), (xA - 1, xT), (xA, xT + 1), (xA, xT - 1)]
            probs = [0.5 * pA, 0.5 * q, 0.5 * pT, 0.5 * (1 - q)]

        next_state = transitions[np.random.choice(len(transitions), p=probs)]
        xA, xT = next_state

        # Ensure the state does not go below zero or above max capacity
        xA = max(0, min(max_capacity, xA))
        xT = max(0, min(max_capacity, xT))

        states.append((xA, xT))

    states = np.array(states)
    A_queue_avg = np.mean(states[:, 0])
    T_queue_avg = np.mean(states[:, 1])

    return states, A_queue_avg, T_queue_avg

def plot_queues(states):
    plt.plot(states[:, 0], label='AGV Queue')
    plt.plot(states[:, 1], label='Trailer Queue')
    plt.xlabel('Time Step')
    plt.ylabel('Queue Length')
    plt.legend()
    plt.title('Queue Lengths Over Time')
    plt.show()

pA = 0.5  # Probability of arrival at AGV queue
pT = 0.5  # Probability of arrival at trailer queue
q = 0.25   # Probability that crane serves AGV queue
simulation_time = 1000000  # Total simulation time
max_capacity = 100  # Maximum capacity for each queue

states, A_queue_avg, T_queue_avg = simulation(pA, pT, q, simulation_time, max_capacity)
#plot_queues(states)

print(f"Average AGV queue length: {A_queue_avg}")
print(f"Average Trailer queue length: {T_queue_avg}")

nr_runs = 10
res_A = np.zeros(nr_runs)
res_T = np.zeros(nr_runs)
for run in range(nr_runs):
    _, res_A[run], res_T[run] = simulation(pA, pT, q, simulation_time, max_capacity)

print(np.mean(res_A))
print(np.mean(res_T))