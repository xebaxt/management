#!/usr/bin/python3

import random
import numpy as np
import matplotlib.pyplot as plt
from queue import Queue, PriorityQueue

# ******************************************************************************
# Constants
# ******************************************************************************
SERVICE = 20.0 # av service time
TYPE1 = 1    
losses = True # False: infinite capacity of waiting line / True: Finite capacity of waiting line
SIM_TIME = 500000
number_servers=2
assignment= "random" # / random / roundRobin / leastCostly; 
service_time_distribution= "exponential" # exponential/ constant/ uniform/ gaussian/  
variance=0.1 # Only used if distribution=gaussian
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

#Capacity of waiting line (only used if losses=True)
if losses and iter_B: #Change the value of B from 5 to 20 in steps of 5
    capacity=[number_servers,5,10,15,20]
    lost_p_matrix=[]
    av_delay_matrix=[]
else:
    capacity=[5]

server_cost=[]
for i in range(number_servers):
    server_cost.append(100-(i*80))

for B in capacity:

    #Lists to save values of each iteration
    users_queue=[]
    number_arr=[]
    number_dep=[]
    number_dep_matrix=[]
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
    busy_time_list_matrix=[]
    lost_p=[]
    overall_cost_list=[]

    for LOAD in np.arange(0.025, 4.025, 0.025): 
        
        busy_time_list=[]
        dep_num_server=[]
        counter=0
        overall_cost=0
        
        ARRIVAL   = SERVICE/LOAD # av inter-arrival time 
        arrivals=0
        users=0
        delayed_packets=0 #number of packets that experience waiting delay
        MM1=[]
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
            server_list.append(Server(i+1,True, 0,0,0, server_cost[i]))
        
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
        server_list.sort(key=lambda x: x.id, reverse=False)
        for i in range(len(server_list)):
            busy_time_list.append(server_list[i].busy_time)
            dep_num_server.append(server_list[i].dep_num)
            overall_cost=overall_cost+(((server_list[i].busy_time)/3600)*server_list[i].cost)
        lost_p.append(data.lp/data.arr)
        if data.dep != 0:
            av_delay.append(data.delay/data.dep)
            av_wdelay.append(data.delay/data.dep)
            av_wdelay2.append(data.delay/data.dep)
        else:
            av_delay.append(0)
        overall_cost_list.append(overall_cost)
        
        # print output data
        print("\n\nMEASUREMENTS ***********************************************************")       
        print("\nNo. of users in the queue:",users,"\nNo. of arrivals =",data.arr,"- No. of departures =",data.dep)
        print("Number of lost packets: ",data.lp)
        print("loss probability: ",data.lp/data.arr)
        if losses:
            print("Capacity: ",B)
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
        print("\nOverall cost: ",overall_cost)            
        print("\nSimulation time: ",SIM_TIME)
        print("\nActual queue size: ",len(MM1))
        
        if len(MM1)>0:
            print("Arrival time of the last element in the queue:",MM1[len(MM1)-1].arrival_time)
         
        busy_time_list_matrix.append(busy_time_list)
        number_dep_matrix.append(dep_num_server)
            
    if losses and iter_B:
        av_delay_matrix.append(av_delay)
        lost_p_matrix.append(lost_p)
        
# ******************************************************************************
# Ploting method
# ******************************************************************************        
def plotingMetrics():
    
    if not iter_B:
    
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
        plt.plot(load_vector,lost_p)
        plt.ylabel('Loss probability')
        plt.xlabel(r'$Load:\rho=\lambda/\mu$')
        plt.title('Loss probability')
        plt.grid()
        plt.show()
        
        server_list.sort(key=lambda x: x.id, reverse=False)
        plt.figure()
        for i in range(len(server_list)):
            btime=[]
            for list in busy_time_list_matrix:
                btime.append(list[i])
            plt.plot(load_vector,btime, label='Server '+str(i+1))
        plt.ylabel('Time [s]')
        plt.xlabel(r'$Load:\rho=\lambda/\mu$')
        plt.title('Busy time')
        plt.legend()
        plt.grid()
        plt.show()
        
        plt.figure()
        for i in range(len(server_list)):
            deps=[]
            for list in number_dep_matrix:
                deps.append(list[i])
            plt.plot(load_vector,deps, label='Server '+str(i+1))
        plt.ylabel('No. of departures')
        plt.xlabel(r'$Load:\rho=\lambda/\mu$')
        plt.title('No. of departures vs load')
        plt.legend()
        plt.grid()
        plt.show()

        plt.figure()
        plt.plot(load_vector,overall_cost_list)
        plt.ylabel('Cost')
        plt.xlabel(r'$Load:\rho=\lambda/\mu$')
        plt.title('Overall cost')
        plt.grid()
        plt.show()
    
    if losses and iter_B:
        plt.figure()
        x=0
        for list in lost_p_matrix:
            plt.plot(load_vector,list , label='B='+str(capacity[x]))
            x=x+1
        plt.ylabel('Loss probability')
        plt.xlabel(r'$Load:\rho=\lambda/\mu$')
        plt.title('Loss probability')
        plt.legend()
        plt.grid()
        plt.show()   
        
        
        plt.figure()
        x=0
        for list in av_delay_matrix:
            plt.plot(load_vector,list , label='B='+str(capacity[x]))
            x=x+1
        plt.ylabel('Time [s]')
        plt.xlabel(r'$Load:\rho=\lambda/\mu$')
        plt.title('Average time in the queue E[T]')
        plt.legend()
        plt.grid()
        plt.show()  
    

plotingMetrics() # Plot metrics

# plt.figure()
# plt.plot(load_vector,ov1 , label='Least costly')
# plt.plot(load_vector,ov2 , label='Random')
# plt.plot(load_vector,ov3 , label='Round Robin')
# plt.xlim(0, 4) 
# plt.ylabel('Cost')
# plt.xlabel(r'$Load:\rho=\lambda/\mu$')
# plt.title('Overall cost') 
# plt.legend()
# plt.grid()
# plt.show() 

# plt.figure()
# plt.plot(load_vector,lossp2 , label='E[Ts]= 2s')
# plt.plot(load_vector,lossp10 , label='E[Ts]= 10s')
# plt.plot(load_vector,lossp20 , label='E[Ts]= 20s')
# plt.plot(load_vector,lossp80 , label='E[Ts]= 80s')
# plt.xlim(0, 4) 
# plt.ylabel('Loss probability')
# plt.xlabel(r'$Load:\rho=\lambda/\mu$')
# plt.title('Loss probability')
# plt.legend()
# plt.grid()
# plt.show()