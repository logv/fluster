# let's just do quick flustering
import math
import random
import sys

from collections import defaultdict
import itertools
import matplotlib.pyplot as plt
import numpy as np


# {{{ HELPERS
def calculate_extrema(pts):

  extrema = []
  for k in pts[0]:
    extrema.append([sys.maxint, -sys.maxint])
    
  for pt in pts:
    for i, dim in enumerate(pt):
      extrema[i][0] = min(extrema[i][0], pt[i])
      extrema[i][1] = max(extrema[i][1], pt[i])
  
  return extrema
# }}} HELPERS  

class Fluster(object):
  def __init__(self, *args, **kwargs):
    self.__buckets = kwargs.get("buckets", 0)

  def get_dim_bucket(self, pt, buckets):
    extrema = self.__extrema
    ranges = self.__ranges

    pt_bucket = []
    for k, val in enumerate(pt):
      k_idx = (float(val) - extrema[k][0]) / ranges[k]
      k_idx *= buckets

      pt_bucket.append(int(k_idx))

    return tuple(pt_bucket)

  def join_cluster(self, min_overlap, min_distance, kernel_size=3):
    dims = self.__dims
    clusters = self.__clusters
    density_map = self.__density_map
    populated = density_map.keys()

    neighbors = []
    dist=kernel_size
    for k in xrange(dims):
      neighbor = [0]
      for d in xrange(dist):
        neighbor += [- d, +d]

      neighbors.append(neighbor)

      NEIGHBORS = list(itertools.product(*neighbors))

    joined = 0
    for i, tuple_1 in enumerate(populated):
      for offset_tuple in NEIGHBORS:    
        tuple_2 = [0] * dims
        for k in xrange(dims):
          tuple_2[k] = tuple_1[k] + offset_tuple[k]
        tuple_2 = tuple(tuple_2)

        if tuple_1 == tuple_2:
          continue

        d1 = density_map[tuple_1]
        d2 = density_map[tuple_2]

        if d1 == 0 or d2 == 0:
          continue

        density_distance = abs(d1 - d2)  /  float(d1  +  d2)
        if density_distance > min_overlap:
          continue


        distance = 0
        for k in xrange(dims):
          distance += (tuple_1[k] - tuple_2[k])**2
        distance = math.sqrt(distance)

        if distance > min_distance:
          continue

        if not tuple_1 in clusters:
          clusters[tuple_1] = set()

        if not tuple_2 in clusters:
          clusters[tuple_2] = set()

        clusters[tuple_1].add(tuple_1)
        clusters[tuple_1].add(tuple_2)

        c1 = clusters[tuple_1]
        c2 = clusters[tuple_2]
        if c1 == c2:
          continue

        joined += 1
        for c in clusters[tuple_2]:
          clusters[c] = clusters[tuple_1]
          clusters[tuple_1].add(c)

    return joined

  def label_clusters(self):
    clusters = self.__clusters

    colors = {}
    for c in clusters:
      if type(c) == set:
        fc = frozenset(c)
        for ic in clusters[c]:
          clusters[ic] = fc

    only_clusters = clusters.values() 
    r = lambda: random.randint(64, 255)
    cluster_id = 0
    for cluster in only_clusters:
      if not id(cluster) in colors:
        colors[id(cluster)] = cluster_id
        cluster_id += 1

    return colors

  def build_density_map(self, pts):
    buckets = self.__buckets

    extrema = self.__extrema
    ranges = self.__ranges

    dims = len(pts[0])
    density_map = defaultdict(int)
    self.__density_map = density_map

    seperate = []
    self.__seperated = seperate
    for k in xrange(dims):
      seperate.append([])

    for pt in pts:
      pt_bucket = []
      for k, val in enumerate(pt):
        k_idx = (float(val) - extrema[k][0]) / ranges[k]
        k_idx *= buckets

        pt_bucket.append(int(k_idx))
        seperate[k].append(val)

      density_map[tuple(pt_bucket)] += 1

    return seperate, density_map

  def fit(self, pts, buckets=45):
    if self.__buckets == 0:
      # estimate the number of buckets based on our extrema and points
      self.__buckets = max(int(math.sqrt(len(pts))), 20)

    print "OUR BUCKETS", self.__buckets, len(pts)
    # every pt is a K tuple of size dims
    dims = len(pts[0])
    self.__dims = dims

    extrema = calculate_extrema(pts)
    self.__extrema = extrema
    ranges = [0] * dims
    print "EXTREMA", extrema
    for k, vals in enumerate(extrema):
      ranges[k] = extrema[k][1] - extrema[k][0]

    self.__ranges = ranges
    seperate, density_map = self.build_density_map(pts)
    self.__clusters = {}


    import time
    total_ms = 0
    overlap = 0.5
    distance = 2
    kernel_size = 3
    for i in xrange(15):
      start = time.time()
      joined = self.join_cluster(overlap, distance, kernel_size)
      end = time.time()
      time_taken = ((end - start) * 1000)
      distance += 0.2
      overlap -= 0.05
      total_ms += time_taken
      print   "JOINED   CLUSTERS",   joined,   "TOOK",   "%ims"   %   time_taken
      if joined <= 5:
        break


    print "TOTAL TIME", "%ims" % (total_ms)

  def axes(self):
    axes = []
    dims = self.__dims
    for k in xrange(dims):
      axes += self.__extrema[k]

    print axes
    return axes

  def predict(self, pts):

    clusters = self.__clusters
    colors = self.label_clusters()
    MIN_REGION=10
    pt_colors = []
    extrema = self.__extrema
    for pt in pts:
      pt_bucket = self.get_dim_bucket(pt, self.__buckets)
      if pt_bucket in clusters:
        cluster = clusters[pt_bucket]
        if  id(cluster)  in  colors  and  len(cluster)   >   MIN_REGION   *   2:
          pt_colors.append(colors[id(cluster)])
        else:
          pt_colors.append(-1)
      else:
        pt_colors.append(-1)

    return pt_colors

   
  def get_seperated(self):
    return self.__seperated

def fluster(pts):
    f = Fluster(buckets=23)
    f.fit(pts)

    pt_colors = f.predict(pts)
    seperate = f.get_seperated()
    import copy
    counts = [100] * len(pt_colors)

    dims = len(pts[0])
    if True:
      sc = plt.scatter(seperate[0], seperate[1], c=pt_colors, s=counts, marker="s")
      plt.axis(f.axes())
      plt.show()


if __name__ == "__main__":
  pts = []
  DIM=2
  def add_gaussian(pts, center, num, mean):
    for i in xrange(num):
      pt = [0] * DIM
      for k in xrange(DIM):
        pt[k] = random.gauss(center[k], mean)
      pts.append(pt)

  def add_uniform(pts, center, num, mean):
    for i in xrange(num):
      pt = [0] * DIM
      for k in xrange(DIM):
        pt[k] = center[k] + random.randint(- mean, mean)
      pts.append(pt)



#
#   center_1   =   (random.randint(-500,   -100),   random.randint(-100,   100))
#  center_2   =   (random.randint(-1000,   -500),   random.randint(-100,   100))
#  center_3   =   (random.randint(-1000,   1000),   random.randint(-100,   100))
#   center_4   =   (random.randint(-500,   500),   random.randint(-200,    200))
#  add_gaussian(pts, center_1, num=100, mean=20)
#  add_gaussian(pts, center_2, num=100, mean=25)
#  add_gaussian(pts, center_3, num=100, mean=25)
#
#  add_uniform(pts, center_1, num=100, mean=10)
#  add_uniform(pts, center_1, num=100, mean=100)
#  add_uniform(pts, center_4, num=100, mean=100)
#
#  fluster(pts)

  from sklearn import datasets
  # Generate datasets.  We choose the size big enough  to  see  the  scalability
  # of the algorithms,  but  not  too  big  to  avoid  too  long  running  times
  n_samples = 1500
  noisy_circles   =    datasets.make_circles(n_samples=n_samples,    factor=0.5,
                                        noise=.05)
  noisy_moons = datasets.make_moons(n_samples=n_samples, noise=.05)
  blobs = datasets.make_blobs(n_samples=n_samples, random_state=8)
  no_structure = np.random.rand(n_samples, 2), None

  fluster(noisy_circles[0])
  fluster(noisy_moons[0])
  fluster(blobs[0])
  fluster(no_structure[0])
