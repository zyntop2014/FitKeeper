import numpy as np
from sklearn.cluster import KMeans
import json
from geopy.distance import vincenty

# An encoder used to encode numpy integers
# so that integers are serializable
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)

# db = [(),(),...]
def kmeans(db):
    """
    Input:
        db: A list of tuples, each tuple corresponds 
            to one user.
            This should be the output of function "read_db_to_ml()"
    Return:
        group: 
            Used to lookup the cluster that each user is in.
            Dictionary format.
            key: Each user's uid
            value: cluster's index
        get_group_member: 
            Used to find components of each cluster.
            Dictionary format.
            key: Cluster index, STRING TYPE
            value: A list containing all members of this cluster
    """
    group = {}
    get_group_member = {}

    data_list = []
    id = []
    for data in db:
        id.append(data[0])
        data_list.append(data[1:])

    df = np.array(data_list)
    k = 10

    for i in range(0, k):
        get_group_member[i] = []
    clf = KMeans(n_clusters=k).fit(df)
    labels = clf.labels_
    for i in range(0, len(labels)):
        group[id[i]] = labels[i]
        get_group_member[labels[i]].append(id[i])
    
    # Encode "numpy" integers to serializable ones
    group = json.loads(json.dumps(group, cls=MyEncoder))
    get_group_member = json.loads(json.dumps(get_group_member, cls=MyEncoder))
    
    return group, get_group_member


def filtering(id, data):
    """
    Perform different filtering methods.
    First find the user's data in 'data',
    subtract it as reference,
    then sort the rest.
    Input:
        id: user's id. 
        data: A list of tuples. The cluster
              of data that this user is in. 
    Return:
        Filter result.
    """
    data_to_filter = []
    
    for d in data:
        if id == d[0]:
            ud = d   # ud: user's data
        else:
            data_to_filter.append(d)

    filter_by_age = sorted(data_to_filter, key=lambda x:abs(x[1]-ud[1]))
    filter_by_rating = sorted(data_to_filter, key=lambda x:x[2], reverse=True)
    filter_by_freq = sorted(data_to_filter, key=lambda x:x[3], reverse=True)
    filter_by_dist = sorted(data_to_filter, key=lambda x:vincenty(x[4],ud[4]).miles)

    res = {}
    # res['filter_by_age'] = filter_by_age
    # res['filter_by_rating'] = filter_by_rating
    # res['filter_by_freq'] = filter_by_freq
    # res['filter_by_dist'] = filter_by_dist
    # Extract IDs
    res['filter_by_age'] = map(lambda x:x[0], filter_by_age)
    res['filter_by_rating'] = map(lambda x:x[0], filter_by_rating)
    res['filter_by_freq'] = map(lambda x:x[0], filter_by_freq)
    res['filter_by_dist'] = map(lambda x:x[0], filter_by_dist)

    return res