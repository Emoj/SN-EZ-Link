import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
#from networkx.algorithms import bipartite

# searching on list of tuples
# [i for i, v in enumerate(locationList) if v[0] == 1 and v[1] == 1]

# loop thru graph         
#[ (u,v,edata['weight']) for u,v,edata in G.edges(data=True) if 'weight' in edata ]


#==============================================================================
# Convert time string to integer as number of seconds
#==============================================================================
def to_seconds(line):
    hh, mm, ss = [int(x) for x in line.split(':')]
    return hh*3600 + mm*60 + ss


#==============================================================================
# Reading input file and manipulate dataset
#==============================================================================
print("reading file...") # 2015-12-25, ezLarge
df = pd.read_csv("C:/_IHPC_Internship/Data/EZLink/ezLarge.csv")
df = df[(df['travelMode'] == "Bus") & (df['endDate'] != '0000-00-00')]
df = df[['cardID','busRegNum','busTripNum','startTime','endTime']]
df['busTripNum'] = df['busTripNum'].map(int)
df['startTime'] = df['startTime'].map(to_seconds)
df['endTime'] = df['endTime'].map(to_seconds)

print("creating agent list")
agentList = list(df.cardID.unique())

#print("creating location list")
#locationList = list(set(zip(df.busRegNum, df.busTripNum)))

agentList.sort()
#locationList.sort()
df.sort_values(['cardID', 'startTime'], ascending=[True, True], inplace=True)


#==============================================================================
# Try bipartite ; need agent list and location list
#==============================================================================
# B = nx.MultiGraph()
# B.add_nodes_from(agentList, bipartite=0)
# B.add_nodes_from(locationList, bipartite=1)

# for t in df.itertuples():
#     agent, location, time = t[1], (t[2], t[3]), (t[4], t[5])
#     B.add_edge(agent, location, t=time)

# agentSet = set(n for n,d in B.nodes(data=True) if d['bipartite']==0)
# locationSet = set(B) - agentSet

# closenessCentrality = bipartite.closeness_centrality(B, locationSet)
# degreeCentrality = bipartite.degree_centrality(B, locationSet)
# betweennessCentrality = bipartite.betweenness_centrality(B, locationSet)


#==============================================================================
# Agent Social Network
#==============================================================================
G = nx.MultiDiGraph(name="Agent Social Network")
G.add_nodes_from(agentList)

othersActivities = df

i = 0
for myAgent in agentList:
#    if i == 20:
#        break
    myActivities = othersActivities[othersActivities['cardID'] == myAgent]
    othersActivities = othersActivities[othersActivities['cardID'] != myAgent]
    
    for activity in myActivities.itertuples():
        nearbyAgent = othersActivities[
            (othersActivities['busRegNum'] == activity[2]) \
            & (othersActivities['busTripNum'] == activity[3]) \
            & ((activity[4] <= othersActivities['endTime']) & (othersActivities['startTime'] <= activity[5])) \
        ]
        for agent in nearbyAgent.itertuples():
            overlap = min(activity[5], agent[5]) - max(activity[4], agent[4])
            G.add_edge(activity[1],agent[1], weight = overlap)
    i = i + 1
#    print("Agent#" + str(i) + " out of " + str(len(agentList)))


#==============================================================================
# Graph Visualization
#==============================================================================
elarge=[(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] >300]
esmall=[(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] <=300]

pos = nx.spring_layout(G) # positions for all nodes

# nodes
nx.draw_networkx_nodes(G,pos,node_size=5)

# edges
nx.draw_networkx_edges(G,pos,edgelist=elarge,width=1)
nx.draw_networkx_edges(G,pos,edgelist=esmall,width=1,alpha=0.5,edge_color='b')

plt.axis('off')
plt.savefig("weighted_graph.svg") # save as png
plt.show() # display


#==============================================================================
# Some analytics
#==============================================================================
degree_all = G.degree()
degree_centrality = nx.degree_centrality(G)

degree_count = 0
zero_count = 0

for key, value in degree_all.items():
    if value == 0:
        zero_count = zero_count + 1

print("node with zero degree: " + str(zero_count))
    
max_centrality = max(degree_centrality, key=lambda key: degree_centrality[key])

for key, value in degree_centrality.items():
    if value == degree_centrality[max_centrality]:
        print(key + ": " + str(value))
        

#==============================================================================
# Check for no neighbor  #ezLarge:82
#==============================================================================
i = 0
for myAgent in agentList:
    myActivities = df[df['cardID'] == myAgent]
    othersActivities = df[df['cardID'] != myAgent]
    
    for activity in myActivities.itertuples():
        nearbyAgent = othersActivities[
            (othersActivities['busRegNum'] == activity[2]) \
            & (othersActivities['busTripNum'] == activity[3]) \
            & ((activity[4] <= othersActivities['endTime']) & (othersActivities['startTime'] <= activity[5])) \
        ]
        if nearbyAgent.empty:
            i = i + 1