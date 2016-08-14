# let's just do quick flustering
import math
import random
import sys

from collections import defaultdict
import itertools

class Fluster(object):
  def __init__(self, *args, **kwargs):
    self.__buckets = 0

  # snaps pt into its histogram buckets in each dimension
  def get_dim_bucket(self, pt, buckets):
    extrema = self.__extrema
    ranges = self.__ranges

    pt_bucket = []
    for k, val in enumerate(pt):
      k_idx = (float(val) - extrema[k][0]) / ranges[k]
      k_idx *= buckets

      pt_bucket.append(int(k_idx))

    return tuple(pt_bucket)

  def get_seperated(self):
    return self.__seperated

  def get_axes(self):
    axes = []
    dims = self.__dims
    for k in xrange(dims):
      axes += self.__extrema[k]

    print axes
    return axes

  # amortized leader labelings
  # for union joins
  def get_cluster_leader(self, clusters, tup):
    prev_tup = tup
    path = []
    while tup in clusters:
      if tup == clusters[tup]:
        break

      tup = clusters[tup]
      path.append(tup)

    leader = tup
    for tup in path:
      clusters[tup] = leader

    return leader


  # finds the min,max in each dimension of pts
  def calculate_extrema(self, pts):
    extrema = []
    for k in pts[0]:
      extrema.append([sys.maxint, -sys.maxint])

    for pt in pts:
      for i, dim in enumerate(pt):
        extrema[i][0] = min(extrema[i][0], pt[i])
        extrema[i][1] = max(extrema[i][1], pt[i])

    self.__extrema = extrema
    return extrema

  # creates a n-dim histogram of counts of pixel frequencies
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


    self.__populated = density_map.keys()
    return seperate, density_map

  # joins nearby cells in the density map
  def join_clusters(self, min_overlap, min_distance):
    dims = self.__dims
    clusters = self.__clusters
    cluster_sizes = self.__cluster_sizes
    density_map = self.__density_map
    populated = self.__populated
    density_map.keys()

    neighbors = []
    kernel_size = int(min_distance)

    dist=kernel_size
    for k in xrange(dims):
      neighbor = [0]
      for d in xrange(dist):
        neighbor += [- d, +d]

      neighbors.append(neighbor)

      NEIGHBORS = list(itertools.product(*neighbors))

    joined = 0

    tuple_template = [0] * dims
    for i, tuple_1 in enumerate(populated):
      for offset_tuple in NEIGHBORS:
        if sum(offset_tuple) == 0:
          continue

        distance = 0
        for k in xrange(dims):
          tuple_template[k] = tuple_1[k] + offset_tuple[k]
          distance += offset_tuple[k]**2
        distance = math.sqrt(distance)

        tuple_2 = tuple(tuple_template)

        if not tuple_1 in density_map:
          continue

        if not tuple_2 in density_map:
          continue

        d1 = density_map[tuple_1]
        d2 = density_map[tuple_2]

        if distance > min_distance:
          continue

        if d1 == 0 or d2 == 0 or d1 + d2 < 2:
          continue

        density_distance = abs(d1 - d2) /  (float(d1  +  d2)+1)
        if density_distance > min_overlap:
          continue

        if not tuple_1 in clusters:
          clusters[tuple_1] = tuple_1

        if not tuple_2 in clusters:
          clusters[tuple_2] = tuple_2

        c1 = self.get_cluster_leader(clusters, tuple_1)
        c2 = self.get_cluster_leader(clusters, tuple_2)

        if c1 == c2:
          continue


        if not c1 in cluster_sizes:
          cluster_sizes[c1] = 1
        if not c2 in cluster_sizes:
          cluster_sizes[c2] = 1

        s1 = cluster_sizes[c1]
        s2 = cluster_sizes[c2]

        cluster_sizes[c1] += s2
        cluster_sizes[c2] += s1

        density_map[tuple_1] = (d1 + d2) / 2.0
        density_map[tuple_2] = (d1 + d2) / 2.0

        clusters[c1] = c2
        joined += 1

    return joined

  def label_clusters(self):
    clusters = self.__clusters

    colors = {}
    cluster_id = 0
    for c in set(clusters.values()):
      leader = self.get_cluster_leader(clusters, c)
      if not leader in colors:
        colors[leader] = cluster_id
        cluster_id += 1

    return colors

  def fit(self, pts):
    if self.__buckets == 0:
      # estimate the number of buckets based on our extrema and points
      # our travel distance should be related to number of buckets and squares
      # we have
      self.__buckets = min(max(int(math.log(len(pts), 2)*5), 25), 56)

    print "BUCKETS", self.__buckets, "FOR", len(pts), "POINTS"
    # every pt is a K tuple of size dims
    dims = len(pts[0])
    if dims > 3:
        raise Exception("Too many dimensions")

    self.__dims = dims

    extrema = self.calculate_extrema(pts)
    self.__extrema = extrema
    ranges = [0] * dims
    print "EXTREMA", extrema
    for k, vals in enumerate(extrema):
      ranges[k] = extrema[k][1] - extrema[k][0]

    self.__ranges = ranges
    self.__clusters = {}
    self.__cluster_sizes = {}
    self.build_density_map(pts)


    import time
    total_ms = 0
    distance = 6.28 - math.log(len(pts)) / 3.14
    distance -= 2
    distance = max(distance, 2)
    missed = 0

    # get aggressive with overlaps
    overlap = min(max((distance - 3.14) / 3.14, 0.5), 0.75)
    overlap_delta = (1 / 2.0) / 10.0
    distance_delta = 1.0 / 2.0
    for i in xrange(15):
      print "DISTANCE", distance, "KERNEL SIZE", int(distance), "OVERLAP", overlap

      start = time.time()
      joined = self.join_clusters(overlap, distance)
      overlap -= overlap_delta
      distance += distance_delta
      end = time.time()
      time_taken = ((end - start) * 1000)
      total_ms += time_taken
      print   "  JOINED CLUSTERS",   joined,   "TOOK",   "%ims"   %   time_taken
      loglen = math.log(len(pts))
      if joined <= 2 * loglen:
        missed += 1
      elif joined >= 5 * loglen and missed > 0:
        missed -= 1

      if missed >= 2:
        break


    print "TOTAL TIME", "%ims" % (total_ms)

  def predict(self, pts):
    clusters = self.__clusters
    cluster_sizes = self.__cluster_sizes
    colors = self.label_clusters()
    extrema = self.__extrema
    MIN_REGION=int(math.log(len(pts)))

    pt_colors = []
    for pt in pts:
      pt_bucket = self.get_dim_bucket(pt, self.__buckets)
      if pt_bucket in clusters:
        cluster = self.get_cluster_leader(clusters, pt_bucket)
        if cluster  in  colors and cluster_sizes[cluster] >= MIN_REGION:
          pt_colors.append(colors[cluster])
        else:
          pt_colors.append(-1)
      else:
        pt_colors.append(-1)

    return pt_colors
