#!/usr/bin/env python
# coding: utf-8

# In[16]:


get_ipython().system(' pip install pulp')


# In[17]:


import pandas as pd
from pulp import *
import matplotlib.pyplot as plt
from itertools import chain, repeat


# In[18]:


def ncycles(iterable, n):
    "Returns the sequence elements n times"
    return chain.from_iterable(repeat(tuple(iterable), n))


# In[19]:


n_staff = [31, 45, 40, 40, 48, 30, 25]
jours = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Staff
df_staff = pd.DataFrame({'Days': jours, 'Staff Demand':n_staff})
df_staff[['Days', 'Staff Demand']].plot.bar(x='Days', figsize = (30, 10), fill=True, color='black')
plt.title('Workforce Ressources Demand by Day')
plt.xlabel('Day of the week')
plt.ylabel('Number of Workers')
plt.show()


# In[20]:


# Create circular list of days
n_days = [i for i in range(7)]
n_days_c = list(ncycles(n_days, 3)) 

# Working days
list_in = [[n_days_c[j] for j in range(i , i + 5)] for i in n_days_c]

# Days off
list_excl = [[n_days_c[j] for j in range(i + 1, i + 3)] for i in n_days_c]


# In[21]:


# The class has been initialize, and x, and days defined
model = LpProblem("Minimize Staffing", LpMinimize)

# Create Variables
start_jours = ['Shift: ' + i for i in jours]
x = LpVariable.dicts('shift_', n_days, lowBound=0, cat='Integer')

# Define Objective
model += lpSum([x[i] for i in n_days])

# Add constraints
for d, l_excl, staff in zip(n_days, list_excl, n_staff):
    model += lpSum([x[i] for i in n_days if i not in l_excl]) >= staff

# Solve Model
model.solve()

# The status of the solution is printed to the screen
print("Status:", LpStatus[model.status])


# In[22]:


# How many workers per day ?
dct_work = {}
dico_work = {}
for v in model.variables():
    dct_work[int(v.name[-1])] = int(v.varValue)
    dico_work[v.name] = int(v.varValue)
dico_work


# In[23]:


# Show workers schedule
dict_sch = {}
for day in dct_work.keys():
    dict_sch[day] = [dct_work[day] if i in list_in[day] else 0 for i in n_days]
df_sch = pd.DataFrame(dict_sch).T
df_sch.columns = jours
df_sch.index = start_jours
# The optimized objective function value is printed to the screen
print("Total number of Staff = ", pulp.value(model.objective))


# In[24]:


# Detailed
df_sch


# In[25]:


# Sum by day
df_sch.sum(axis =0)


# In[26]:


df_supp = df_staff.copy().set_index('Days')
df_supp['Staff Supply'] = df_sch.sum(axis = 0)
df_supp['Extra_Ressources'] = df_supp['Staff Supply'] - df_supp['Staff Demand']
df_supp.to_csv('test.csv')


# In[27]:


# Staff
ax = df_supp.plot.bar(y=['Staff Demand', 'Staff Supply'], figsize = (30, 10), fill=True, color=['black', 'red'])
df_supp.plot(y=['Extra_Ressources'], color=['blue'], secondary_y = True, ax = ax, linewidth = 3)
plt.title('Workforce: Demand vs. Supply')
plt.xlabel('Day of the week')
plt.ylabel('Number of Workers')
plt.show()


# In[ ]:




