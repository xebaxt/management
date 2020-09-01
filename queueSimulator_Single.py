#!/usr/bin/python3

import random
import numpy as np
from queue import Queue, PriorityQueue

# ******************************************************************************
# Constants
# ******************************************************************************
LOAD = 0.85
SERVICE = 10.0 # av service time
ARRIVAL = SERVICE/LOAD # av inter-arrival time
TYPE1 = 1    
losses = False # False: infinite capacity of waiting line / True: Finite capacity of waiting line
SIM_TIME = 500000
number_servers=1
assignment= "leastCostly" # random / roundRobin / leastCostly; 
service_time_distribution= "exponential" # exponential/ constant/ uniform/ gaussian/  
variance=0.1
users=0
counter=0
delayed_packets=0 # Number of packets that experience waiting delay
B=2 #Capacity of waiting line (only used if losses=True)
MM1=[]
server_list=[]


# ******************************************************************************
# To take the measurements
# ******************************************************************************
class Measure:
    def __init__(self,Narr,Ndep,NAveraegUser,NAverageUserQueue,OldTimeEvent,AverageDelay,AverageWaitDelay,busy_time,lost_packets):
        self.arr = Narr # Number of arrivals
        self.dep = Ndep # Number of departures
        self.ut = NAveraegUser # Number of average users
        self.uq = NAverageUserQueue # Number of average users in queue line
        self.oldT = OldTimeEvent  
        self.delay = AverageDelay # Time in the queue
        self.wdelay = AverageWaitDelay # Time in the waiting line
        self.busy_time = busy_time # Time that server spends in a busy state
        self.lp=lost_packets
        
        
# ******************************************************************************
# Client
# ******************************************************************************
class Client:
    def __init__(self,type,arrival_time):
        self.type = type
        self.arrival_time = arrival_time


# ******************************************************************************
# Server
# ******************************************************************************
class Server(object):

    # constructor
    def __init__(self,server_id,is_idle,busy_t,depar_time,numDep,server_cost):

        # whether the server is idle or not
        self.id=server_id
        self.idle = is_idle
        self.busy_time=busy_t
        self.dt=depar_time
        self.dep_num=numDep
        self.cost=server_cost


# ******************************************************************************
# Arrivals 
# ******************************************************************************
def arrival(time, FES, queue, servers):
    global users

    data.arr += 1
    data.ut += users*(time-data.oldT)
    if users>number_servers:
        data.uq += (users-number_servers)*(time-data.oldT)
    data.oldT = time

    # sample the time until the next event
    inter_arrival = random.expovariate(lambd=1.0/ARRIVAL)
    
    # schedule the next arrival
    FES.put((time + inter_arrival, "arrival"))

   
    users += 1
    
    if (users <= B and  losses) or (not losses):
        # create a record for the client
        client = Client(TYPE1,time)

        # insert the record in the queue
        queue.append(client)
        
        # if the server is idle start the service
        if users <= number_servers:
            
            # sample the service time
            service_time=serviceTimeGeneration()
            
            # schedule when the client will finish the server
            FES.put((time + service_time, "departure"))
            
            server_assignment(servers,time,service_time)
    else:
        data.lp +=1
        users -=1

        
# ******************************************************************************
# Departures
# ******************************************************************************
def departure(time, FES, queue, servers):
    global users
    global delayed_packets
    
    # get the first element from the queue
    client = queue.pop(0)
    
    for i in range(len(servers)):
            if not servers[i].idle and servers[i].dt==time: 
                servers[i].idle=True
                servers[i].dep_num+=1
                break

    data.dep += 1
    data.ut += users*(time-data.oldT)
    if users>number_servers:
        data.uq += (users-number_servers)*(time-data.oldT)
        delayed_packets +=1
        nextclient=queue[number_servers-1]
        data.wdelay += (time-nextclient.arrival_time)

    data.delay += (time-client.arrival_time)
    users -= 1
    
    # see whether there are more clients to in the line
    if users > number_servers-1:
        # sample the service time
        service_time=serviceTimeGeneration()

        # schedule when the client will finish the server
        FES.put((time + service_time, "departure"))
        
        server_assignment(servers,time,service_time)
        
    data.oldT = time
    
# ******************************************************************************
# Service time distribution method
# ******************************************************************************     
def serviceTimeGeneration():        
    if service_time_distribution == "exponential":
        service_time = random.expovariate(1.0/SERVICE)
    elif service_time_distribution == "constant":
        service_time = 1.0/SERVICE
    elif service_time_distribution == "uniform":
        service_time = random.uniform(0, 1.0/SERVICE)
    elif service_time_distribution == "gaussian":
        service_time = random.gauss(1.0/SERVICE, variance)   
    return service_time    
        
# ******************************************************************************
# Server assignment method
# ****************************************************************************** 
def server_assignment(servers,time,service_time):
    global counter
    j=0
    assigned=False
    while assigned==False:
        if assignment == "random":
            random.shuffle(servers)
        elif assignment == "roundRobin":
            if counter==len(servers):
                counter=0
            j=counter
        elif assignment == "leastCostly":
            servers.sort(key=lambda x: x.cost, reverse=False)
        
        for i in range(j,len(servers)):
            if servers[i].idle:           
                servers[i].idle=False
                servers[i].busy_time+=service_time
                servers[i].dt=time + service_time
                counter=i+1
                assigned=True
                break
            else:
                counter=number_servers
 
# ******************************************************************************
# the "main" of the simulation
# ******************************************************************************
random.seed(42) 

data = Measure(0,0,0,0,0,0,0,0,0)
overall_cost=0

# the simulation time 
time = 0

# the list of events in the form: (time, type)
FES = PriorityQueue() # PQ class that will contain all the events that can occur on the system 


# schedule the first arrival at t=0
FES.put((0, "arrival"))


for i in range(number_servers):
    server_list.append(Server(i+1,True, 0,0,0, abs(np.random.normal()*100)))

# simulate until the simulated time reaches a constant
while time < SIM_TIME:
    (time, event_type) = FES.get()

    if event_type == "arrival":
        arrival(time, FES, MM1, server_list)

    elif event_type == "departure":
        departure(time, FES, MM1, server_list)

# print output data
print("MEASUREMENTS ***********************************************************")       
print("\nNo. of users in the queue:",users,"\nNo. of arrivals =",data.arr,"- No. of departures =",data.dep)
print("Number of lost packets: ",data.lp)
print("loss probability: ",data.lp/data.arr)
print("\nLoad: ",SERVICE/ARRIVAL)
print("Arrival rate: ",data.arr/time," - Departure rate: ",data.dep/time) #lambda and mu
print("\nAverage number of users: ",data.ut/time) #Mean number of customers in the queue E[N]
print("Average number of users in queuing line: ",data.uq/time) #Mean number of customers in waiting line E[Nw]
print("\nAverage delay: ",data.delay/data.dep)  #Average time in the queue E[T]
print("Average waiting delay: ",data.wdelay/data.dep) #Average time in the waiting lineE[Tw]
if delayed_packets>0:
    print("Average waiting delay considering only packets that experience delay: ",data.wdelay/delayed_packets)
else:
    print("Average waiting delay considering only packets that experience delay: No delayed packages")
print("\nAlgorithm to assign new requests to an available server:", assignment)
server_list.sort(key=lambda x: x.id, reverse=False)
for i in range(len(server_list)):
    print("\n***Server ",i+1,"***")
    print("  Busy time:",server_list[i].busy_time)
    if server_list[i].dep_num>0:
        print("  Average service time:",server_list[i].busy_time/server_list[i].dep_num)
    else:
        print("  Average service time: Not used")
    print("  No. of departures:",server_list[i].dep_num)
    print("  Cost:",server_list[i].cost)
    overall_cost=overall_cost+(((server_list[i].busy_time)/3600)*server_list[i].cost)
print("\nOverall cost: ",overall_cost)
print("\nSimulation time: ",SIM_TIME)
print("\nActual queue size: ",len(MM1))

if len(MM1)>0:
    print("Arrival time of the last element in the queue:",MM1[len(MM1)-1].arrival_time)