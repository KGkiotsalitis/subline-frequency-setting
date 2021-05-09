# ===============================
# AUTHOR: Dr Konstantinos Gkiotsalitis
# CONTACT DETAILS: k.gkiotsalitis@utwente.nl
# CREATE DATE: 7 May 2021
# PURPOSE: Model the subline frequency setting problem
# SPECIAL NOTES: -
# ===============================
# Change History: v1
# ==================================

# import solver
import gurobipy as gp
from gurobipy import GRB
import pandas as pd
import numpy as np

model = gp.Model()

#Set the values of sets.
R = (1,2,3,4,5,6,7,8,9,10,11) #list of lines
S = (1,2,3,4,5,6,7,8,9,10,11,12,13,14) #list of stops

#OD-pairs with passenger demand
O=[]
for j in range(1,7):
    for i in range(1,8):
        if j<i:
            O.append((j,i))
for j in range(8,14):
    for i in range(8,15):
        if j<i:
            O.append((j,i))
O=tuple(O)
D={(i, j): 1 for i in R for j in O}
for r in [2,3,4,5,6]:
    if r>1:
        for j in O:
            if (j[0]>8-r and j[0]<7+r) or (j[1]>8-r and j[1]<7+r):
                #print(j)
                D[r,j]=0
for r in [7,8,9,10,11]:
    for j in O:
        if (j[0]>=21-r or j[0]<=r-6) or (j[1]>=21-r or j[1]<=-6+r):
            #print(j)
            D[r,j]=0
F_r = (0,1,2,3,4,5,6,8,10,12,15,20,30,60) #permitted frequencies
W1=3
W2=1.5
Tr={1:0.3, 2:0.237, 3:0.189, 4:0.142, 5:0.11, 6:0.063, 7:0.237, 8:0.189, 9:0.1577, 10:0.11, 11:0.063} #round-trip travel time of every trip in r\in R expressed in hours;
Theta=2 #maximum allowed waiting time to ensure a minimum level of service for any passenger;
K=2 #minimum number of minibusses that should be assigned to the original line;
N=36 #number of available minibuses;
M=100000000
F=0,1,2,3,4,5,6,8,10,12,15,20,30,60 #set of frequencies;
f={0:0,1:1,2:2,3:3,4:4,5:5,6:6,8:8,10:10,12:12,15:15,20:20,30:30,60:60}
F_min=1.0 #minimum required frequency of a sub-line to be allowed to be operational in the time period T;
Tperiod=6 #time period of the planning phase;
c=8 #minibus capacity;
data=np.loadtxt('Data_input/demand_14stops_leftskewed.txt') #You can read another input file by changing this command
Bsy={j:0 for j in O}
count=0
for j in O:
    Bsy[j]=data[count]
    count=count+1


#Initialize variable x_r as non-negative integer
x = model.addVar(vtype=gp.GRB.INTEGER, lb=0, name='x')

#initialize variable z_{f,r}
z = model.addVars(F,vtype=gp.GRB.BINARY,name='z')

#initialize variable u_{f,sy}
u = model.addVars(F,O,vtype=gp.GRB.BINARY,name='u')

#Initialize variable h_{f1,f2,r,sy}
h = model.addVars(F,F,O,vtype=gp.GRB.BINARY,lb=0,name='h')

#Initialize variable b_{r,s}
b = model.addVars(S,vtype=gp.GRB.CONTINUOUS,lb=0,name='b')

#Initialize variable v_{r,s}
v = model.addVars(S,vtype=gp.GRB.CONTINUOUS,lb=0,name='v')

#Initialize variable l_{r,s}
l = model.addVars(S,vtype=gp.GRB.CONTINUOUS,lb=0,name='l')

Overall_passenger_waiting_times = model.addVar(vtype=gp.GRB.CONTINUOUS,name='Overall_passenger_waiting_times')
Overall_vehicle_running_times = model.addVar(vtype=gp.GRB.CONTINUOUS,name='Overall_vehicle_running_times')

import math

model.addConstr(sum(z[i] for i in F) <= 1)
model.addConstr(sum(f[i]*z[i] for i in F) <= x/Tr[1] )
#model.addConstrs( sum(f[i]*u[i,sy[0],sy[1]] for i in F) <= sum(D[r,sy] * (sum(f[i]*z[i,r] for i in F)) for r in R) for sy in O)
model.addConstrs( sum(f[i]*u[i,sy[0],sy[1]] for i in F) <= D[1,sy] * (sum(f[i]*z[i] for i in F)) for sy in O)
model.addConstrs(sum(f[i]*u[i,sy[0],sy[1]] for i in F) >= Theta for sy in O)
model.addConstrs(sum(u[i,sy[0],sy[1]] for i in F) == 1 for sy in O)
model.addConstr(x <= N)
model.addConstr(x >= K)
model.addConstrs(b[s] == sum(Bsy[sy]*D[1,sy]* sum(sum( (i1/i2) * h[i1,i2,sy[0],sy[1]] for i2 in F if i2!=0) for i1 in F) for sy in O if sy[0]==s) for s in S[0:-1]) #do not consider the last element of the tuple
model.addConstrs(v[s] == sum(Bsy[sy]*D[1,sy]* sum(sum( (i1/i2) * h[i1,i2,sy[0],sy[1]] for i2 in F if i2!=0) for i1 in F) for sy in O if sy[1]==s) for s in S[1:]) #do not consider the last element of the tuple
model.addConstrs(2*h[i1,i2,sy[0],sy[1]] <= z[i1]+u[i2,sy[0],sy[1]] for i1 in F for i2 in F for sy in O)
model.addConstrs(sum(sum(h[i1,i2,sy[0],sy[1]] for i2 in F if i2!=0) for i1 in F)==1 for sy in O)
model.addConstrs(l[s] == l[s-1]+b[s]-v[s] for s in S[1:])
model.addConstr(l[1] == b[1])
model.addConstrs(l[s] <= c*sum(f[i]*z[i] for i in F) for s in S)

model.addConstr(Overall_passenger_waiting_times == 60*(1/sum(Bsy[sy] for sy in O))*sum(Bsy[sy]* sum(u[i,sy[0],sy[1]]*(1/(f[i]+1)) for i in F) for sy in O))
model.addConstr(Overall_vehicle_running_times == Tr[1]*Tperiod* sum(f[i]*z[i] for i in F))

#Declare objective function
obj = x*W1 + W2*Tr[1]*Tperiod* sum(f[i]*z[i] for i in F) + sum(Bsy[sy]* sum(u[i,sy[0],sy[1]]*(1/(f[i]+1)) for i in F) for sy in O)
model.setObjective(obj,GRB.MINIMIZE)

model.optimize()
print('status',GRB.Status.OPTIMAL)
model.printQuality()
for v in model.getVars():
    if v.x > 0:
        print('%s %s %g' % (v.varName, '=', v.x))