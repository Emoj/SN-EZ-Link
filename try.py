import pandas as pd
import networkx as nx
#from networkx.algorithms import bipartite
import matplotlib.pyplot as plt

# searching on list of tuples
# [i for i, v in enumerate(locationList) if v[0] == 1 and v[1] == 1]


def to_seconds(line):
    hh, mm, ss = [int(x) for x in line.split(':')]
    return hh*3600 + mm*60 + ss


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
# Try bipartite
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


#==============================================================================
# Agent Social Network
#==============================================================================
G = nx.Graph(name="Agent Social Network")
#G.add_nodes_from(agentList)

othersActivities = df

#i = 0
for myAgent in agentList:
#    if i == 100:
#        break
    myActivities = othersActivities[othersActivities['cardID'] == myAgent]
    othersActivities = othersActivities[othersActivities['cardID'] != myAgent]
    
    G.add_node(myAgent)
    for activity in myActivities.itertuples():
        nearbyAgent = othersActivities[
            (othersActivities['busRegNum'] == activity[2]) \
            & (othersActivities['busTripNum'] == activity[3]) \
            & ((activity[4] <= othersActivities['endTime']) & (othersActivities['startTime'] <= activity[5])) \
        ]
        
        for agent in nearbyAgent.itertuples():
            overlap = min(activity[5], agent[5]) - max(activity[4], agent[4])
            G.add_node(agent[1])
            G.add_edge(activity[1],agent[1], weight = overlap)
#    i = i + 1
   
#==============================================================================

#==============================================================================
# Draw a graph
#==============================================================================

elarge=[(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] >300]
esmall=[(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] <=300]

pos=nx.spring_layout(G) # positions for all nodes

# nodes
nx.draw_networkx_nodes(G,pos,node_size=1)

# edges
nx.draw_networkx_edges(G,pos,edgelist=elarge,width=1)
nx.draw_networkx_edges(G,pos,edgelist=esmall,width=1,alpha=0.5,edge_color='b')

# labels
# nx.draw_networkx_labels(G,pos,font_size=5,font_family='sans-serif')

plt.axis('off')
plt.savefig("weighted_graph.png") # save as png
plt.show() # display
#==============================================================================

degree_all = G.degree()
degree_centrality = nx.degree_centrality(G)

degree_count = 0
zero_count = 0
for key, value in degree_centrality.items():
    if value == 0:
        zero_count = zero_count + 1
    degree_count = degree_count + value
    
max_centrality = max(degree_centrality, key=lambda key: degree_centrality[key])
        