#!/usr/bin/python3

import random
from queue import Queue, PriorityQueue

# ******************************************************************************
# Constants
# ******************************************************************************
LOAD=0.85
SERVICE = 10.0 # av service time
ARRIVAL   = SERVICE/LOAD # av inter-arrival time
TYPE1 = 1    # is not used
losses=False
SIM_TIME = 500000
# SIM_TIME = 500000000
number_servers=2
# arrivals=0
users=0
delayed_packets=0 #number of packets that experience waiting delay
BusyServer=False # True: server is currently busy; False: server is currently idle
B=5
MM1=[]
server_list=[]


# ******************************************************************************
# To take the measurements
# ******************************************************************************
class Measure:
    def __init__(self,Narr,Ndep,NAveraegUser,NAverageUserQueue,OldTimeEvent,AverageDelay,AverageWaitDelay,busy_time,lost_packets):
        self.arr = Narr #number of arr
        self.dep = Ndep #number of departures
        self.ut = NAveraegUser #number of average users
        self.uq = NAverageUserQueue #number of average users in queue line
        self.oldT = OldTimeEvent #
        self.delay = AverageDelay
        self.wdelay = AverageWaitDelay
        self.busy_time = busy_time #time that server spends in a busy state
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
    def __init__(self,is_idle,busy_t,depar_time):

        # whether the server is idle or not
        self.idle = is_idle
        self.busy_time=busy_t
        self.dt=depar_time


# ******************************************************************************

# arrivals *********************************************************************
def arrival(time, FES, queue, servers):
    global users
    
    #print("Arrival no. ",data.arr+1," at time ",time," with ",users," users" )
    
    # cumulate statistics
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
    else:
        data.lp +=1
        users -=1

    # if the server is idle start the service
    if users <= number_servers:
        
        # sample the service time
        service_time = random.expovariate(1.0/SERVICE)
        #service_time = 1 + random.uniform(0, SEVICE_TIME)

        # schedule when the client will finish the server
        FES.put((time + service_time, "departure"))
        
        for i in range(len(servers)):
            if servers[i].idle:           
                servers[i].idle=False
                servers[i].busy_t+=service_time
                servers[i].dt=time + service_time
                break
        
        
# ******************************************************************************

# departures *******************************************************************
def departure(time, FES, queue, servers):
    global users
    global delayed_packets
    # get the first element from the queue
    client = queue.pop(0)
    
    for i in range(len(servers)):
            if not servers[i].idle and servers[i].dt==time: 
                servers[i].idle=True
                break
    
    #print("Departure no. ",data.dep+1," at time ",time," with ",users," users" )
    
    # cumulate statistics
    data.dep += 1
    data.ut += users*(time-data.oldT)
    if users>number_servers:
        data.uq += (users-number_servers)*(time-data.oldT)
    
    if users>number_servers:
        delayed_packets +=1
        nextclient=queue[number_servers-1]
        data.wdelay += (time-nextclient.arrival_time)
    # do whatever we need to do when clients go away
    
    data.delay += (time-client.arrival_time)
    users -= 1
    
    # see whether there are more clients to in the line
    if users > number_servers-1:
        # sample the service time
        service_time = random.expovariate(1.0/SERVICE)

        # schedule when the client will finish the server
        FES.put((time + service_time, "departure"))
        
        for i in range(len(servers)):
            if servers[i].idle:           
                servers[i].idle=False
                servers[i].busy_t+=service_time
                servers[i].dt=time + service_time
                break
        
    data.oldT = time
        
# ******************************************************************************
# the "main" of the simulation
# ******************************************************************************

random.seed(42)  #same ramdom results

data = Measure(0,0,0,0,0,0,0,0,0)

# the simulation time 
time = 0

# the list of events in the form: (time, type)
FES = PriorityQueue()


# schedule the first arrival at t=0
FES.put((0, "arrival"))

server=Server(True, 0,0)
for i in range(number_servers):
    servers.append(server)

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
print("Average waiting delay considering only packets that experience delay: ",data.wdelay/delayed_packets)
print("\nBusy time: ",data.busy_time, "- simulation time: ",SIM_TIME)
print("\nActual queue size: ",len(MM1))

if len(MM1)>0:
    print("Arrival time of the last element in the queue:",MM1[len(MM1)-1].arrival_time)
