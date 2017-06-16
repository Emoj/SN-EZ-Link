import pandas as pd
import networkx as nx
from networkx.algorithms import bipartite

# searching on list of tuples
# [i for i, v in enumerate(locationList) if v[0] == 1 and v[1] == 1]


def to_seconds(line):
    hh, mm, ss = [int(x) for x in line.split(':')]
    return hh*3600 + mm*60 + ss


print("reading file...") # 2015-12-25, ezLarge
df = pd.read_csv("D:/KMUTT/_IHPC_Internship/Data/EZLink/ezLarge.csv")
df = df[df.travelMode == "Bus"]
df = df[['cardID','busRegNum','busTripNum','startTime','endTime']]
df['busTripNum'] = df['busTripNum'].map(int)
df['startTime'] = df['startTime'].map(to_seconds)
df['endTime'] = df['endTime'].map(to_seconds)

print("creating agent list")
agentList = list(df.cardID.unique())

print("creating location list")
locationList = list(set(zip(df.busRegNum, df.busTripNum)))

agentList.sort()
locationList.sort()
df.sort_values(['cardID', 'startTime'], ascending=[True, True], inplace=True)


#==============================================================================
# Try bipartite
#==============================================================================
B = nx.MultiGraph()
B.add_nodes_from(agentList, bipartite=0)
B.add_nodes_from(locationList, bipartite=1)

for t in df.itertuples():
    agent, location, time = t[1], (t[2], t[3]), (t[4], t[5])
    B.add_edge(agent, location, t=time)

agentSet = set(n for n,d in B.nodes(data=True) if d['bipartite']==0)
locationSet = set(B) - agentSet

closenessCentrality = bipartite.closeness_centrality(B, locationSet)
degreeCentrality = bipartite.degree_centrality(B, locationSet)
betweennessCentrality = bipartite.betweenness_centrality(B, locationSet)
#==============================================================================


#==============================================================================
# Agent Social Network
#==============================================================================
G = nx.Graph()
G.add_nodes_from(agentList)

othersActivities = df

i = 0
for x in agentList:
    myActivities = othersActivities[othersActivities.cardID == x]
    othersActivities = othersActivities[othersActivities.cardID != x]

#    for activity in myActivities.itertuples():
    i = i + 1
    print(str(i) + " ")
    print(len(othersActivities))

#==============================================================================
