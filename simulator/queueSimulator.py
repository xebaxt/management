#!/usr/bin/python3

import random
import numpy as np
import matplotlib.pyplot as plt
from queue import Queue, PriorityQueue

# ******************************************************************************
# Constants
# ******************************************************************************
SERVICE = 10.0 # av service time
TYPE1 = 1    
losses = True # False: infinite capacity of waiting line / True: Finite capacity of waiting line
SIM_TIME = 500000
number_servers=1
assignment= "ordered" # ordered/ random / roundRobin / leastCostly; 
service_time_distribution= "exponential" # exponential/ constant/ uniform/ gaussian/  
variance=0.1 # Only used if distribution=gaussian
# users=0
# counter=0
# delayed_packets=0 # Number of packets that experience waiting delay
# B=5 #Capacity of waiting line (only used if losses=True)
iter_B=False # False: Run program once / True: Run the program for different values of B

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
def arrival(time, FES, queue, servers ,B):
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
    else:
        data.lp +=1
        users -=1

    # if the server is idle start the service
    if users <= number_servers:
        
        # sample the service time
        service_time=serviceTimeGeneration()
        
        # schedule when the client will finish the server
        FES.put((time + service_time, "departure"))
        
        server_assignment(servers,time,service_time)


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
    
    if users>number_servers:
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
    if assignment == "ordered":
          j=0
    elif assignment == "random":
        random.shuffle(servers)
        j=0
    elif assignment == "roundRobin":
        if counter==len(servers):
            counter=0
        j=counter
    elif assignment == "leastCostly":
        j=0
        servers.sort(key=lambda x: x.cost, reverse=False)
    
    for i in range(j,len(servers)):
        if servers[i].idle:           
            servers[i].idle=False
            servers[i].busy_time+=service_time
            servers[i].dt=time + service_time
            counter=i+1
            break
    
    
# ******************************************************************************
# the "main" of the simulation
# ******************************************************************************

#Capacity of waiting line (only used if losses=True)
if losses and iter_B: #Change the value of B from 5 to 20 in steps of 5
    a=5
    b=25
    lost_p_matrix=[]
    av_delay_matrix=[]
else:
    a=5 # B=5
    b=10
    
for B in np.arange(a, b, 5):

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

    for LOAD in np.arange(0.025, 4.025, 0.025): 
    
        # SERVICE = 10.0 # av service time
        ARRIVAL   = SERVICE/LOAD # av inter-arrival time 
        # TYPE1 = 1 
        # SIM_TIME = 5000 #simulation time
        arrivals=0
        users=0
        delayed_packets=0 #number of packets that experience waiting delay
        MM1=[]
        # B=5
        # losses=True
        server_list=[]
        
        random.seed(42) 
    
        data = Measure(0,0,0,0,0,0,0,0,0)
        
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
                arrival(time, FES, MM1, server_list, B)
        
            elif event_type == "departure":
                departure(time, FES, MM1, server_list)
                
                
        #Save values of each iteration **************************************************
        users_queue.append(users)
        number_arr.append(data.arr)
        number_dep.append(data.dep)
        load_vector.append(LOAD)
        arr_rate.append(data.arr/time)
        dep_rate.append(data.dep/time)
        av_num_users.append(data.ut/time)
        av_num_users_q.append(data.uq/time)
        actual_queue_size.append(len(MM1))
        mm1_vector.append(MM1)
        arrival_rate.append(1/ARRIVAL)
        busy_time_list.append(server_list[i].busy_time)
        lost_p.append(data.lp/data.arr)
        if data.dep != 0:
            av_delay.append(data.delay/data.dep)
            av_wdelay.append(data.delay/data.dep)
            av_wdelay2.append(data.delay/data.dep)
        else:
            av_delay.append(0)
            
        # print output data
        print("\n\nMEASUREMENTS ***********************************************************")       
        print("\nNo. of users in the queue:",users,"\nNo. of arrivals =",data.arr,"- No. of departures =",data.dep)
        print("Number of lost packets: ",data.lp)
        print("loss probability: ",data.lp/data.arr)
        print("\nLoad: ",SERVICE/ARRIVAL)
        print("Arrival rate: ",data.arr/time," - Departure rate: ",data.dep/time) #lambda and mu
        print("\nAverage number of users: ",data.ut/time) #Mean number of customers in the queue E[N]
        print("Average number of users in queuing line: ",data.uq/time) #Mean number of customers in waiting line E[Nw]
        if data.dep>0:
            print("\nAverage delay: ",data.delay/data.dep)  #Average time in the queue E[T]
            print("Average waiting delay: ",data.wdelay/data.dep) #Average time in the waiting lineE[Tw]
        else:
            print("\nAverage delay: No departures")  #Average time in the queue E[T]    
            print("Average waiting delay: No departures") #Average time in the waiting lineE[Tw]
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
        print("\nSimulation time: ",SIM_TIME)
        print("\nActual queue size: ",len(MM1))
        
        if len(MM1)>0:
            print("Arrival time of the last element in the queue:",MM1[len(MM1)-1].arrival_time)
         
    if losses and iter_B:
        av_delay_matrix.append(av_delay)
        lost_p_matrix.append(lost_p)
    
# ******************************************************************************
# Ploting method
# ******************************************************************************        
def plotingMetrics():
    plt.figure()
    plt.plot(load_vector,number_arr, label='No. of arrivals')
    plt.plot(load_vector,number_dep, label='No. of departures')
    plt.xlabel(r'$Load:\rho=\lambda/\mu$')
    plt.title('No. of arrivals and departures vs load')
    plt.legend()
    plt.grid()
    plt.show()
    
    plt.figure()
    plt.plot(load_vector,arr_rate,label='Arrival rate')
    plt.plot(load_vector,dep_rate,label='Departure rate')
    plt.xlabel(r'$Load:\rho=\lambda/\mu$')
    plt.title('Arrival and departure rates vs load')
    plt.legend()
    plt.grid()
    plt.show()
    
    plt.figure()
    plt.plot(load_vector,av_num_users)
    plt.ylabel('Average number of packets')
    plt.xlabel(r'$Load:\rho=\lambda/\mu$')
    plt.title('Average number of packets in the queue E[N]')
    plt.grid()
    plt.show()
    
    plt.figure()
    plt.plot(load_vector,av_num_users_q)
    plt.ylabel('Average number of packets in waiting line')
    plt.xlabel(r'$Load:\rho=\lambda/\mu$')
    plt.title('Average number of packets in waiting line E[Nw]')
    plt.grid()
    plt.show()
    
    plt.figure()
    plt.plot(load_vector,av_delay)
    plt.ylabel('Time [s]')
    plt.xlabel(r'$Load:\rho=\lambda/\mu$')
    plt.title('Average time in the queue E[T]')
    plt.grid()
    plt.show()
    
    plt.figure()
    plt.plot(load_vector,av_wdelay)
    plt.ylabel('Average waiting delay')
    plt.xlabel(r'$Load:\rho=\lambda/\mu$')
    plt.title('Average waiting delay')
    plt.grid()
    plt.show()
    
    plt.figure()
    plt.plot(load_vector,av_wdelay2)
    plt.ylabel('Average waiting delay')
    plt.xlabel(r'$Load:\rho=\lambda/\mu$')
    plt.title('Average waiting delay considering only packets that experience delay')
    plt.grid()
    plt.show()
    
    plt.figure()
    plt.plot(load_vector,busy_time_list)
    plt.ylabel('Busy time')
    plt.xlabel(r'$Load:\rho=\lambda/\mu$')
    plt.title('Busy time')
    plt.grid()
    plt.show()
    
    plt.figure()
    plt.plot(load_vector,lost_p)
    plt.ylabel('Lost probability')
    plt.xlabel(r'$Load:\rho=\lambda/\mu$')
    plt.title('Lost probability')
    plt.grid()
    plt.show()
    
    if losses and iter_B:
        plt.figure()
        x=0
        for list in lost_p_matrix:
            plt.plot(load_vector,list , label='B='+str(x+5))
            x=x+5
        plt.ylabel('Lost probability')
        plt.xlabel(r'$Load:\rho=\lambda/\mu$')
        plt.title('Lost probability')
        plt.legend()
        plt.grid()
        plt.show()   
        
    if losses and iter_B:
        plt.figure()
        x=0
        for list in av_delay_matrix:
            plt.plot(load_vector,list , label='B='+str(x+5))
            x=x+5
        plt.ylabel('Time [s]')
        plt.xlabel(r'$Load:\rho=\lambda/\mu$')
        plt.title('Average time in the queue E[T]')
        plt.legend()
        plt.grid()
        plt.show()  
    

plotingMetrics() # Plot metrics