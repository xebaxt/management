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

#SIM_TIME = 500000
SIM_TIME = 500000000

arrivals=0
users=0
users_old=0
delayed_packets=0
BusyServer=False # True: server is currently busy; False: server is currently idle

MM1=[]


# ******************************************************************************
# To take the measurements
# ******************************************************************************
class Measure:
    def __init__(self,Narr,Ndep,NAveraegUser,NAverageUserQueue,OldTimeEvent,AverageDelay,AverageWaitDelay, OldTimeDeparture):
        self.arr = Narr #number of arr
        self.dep = Ndep #number of departures
        self.ut = NAveraegUser #number of average users
        self.uq = NAverageUserQueue #number of average users in queue line
        self.oldT = OldTimeEvent #
        self.oldD = OldTimeDeparture
        self.delay = AverageDelay
        self.wdelay = AverageWaitDelay
        
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
    def __init__(self):

        # whether the server is idle or not
        self.idle = True


# ******************************************************************************

# arrivals *********************************************************************
def arrival(time, FES, queue):
    global users
    
    #print("Arrival no. ",data.arr+1," at time ",time," with ",users," users" )
    
    # cumulate statistics
    data.arr += 1
    data.ut += users*(time-data.oldT)
    if users>0:
        data.uq += (users-1)*(time-data.oldT)
    data.oldT = time

    # sample the time until the next event
    inter_arrival = random.expovariate(lambd=1.0/ARRIVAL)
    
    # schedule the next arrival
    FES.put((time + inter_arrival, "arrival"))

    users += 1
    
    # create a record for the client
    client = Client(TYPE1,time)

    # insert the record in the queue
    queue.append(client)

    # if the server is idle start the service
    if users==1:
        
        # sample the service time
        service_time = random.expovariate(1.0/SERVICE)
        #service_time = 1 + random.uniform(0, SEVICE_TIME)

        # schedule when the client will finish the server
        FES.put((time + service_time, "departure"))

# ******************************************************************************

# departures *******************************************************************
def departure(time, FES, queue):
    global users
    global delayed_packets
    # get the first element from the queue
    client = queue.pop(0)
    
    
    #print("Departure no. ",data.dep+1," at time ",time," with ",users," users" )
    
    # cumulate statistics
    data.dep += 1
    data.ut += users*(time-data.oldT)
    
    if users>1:
        delayed_packets +=1
        nextclient=queue[0]
        data.wdelay += (time-nextclient.arrival_time)
    # do whatever we need to do when clients go away
    
    data.delay += (time-client.arrival_time)
    users -= 1
    
    # see whether there are more clients to in the line
    if users >0:
        # sample the service time
        service_time = random.expovariate(1.0/SERVICE)

        # schedule when the client will finish the server
        FES.put((time + service_time, "departure"))
        
        data.uq += (users-1)*(time-data.oldT)
    data.oldT = time
        
# ******************************************************************************
# the "main" of the simulation
# ******************************************************************************

random.seed(42)  #same ramdom results

data = Measure(0,0,0,0,0,0,0,0)

# the simulation time 
time = 0

# the list of events in the form: (time, type)
FES = PriorityQueue()


# schedule the first arrival at t=0
FES.put((0, "arrival"))

# simulate until the simulated time reaches a constant
while time < SIM_TIME:
    (time, event_type) = FES.get()

    if event_type == "arrival":
        arrival(time, FES, MM1)

    elif event_type == "departure":
        departure(time, FES, MM1)

# print output data
print("MEASUREMENTS \n\nNo. of users in the queue:",users,"\nNo. of arrivals =",
      data.arr,"- No. of departures =",data.dep)

print("Load: ",SERVICE/ARRIVAL)
print("\nArrival rate: ",data.arr/time," - Departure rate: ",data.dep/time)

print("\nAverage number of users: ",data.ut/time)
print("\nAverage number of users in queuing line: ",data.uq/time) #E[Nw]

print("Average delay: ",data.delay/data.dep)
print("Average waiting delay: ",data.wdelay/data.dep) #E[Tw]
print("Average waiting delay: ",data.wdelay/delayed_packets) #E[Tw]
print("Actual queue size: ",len(MM1))

if len(MM1)>0:
    print("Arrival time of the last element in the queue:",MM1[len(MM1)-1].arrival_time)
    
