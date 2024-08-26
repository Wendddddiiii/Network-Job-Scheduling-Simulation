import os
import sys
import random
import decimal
import math
import numpy
from matplotlib import pyplot as plt

# Event types
ARRIVAL = 0
DEPARTURE = 1


# generates the service time for server group 0 
def get_service_time_group_0(alpha_0, beta_0, eta_0):
    gamma_0 = alpha_0 ** (-eta_0) - beta_0 ** (-eta_0)
    u = random.random()
    return round(math.exp(math.log(beta_0 / (gamma_0 * u)) / (beta_0 + 1)),4)

# generates the service time for server group 1
def get_service_time_group_1(alpha_1, eta_1):
    gamma_1 = alpha_1 ** (-eta_1)
    u = random.random()
    return round(math.exp(math.log(eta_1 / (gamma_1 * u)) / (eta_1 + 1)),4)


def get_arrival_time(lenda, a2l, a2u):
    a1 = random.expovariate(lenda)
    a2 = random.uniform(a2l, a2u)
    return round(a1 * a2,4)


# simulate a job in the system 
class Job:
    def __init__(self, job_id, arrival_time, service_time,server_group_id):
        self.job_id = job_id
        self.server_group_id = server_group_id
        self.arrival_time = arrival_time
        self.service_time = service_time
        self.start_time = float('inf')
        self.complition_time = None
        self.server_groups_passed = []
    def __str__(self):
        return f"Job {self.job_id} (Group {self.server_group_id})"

#simulate an event in the system 
class Event:
    def __init__(self, event_type, time, job):
        self.event_type = event_type
        self.time = time
        self.job = job
    
    def __str__(self):
        return f"Event:Type: {self.event_type}, Time: {self.time:.4f}, Job: {self.job}"

class EventList:
    def __init__(self):
        self.events = []

    def insert(self, event):
        self.events.append(event)
        self.events.sort(key=lambda x: x.time)

    def pop(self):
        return self.events.pop(0)

    def is_empty(self):
        return len(self.events) == 0
    
    def __str__(self):
        s = ""
        for event in self.events:
            s += str(event) + "\n"
        return s


class Server:
    def __init__(self, id, group_id,time_limit=float('inf')):
        self.id = id
        self.group_id = group_id
        self.time_limit = time_limit
        self.current_job = None
        self.next_event_time = float('inf')
    
    def __str__(self):
        return f"Server {self.id} - Group {self.group_id} -Job {self.current_job}"

class ServerGroup:
    def __init__(self, group_id,server_num,event_list,time_limit=float('inf')):
        self.servers = []
        self.group_id = group_id
        self.time_limit = time_limit
        self.event_list = event_list
        self.job_queue = []
        for i in range(server_num):
            server = Server(i,group_id,time_limit)
            self.servers.append(server)
    
    def getIdleServer(self):
        for server in self.servers:
            if server.current_job is None:
                return server
        return None

    def addJob(self,job,clock_time):
        if job is None:
            return
        idleServer = self.getIdleServer()
        if idleServer is not None:
            job.start_time = clock_time
            job.server_groups_passed.append(self.group_id)
            idleServer.current_job = job
            new_event = Event(DEPARTURE,clock_time + min(self.time_limit,job.service_time),job)
            self.event_list.insert(new_event)
        else:
            self.job_queue.append(job)
    
    def handleEvent(self,event):
        if event.event_type == ARRIVAL:
            if event.job.server_group_id == self.group_id:
                self.addJob(event.job,event.time)
            else:
                return
        else:
            job = event.job
            if abs(event.time - job.start_time -job.service_time)<0.0001:
                if job.server_groups_passed[-1] != self.group_id:
                    return
                for server in self.servers:
                    if server.current_job and server.current_job.job_id == job.job_id:
                        job.complition_time = event.time
                        server.current_job = None
                        if self.job_queue:
                            self.addJob(self.job_queue.pop(0),event.time)
                        break
            else:
                if self.group_id == 1:
                    self.addJob(job,event.time)
                else:
                    for server in self.servers:
                        if server.current_job and server.current_job.job_id == job.job_id:
                            server.current_job = None
                            if self.job_queue:
                                self.addJob(self.job_queue.pop(0),event.time)
                            break

    def __str__(self):
        return f"Server Group {self.group_id} - {len(self.servers)} Servers - Time Limit {self.time_limit}"

def main(test_number):
    # Read configuration files
    job_records = []
    config_folder = 'config'
    mode_file = os.path.join(config_folder, f'mode_{test_number}.txt')
    para_file = os.path.join(config_folder, f'para_{test_number}.txt')
    interarrival_file = os.path.join(config_folder, f'interarrival_{test_number}.txt')
    service_file = os.path.join(config_folder, f'service_{test_number}.txt')

    with open(mode_file, 'r') as f:
        mode = f.read().strip()

    with open(para_file, 'r') as f:
        para_lines = f.readlines()
        n = int(para_lines[0])
        n_0 = int(para_lines[1])
        n_1 = n - n_0
        T_limit = float(para_lines[2])
        if mode == 'random':
            time_end = float(para_lines[3])
    # Initialize system

    event_list = EventList()

    server_group0 = ServerGroup(group_id=0,server_num=n_0,event_list=event_list,time_limit=T_limit)
    server_group1 = ServerGroup(group_id=1,server_num=n_1,event_list=event_list)

    if mode == 'trace':
        # Read inter-arrival times and service times from files
        with open(interarrival_file, 'r') as f:
            arrival_times = [float(line.strip()) for line in f.readlines()]
        cumulative_arrival_times = []
        current_time = 0.0
        for interarrival in arrival_times:
            current_time += interarrival
            cumulative_arrival_times.append(current_time)

        with open(service_file, 'r') as f:
            service_times = []
            server_groups = []
            for line in f.readlines():
                service_time, server_group = line.strip().split()
                service_times.append(float(service_time))
                server_groups.append(int(server_group))

        # Schedule initial arrivals
        i = 0
        for arrival_time, service_time, server_group in zip(cumulative_arrival_times, service_times, server_groups):
            job = Job(i,arrival_time,service_time,server_group)
            job_records.append(job)
            event = Event(ARRIVAL, arrival_time, job)
            event_list.insert(event)
            i += 1
    elif mode == 'random':
        # Read parameters from files
        with open(interarrival_file, 'r') as f:
            lenda, a2l, a2u = [float(x) for x in f.read().split()]

        with open(service_file, 'r') as f:
            service_lines = f.readlines()
            p_0 = float(service_lines[0])
            alpha_0, beta_0, eta_0 = [float(x) for x in service_lines[1].split()]
            alpha_1, eta_1 = [float(x) for x in service_lines[2].split()]
        arrival_time = 0
        i = 0
        while True:
        # Schedule initial arrival
            inter_arrival_time = get_arrival_time(lenda, a2l, a2u)
            arrival_time += inter_arrival_time
            if arrival_time > time_end:
                break
            server_group = 0 if random.random() < p_0 else 1
            service_time = get_service_time_group_0(alpha_0, beta_0, eta_0) if server_group==0 else get_service_time_group_1(alpha_1, eta_1)
            job = Job(i,arrival_time,service_time,server_group)
            job_records.append(job)
            event = Event(ARRIVAL, arrival_time, job)
            event_list.insert(event)
            i += 1
    
    while not event_list.is_empty():
        event = event_list.pop()
        server_group0.handleEvent(event)
        server_group1.handleEvent(event)

    out_folder = 'output'
    mrt_file = os.path.join(out_folder, f'mrt_{test_number}.txt')
    dep_file = os.path.join(out_folder, f'dep_{test_number}.txt')
    job_records = sorted(job_records, key=lambda x: x.complition_time)
    sum0 = 0
    num0 = 0
    sum1 = 0
    num1 = 0
    
    with open(dep_file, 'w') as f:
        for job in job_records:
            group = 'r0' if len(job.server_groups_passed)>1 else job.server_groups_passed[0]
            f.write(f"{job.arrival_time:.4f} {job.complition_time:.4f} {group}\n")
            if group == 0:
                sum0 += job.complition_time - job.arrival_time
                num0 += 1
            if group == 1:
                sum1 += job.complition_time - job.arrival_time
                num1 += 1
    group_0_mrt = sum0/num0 if num0 else 0
    group_1_mrt = sum1/num1 if num1 else 0
    
    with open(mrt_file, 'w') as f:
        f.write(f"{group_0_mrt:.4f} {group_1_mrt:.4f}\n")

def weighted_response_time(n_0,length_of_simulation,seed):
    random.seed(seed)
    n = 10
    n_1 = n - n_0
    lenda,a2l,a2u =(3.1,0.85,1.21)
    p_0 = 0.74
    alpha_0, beta_0, eta_0 = (0.5,5.7,1.9)
    alpha_1,eta_1 = (2.7,2.5)
    T_limit = 3.3
    job_records = []
    event_list = EventList()

    server_group0 = ServerGroup(group_id=0,server_num=n_0,event_list=event_list,time_limit=T_limit)
    server_group1 = ServerGroup(group_id=1,server_num=n_1,event_list=event_list)

    arrival_time = 0
    i = 0
    while i<length_of_simulation:
        inter_arrival_time = get_arrival_time(lenda, a2l, a2u)
        arrival_time += inter_arrival_time
        server_group = 0 if random.random() < p_0 else 1
        service_time = get_service_time_group_0(alpha_0, beta_0, eta_0) if server_group==0 else get_service_time_group_1(alpha_1, eta_1)
        job = Job(i,arrival_time,service_time,server_group)
        job_records.append(job)
        event = Event(ARRIVAL, arrival_time, job)
        event_list.insert(event)
        i += 1
    while not event_list.is_empty():
        event = event_list.pop()
        server_group0.handleEvent(event)
        server_group1.handleEvent(event)

    sum0 = 0
    num0 = 0
    sum1 = 0
    num1 = 0

    for job in job_records:
        group = 'r0' if len(job.server_groups_passed)>1 else job.server_groups_passed[0]
        if group == 0:
            sum0 += job.complition_time - job.arrival_time
            num0 += 1
        if group == 1:
            sum1 += job.complition_time - job.arrival_time
            num1 += 1

    t0 = sum0/num0 if num0 else 0
    t1= sum1/num1 if num1 else 0
    w0 = 0.83
    w1 = 0.059
    return w0*t0 + w1*t1


if __name__ == "__main__":
    main(sys.argv[1])

