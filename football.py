import pandas as pd 
from pulp import *

# read in data to dataframe
df = pd.read_csv('RMT.csv')

# create binary columns for positions and teams
df = pd.get_dummies(df, columns=['Pos'])
df = pd.get_dummies(df, columns=['Team'])

players = df['Player']

# initiate linear optimization model
model = LpProblem("Fantasy Football", LpMaximize)

# limit parameters to 0 or 1
x = pulp.LpVariable.dicts('player', players, 0, 1, LpInteger)

# create dictionaries (necessary for model)
value_dict = dict(zip(players, df['Total'])) 
cost_dict = dict(zip(players, df['Price']))

# maximise based on value (predicted performance)
model += sum([value_dict[i] * x[i] for i in players])

# constraint - limit cost to 102.9m
model += sum([cost_dict[i] * x[i] for i in players]) <= 102.9

#create dict for each position
pos_dict = {}
for col in df.columns.values[-24:-20]:
	pos_dict[col] = dict(zip(players, df[col])) 

pos_limits = [5, 3, 2, 5]

# set constraint on each position for GK (2), D(5), M(5), F(2)
for index, col in enumerate(df.columns.values[-24:-20]):
	current = pos_dict[col]
	model += sum([current[i] * x[i] for i in players]) == pos_limits[index]

#create dict for each team
team_dict = {}
for col in df.columns.values[-20:]:
	team_dict[col] = dict(zip(players, df[col])) 
	
# set constraint on each team for 3 players max
for col in df.columns.values[-20:]:
	current = team_dict[col]
	model += sum([current[i] * x[i] for i in players]) <= 3

# constraints - must spend 9m on keepers and over 20m on forwards
model += sum([pos_dict['Pos_GK'][i] * cost_dict[i] * x[i] for i in players]) == 9.0
model += sum([pos_dict['Pos_F'][i] * cost_dict[i] * x[i] for i in players]) >= 20.0

model.solve()

total_cost = []
total_value = []

# print chosen players by finding parameters which are 1 
for player in players:
	if x[player].value() == 1:
		print player
		total_cost.append(cost_dict[player])
		total_value.append(value_dict[player])

print sum(total_value)
print sum(total_cost)


