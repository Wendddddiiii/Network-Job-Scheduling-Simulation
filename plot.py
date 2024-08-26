import random
import matplotlib.pyplot as plt
from main import get_arrival_time, weighted_response_time

def plot_arrival_time(lenda, a2l, a2u, time_end, seed):
    random.seed(seed)
    arrival_times = []
    total_time = 0
    while total_time < time_end:
        inter_arrival_time = get_arrival_time(lenda, a2l, a2u)
        total_time += inter_arrival_time
        arrival_times.append(inter_arrival_time)
    plt.hist(arrival_times, bins=100, edgecolor='black')
    plt.xlabel('Inter-arrival time')
    plt.ylabel('Frequency')
    plt.show()

def plot_n0_seed(n0, seed, l=10000):
    mts = []
    for i in range(1, l, 100):
        mt = weighted_response_time(n0, i, seed)
        mts.append([i, mt])

    x = [point[0] for point in mts]
    y = [point[1] for point in mts]

    plt.plot(x, y)
    plt.ylim(0)
    plt.title(f'n0 = {n0}, seed = {seed}')
    plt.xlabel('Length of simulation')
    plt.ylabel('Weighted mean response time')
    plt.show()
