import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import random
from os import listdir
from networkx.algorithms import bipartite

##############################
###  Combine 2-week files  ###
##############################
data_dir = "/your/directory/here/"

files = listdir(data_dir)

dfs = []
for f in files:
    df = pd.read_csv(data_dir + f)
    dfs.append(df)
    
combined = pd.concat(dfs)
combined.to_csv(data_dir + 'video-data.csv')

######################
###  Get datasets  ###
######################
combined = pd.read_csv(data_dir+'video-data.csv')

sessions, session_counts = np.unique(combined['session_id'].values, return_counts = True)
students, student_counts = np.unique(combined['useraccount_id'].values, return_counts = True)
videos, video_counts = np.unique(combined['video_id'].values, return_counts = True)

print('There are {} unique sessions, {} students, and {} videos'.format(len(sessions),len(students),len(videos)))

pd.Series(session_counts).describe()
pd.Series(student_counts).describe()
pd.Series(video_counts).describe()

#########################
###  Build a network  ###
#########################

# One group is student IDs
# The other group is video IDs
G = nx.Graph()
G.add_nodes_from(students, bipartite=0)
G.add_nodes_from(videos, bipartite=1)
G.add_edges_from(list(zip(combined['useraccount_id'].values, combined['video_id'].values)))

cluster_all = bipartite.average_clustering(G)
density_all = bipartite.density(G)

# Get degrees for unprojected graph
student_degree = G.degree(students)
list_student_degree = [val for (node, val) in student_degree]
plt.hist(list_student_degree)
plt.xlabel('Number of Unique Videos')
plt.ylabel('Number of Students')
plt.show()
pd.Series(list_student_degree).describe()

video_degree = G.degree(videos)
list_video_degree = [val for (node, val) in video_degree]
plt.hist(list_video_degree)
plt.xlabel('Number of Unique Accessing Students')
plt.ylabel('Number of Videos')
plt.show()
pd.Series(list_video_degree).describe()

# Attempt at student projection
sample_rate = 0.3
n_sampled = int(sample_rate * len(students))
sampled_students = random.sample(list(students), n_sampled)
student_projection = bipartite.projected_graph(G,sampled_students) # MEMORY ERROR HERE

# Video projection
video_projection = bipartite.projected_graph(G,videos)
video_proj_degree = video_projection.degree()
list_video_proj_degree = [val for (node, val) in video_proj_degree]
plt.hist(list_video_proj_degree)
plt.xlabel('Number of Neighbors')
plt.ylabel('Number of Videos')
plt.show()

pd.Series(list_video_proj_degree).describe()
nx.density(video_projection)

# Degree centrality
deg = nx.degree_centrality(video_projection)
deg_list = list(deg.values())
pd.Series(deg_list).describe()
plt.hist(deg_list)
plt.xlabel('Degree Centrality')
plt.ylabel('Number of videos')
plt.show()

# Eigenvector centrality
eig = nx.eigenvector_centrality(video_projection)
eig_list = list(eig.values())
pd.Series(eig_list).describe()
plt.hist(eig_list)
plt.xlabel('Eigenvector Centrality')
plt.ylabel('Number of videos')
plt.show()

# Closeness centrality
close = nx.closeness_centrality(video_projection)
close_list = list(close.values())
pd.Series(close_list).describe()
plt.hist(close_list)
plt.xlabel('Closeness Centrality')
plt.ylabel('Number of videos')
plt.show()

# Betweenness centrality
between = nx.betweenness_centrality(video_projection)
between_list = list(between.values())
pd.Series(between_list).describe()
plt.hist(between_list)
plt.xlabel('Betweenness Centrality')
plt.ylabel('Number of videos')
plt.show()

# Triangles and clustering coefficient
tri = nx.triangles(video_projection)
tri_list = list(tri.values())
print("There are {} triangles".format(np.sum(tri_list)/3))
cluster = nx.clustering(video_projection)
cluster_list = list(cluster.values())
pd.Series(cluster_list).describe()
plt.hist(cluster_list,bins=15)
plt.xlabel('Clustering Coefficient')
plt.ylabel('Number of videos')
plt.show()

# Diameter
print("The diameter is {}".format(nx.diameter(video_projection)))
print("Because minimum degree is {}".format(min(deg_list)))

###########################
###  Changes over time  ###
###########################
combined['ts_created'] = pd.to_datetime(combined['ts_created'])
combined.index = combined['ts_created']
combined['month'] = combined.index.month
combined_sorted = combined.sort_values(by=['month'])



video_by_month = combined.groupby(['video_id',combined.index.month]).count()
student_by_month = combined.groupby(['useraccount_id',combined.index.month]).count().drop(columns=['ts_created'])
student_by_month = student_by_month.reset_index(level='ts_created')

# Month of first view per video
video_first = combined_sorted.drop_duplicates(subset='video_id')['month']
plt.hist(video_first.values)
plt.xlabel('Month of first view')
plt.ylabel('Number of Videos')
plt.show()

# Average month view per video
video_avg_month = combined.groupby(['video_id']).mean()['month']
plt.hist(video_avg_month.values,bins=25)
plt.xlabel('Average Month')
plt.ylabel('Number of Videos')
plt.show()

# Count of video views per month
plt.hist(combined.index.month.values)
plt.xlabel('Month')
plt.ylabel('Number of video views')
plt.show()

month_counts = combined['video_id'].groupby(combined.index.month).count()
pd.Series(month_counts).describe()

# Average number of student views per month
avgs = []
for i in range(1,7):
    filtered = student_by_month.loc[student_by_month['ts_created'] == i]
    avgs.append(np.mean(filtered['session_id'].values))
plt.plot(range(1,7),avgs)
plt.ylim((0,8))
plt.xlabel('Month')
plt.ylabel('Average video views per student')
plt.show()
