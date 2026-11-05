# Crane Scheduling at a Container Transfer Point

Markov-chain models and a discrete-event simulation of a single crane that moves containers between automated guided vehicles (AGVs) and trailers, set at the Port of Rotterdam.

**Stochastic Processes · Apr 2024 – Jul 2024**

<!-- REPORT_LINK -->

## Problem

At a transfer point, one crane unloads containers from AGVs (ship side) and trailers (land side), stores them, and loads them onto the other type of vehicle. The goal is a crane policy that keeps queues and waiting times short on both sides.

## Approach

- **Initial model:** a discrete-time Markov chain on two bounded queues. The transition matrix and balance equations give the stationary distribution as a function of the crane's service probability $q$, and from it the expected queue lengths. A simulation of $10^6$ steps reproduces them (about 1.00 for each queue in the symmetric case).
- **Extended model:** Poisson arrivals of ships and trucks with fixed cargo, normally distributed AGV trip times, and the crane as a two-state Markov chain.
- **Realistic model:** four unbounded queues (unload and load, for both AGVs and trailers) with exponential service times. This is analytically intractable, so a discrete-event simulation compares three crane policies: first-come first-serve, AGV priority, and priority to whichever vehicle has waited longest.

## Results

- In the initial model, the simulation reproduces the analytical expected queue lengths.
- In the realistic model, a vehicle is loaded only once a container from the other side is in storage. This couples the two sides: when AGVs and trailers arrive at the same rate, vehicles waiting for a matching container accumulate over time, so long-run queue lengths depend on the simulation horizon instead of settling to a steady state.

## Repository contents

- `src/initial_model_simulation.py`: Markov-chain simulation of the initial model
- `src/ExtendedModel/`: the building blocks of the event-driven simulator (`Car`, `Crane`, `Event`, `FES`, `Queues`, `SimResults`)
- `src/policy_fcfs.py`, `src/policy_agv_priority.py` and `src/policy_longest_wait.py`: the three crane policies (Simulations 1–3 in the report), each with an example experiment of 100 replications

Run any script from `src/`, for example `python policy_longest_wait.py`. A policy script takes 10–20 minutes for all 100 replications.

**Tools:** Python · NumPy · SciPy · Matplotlib
