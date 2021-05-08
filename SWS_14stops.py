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

Iset = np.arange(1,101)
Iset = tuple(Iset)

D={(i, j): 1 for i in R for j in O}
for r in [2,3,4,5,6]:
    if r>1:
        for j in O:
            if (j[0]>8-r and j[0]<7+r) or (j[1]>8-r and j[1]<7+r):
                D[r,j]=0
for r in [7,8,9,10,11]:
    for j in O:
        if (j[0]>=21-r or j[0]<=r-6) or (j[1]>=21-r or j[1]<=-6+r):
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

retrieve_data = pd.read_excel('Data_input/data_input_14stops.xlsx', sheet_name='sbt_fr', index_col=0)
df = pd.DataFrame(retrieve_data)
D_old = {(i, j): df.at[i, j] for i in df.index for j in df.columns}
for i in R:
    for j in O:
        Bsy = {(i, j): D_old[i, '{}'.format(str(j))] for i in Iset for j in O}

total_demand = sum(Bsy[i, sy] for i in Iset for sy in O)
print('total demand',total_demand)

#Initialize the Gurobi model
model = gp.Model()

LL_check = model.addVar(vtype=gp.GRB.CONTINUOUS, lb=0, name='LL_check')
LL_check2 = model.addVar(vtype=gp.GRB.CONTINUOUS, lb=0, name='LL_check2')

#Initialize variable x_r as non-negative integer
x = model.addVars(R,vtype=gp.GRB.INTEGER, lb=0, name='x')

#initialize variable z_{f,r}
z = model.addVars(F,R,vtype=gp.GRB.BINARY,name='z')

#initialize variable u_{f,sy}
u = model.addVars(F,O,vtype=gp.GRB.BINARY,name='u')

#Initialize variable h_{f1,f2,r,sy}
h = model.addVars(F,F,R,O,vtype=gp.GRB.BINARY,lb=0,name='h')

#Initialize variable b_{r,s}
b = model.addVars(Iset,R,S,vtype=gp.GRB.CONTINUOUS,lb=0,name='b')

#Initialize variable v_{r,s}
v = model.addVars(Iset,R,S,vtype=gp.GRB.CONTINUOUS,lb=0,name='v')

#Initialize variable l_{r,s}
l = model.addVars(Iset,R,S,vtype=gp.GRB.CONTINUOUS,lb=0,name='l')

#Initialize variable probability_{i,r,s}
probability = model.addVars(Iset,vtype=gp.GRB.BINARY,name='probability')
#Initialize variable g_{i,r,s}
g = model.addVars(Iset,R,S,vtype=gp.GRB.CONTINUOUS,lb=-10000000,name='g')
sigma = model.addVars(Iset,R,S,vtype=gp.GRB.CONTINUOUS,lb=-10000000,name='sigma')
y = model.addVars(Iset,R,S,vtype=gp.GRB.BINARY,name='y')
Overall_passenger_waiting_times = model.addVar(vtype=gp.GRB.CONTINUOUS,name='Overall_passenger_waiting_times')
Overall_vehicle_running_times = model.addVar(vtype=gp.GRB.CONTINUOUS,name='Overall_vehicle_running_times')
Unserved_passengers = model.addVar(vtype=gp.GRB.CONTINUOUS,name='Unserved_passengers')
Averange_passenger_waiting_time = model.addVar(vtype=gp.GRB.CONTINUOUS,name='Averange_passenger_waiting_time')
sum_probability = model.addVar(vtype=gp.GRB.CONTINUOUS,name='sum_probability')

import math

model.addConstrs(sum(z[i,r] for i in F) <= 1 for r in R)
model.addConstrs(sum(f[i]*z[i,r] for i in F) <= x[r]/Tr[r] for r in R)
model.addConstrs( sum(f[i]*u[i,sy[0],sy[1]] for i in F) <= sum(D[r,sy] * (sum(f[i]*z[i,r] for i in F)) for r in R) for sy in O)
model.addConstrs(sum(f[i]*u[i,sy[0],sy[1]] for i in F) >= Theta for sy in O)
model.addConstrs(sum(u[i,sy[0],sy[1]] for i in F) == 1 for sy in O)
model.addConstr(sum(x[r] for r in R) <= N)
model.addConstr(x[1] >= K)

model.addConstrs(b[ist,r,s] == sum(Bsy[ist,sy]*D[r,sy]* sum(sum( (i1/i2) * h[i1,i2,r,sy[0],sy[1]] for i2 in F if i2!=0) for i1 in F) for sy in O if sy[0]==s) for ist in Iset for r in R for s in S[0:-1]) #do not consider the last element of the tuple
model.addConstrs(v[ist,r,s] == sum(Bsy[ist,sy]*D[r,sy]* sum(sum( (i1/i2) * h[i1,i2,r,sy[0],sy[1]] for i2 in F if i2!=0) for i1 in F) for sy in O if sy[1]==s) for ist in Iset for r in R for s in S[1:]) #do not consider the last element of the tuple
model.addConstrs(2*h[i1,i2,r,sy[0],sy[1]] <= z[i1,r]+u[i2,sy[0],sy[1]] for i1 in F for i2 in F for r in R for sy in O)
model.addConstrs(sum(sum(h[i1,i2,r,sy[0],sy[1]] for i2 in F if i2!=0) for i1 in F)==1 for r in R for sy in O)
model.addConstrs(l[ist,r,s] == l[ist,r,s-1]+b[ist,r,s]-v[ist,r,s] for ist in Iset for r in R for s in S[1:]) #ignore the first stop
model.addConstrs(l[ist,r,1] == b[ist,r,1] for ist in Iset for r in R)
model.addConstrs(g[ist,r,s] + c*sum(f[i]*z[i,r] for i in F) == l[ist,r,s] for ist in Iset for r in R for s in S if s!=S[-1])

model.addConstrs(sigma[ist,r,s] >= 0 for ist in Iset for r in R for s in S if s!=S[-1])
model.addConstrs(sigma[ist,r,s] >= g[ist,r,s] for ist in Iset for r in R for s in S if s!=S[-1])
model.addConstrs(sigma[ist,r,s] <= M*y[ist,r,s] for ist in Iset for r in R for s in S if s!=S[-1])
model.addConstrs(sigma[ist,r,s] <= g[ist,r,s]+(1-y[ist,r,s])*M for ist in Iset for r in R for s in S if s!=S[-1])

model.addConstr(sum(sigma[ist,r,s] for ist in Iset for r in R for s in S if s!=S[-1]) <= 0.01*sum(Bsy[ist,sy] for ist in Iset for sy in O))

model.addConstr(Overall_vehicle_running_times == sum(Tr[r]*Tperiod* sum(f[i]*z[i,r] for i in F)  for r in R) )
model.addConstr(Averange_passenger_waiting_time == 60*(1/sum(sum(Bsy[ist,sy] for sy in O) for ist in Iset))*sum(sum(Bsy[ist,sy]* sum(u[i,sy[0],sy[1]]*(1/(f[i]+1)) for i in F) for sy in O) for ist in Iset))
model.addConstr(Unserved_passengers == sum(sigma[ist,r,s] for ist in Iset for r in R for s in S if s!=S[-1]))

#Declare objective function
obj = sum(x[r]*W1 + W2*Tr[r]*Tperiod* sum(f[i]*z[i,r] for i in F)  for r in R) + (1/len(Iset))*sum(sum(Bsy[ist,sy]* sum(u[i,sy[0],sy[1]]*(1/(f[i]+1)) for i in F) for sy in O) for ist in Iset)
model.setObjective(obj,GRB.MINIMIZE)
model.optimize()
model.Params.NodefileStart = 0.1
print('status',GRB.Status.OPTIMAL)
#model.printQuality()
for v in model.getVars():
    if v.x > 1e-5:
        print('%s %s %g' % (v.varName, '=', v.x))

model.write('model.mps')