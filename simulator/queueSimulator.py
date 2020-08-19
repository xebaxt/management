#!/usr/bin/python3

import random
import numpy as np
import matplotlib.pyplot as plt
from queue import Queue, PriorityQueue

# ******************************************************************************
# To take the measurements
# ******************************************************************************
class Measure:
    def __init__(self,Narr,Ndep,NAveraegUser,NAverageUserQueue,OldTimeEvent,AverageDelay,AverageWaitDelay,busy_time,lost_packets):
        self.arr = Narr #number of arr
        self.dep = Ndep #number of departures
        self.ut = NAveraegUser #number of average users
        self.uq = NAverageUserQueue #number of average users in queue line
        self.oldT = OldTimeEvent 
        self.delay = AverageDelay #time in the queue
        self.wdelay = AverageWaitDelay #time in the waiting line
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
    def __init__(self):

        # whether the server is idle or not
        self.idle = True


# ******************************************************************************
# arrivals 
# ******************************************************************************
def arrival(time, FES, queue):
    global users
    
    # cumulate statistics
    data.arr += 1
    data.ut += users*(time-data.oldT)
    if users>0:
        data.uq += (users-1)*(time-data.oldT)
    data.oldT = time

    inter_arrival = random.expovariate(lambd=1.0/ARRIVAL)# sample the time until the next event
    
    FES.put((time + inter_arrival, "arrival"))# schedule the next arrival

    users += 1 #increment count of users
    
    if (users <= B and  losses) or (not losses):
    
        client = Client(TYPE1,time)# create a record for the client
        queue.append(client)# insert the record in the queue
    
    else:
        data.lp +=1
        users -=1

    # if the server is idle start the service
    if users==1:
        service_time = random.expovariate(1.0/SERVICE)# sample the service time
        #service_time = 1 + random.uniform(0, SEVICE_TIME)

        FES.put((time + service_time, "departure"))# schedule when the client will finish the server

        data.busy_time +=service_time


# ******************************************************************************
# departures 
# ******************************************************************************
def departure(time, FES, queue):
    global users
    global delayed_packets
        
    # cumulate statistics
    data.dep += 1
    data.ut += users*(time-data.oldT)
   
    if users>1:
       delayed_packets +=1
       nextclient=queue[1]
       data.wdelay += (time-nextclient.arrival_time)
    
    client = queue.pop(0) # get the first element from the queue
    
    # do whatever we need to do when clients go away
    
    data.delay += (time-client.arrival_time)
    users -= 1
    
    # see whether there are more clients to in the line
    if users >0:
        service_time = random.expovariate(1.0/SERVICE)# sample the service time

        FES.put((time + service_time, "departure"))# schedule when the client will finish the server
        
        data.busy_time +=service_time #count busy time
        
        data.uq += (users-1)*(time-data.oldT) #cumulate statistic
        
    data.oldT = time
        
    
# ******************************************************************************
# the "main" of the simulation
# ******************************************************************************

#Lists to save values of each iteration
users_queue=[]
number_arr=[]
number_dep=[]
load_vector=[]
arr_rate=[]
dep_rate=[]
av_num_users=[]
av_num_users_q=[]
av_delay=[]
av_wdelay=[]
av_wdelay2=[]
actual_queue_size=[]
mm1_vector=[]
arrival_rate=[]
busy_time_list=[]
lost_p=[]

for LOAD in np.arange(0.05, 5, 0.05): 

    SERVICE = 10.0 # av service time
    ARRIVAL   = SERVICE/LOAD # av inter-arrival time 
    TYPE1 = 1 
    SIM_TIME = 5000 #simulation time
    # arrivals=0
    users=0
    delayed_packets=0 #number of packets that experience waiting delay
    #BusyServer=False # True: server is currently busy; False: server is currently idle
    MM1=[]
    B=5
    losses=True
    random.seed(42)
    
    data = Measure(0,0,0,0,0,0,0,0,0)
    time = 0
    
    # the list of events in the form: (time, type)
    FES = PriorityQueue() #we initialize the PQ class that will contain all the events that can occur on the system 
    
    FES.put((0, "arrival")) #schedule the first arrival at t=0
    
    # simulate until the simulated time reaches a constant
    while time < SIM_TIME:   
        (time, event_type) = FES.get()
    
        if event_type == "arrival":
            arrival(time, FES, MM1)
    
        elif event_type == "departure":
            departure(time, FES, MM1)
            
            
    #Save values of each iteration **************************************************
    users_queue.append(users)
    number_arr.append(data.arr)
    number_dep.append(data.dep)
    load_vector.append(SERVICE/ARRIVAL)
    arr_rate.append(data.arr/time)
    dep_rate.append(data.dep/time)
    av_num_users.append(data.ut/time)
    av_num_users_q.append(data.uq/time)
    actual_queue_size.append(len(MM1))
    mm1_vector.append(MM1)
    arrival_rate.append(1/ARRIVAL)
    busy_time_list.append(data.busy_time)
    lost_p.append(data.lp/data.arr)
    if data.dep != 0:
        av_delay.append(data.delay/data.dep)
        av_wdelay.append(data.delay/data.dep)
        av_wdelay2.append(data.delay/data.dep)
 
    # print output data**************************************************************
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
     
#Ploting*****************************************************************************
plt.figure()
plt.plot(arrival_rate,users_queue)
plt.ylabel('No. of users in the queue')
plt.xlabel(r'$\lambda$')
plt.title('No. of users in the queue')
plt.grid()

plt.figure()
plt.plot(arrival_rate,number_arr)
plt.ylabel('No. of arrivals')
plt.xlabel(r'$\lambda$')
plt.title('No. of arrivals')
plt.grid()

plt.figure()
plt.plot(arrival_rate,number_dep)
plt.ylabel('No. of departures')
plt.xlabel(r'$\lambda$')
plt.title('No. of departures')
plt.grid()

plt.figure()
plt.plot(arrival_rate,arr_rate)
plt.ylabel('Arrival rate')
plt.xlabel(r'$\lambda$')
plt.title('Arrival rate')
plt.grid()

plt.figure()
plt.plot(arrival_rate,dep_rate)
plt.ylabel('Departure rate')
plt.xlabel(r'$\lambda$')
plt.title('Departure rate')
plt.grid()

plt.figure()
plt.plot(arrival_rate,av_num_users)
plt.ylabel('Average number of users')
plt.xlabel(r'$\lambda$')
plt.title('Average number of users')
plt.grid()

plt.figure()
plt.plot(arrival_rate,av_num_users_q)
plt.ylabel('Average number of users in queuing line')
plt.xlabel(r'$\lambda$')
plt.title('Average number of users in queuing line')
plt.grid()

plt.figure()
plt.plot(arrival_rate,av_delay)
plt.ylabel('Average delay')
plt.xlabel(r'$\lambda$')
plt.title('Average delay')
plt.grid()

plt.figure()
plt.plot(arrival_rate,av_wdelay)
plt.ylabel('Average waiting delay')
plt.xlabel(r'$\lambda$')
plt.title('Average waiting delay')
plt.grid()

plt.figure()
plt.plot(arrival_rate,av_wdelay2)
plt.ylabel('Average waiting delay')
plt.xlabel(r'$\lambda$')
plt.title('Average waiting delay considering only packets that experience delay')
plt.grid()

plt.figure()
plt.plot(arrival_rate,busy_time_list)
plt.ylabel('Busy time')
plt.xlabel(r'$\lambda$')
plt.title('Busy time')
plt.grid()

plt.figure()
plt.plot(arrival_rate,actual_queue_size)
plt.ylabel('Actual queue size')
plt.xlabel(r'$\lambda$')
plt.title('Actual queue size')
plt.grid()


plt.figure()
plt.plot(arrival_rate,lost_p)
plt.ylabel('Lost probability')
plt.xlabel(r'$\lambda$')
plt.title('Lost probability')
plt.grid()
