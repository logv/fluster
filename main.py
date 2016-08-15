import matplotlib.pyplot as plt
import numpy as np
from sklearn import datasets

from fluster import Fluster

SHOW=True
def fluster(pts):
    f = Fluster()
    f.fit(pts)

    pt_colors = f.predict(pts)
    seperate = f.get_seperated()
    import copy
    counts = [100] * len(pt_colors)

    dims = len(pts[0])
    if SHOW:
      cm = plt.cm.get_cmap('brg')
      plt.hexbin(seperate[0], seperate[1], gridsize=f.buckets(), mincnt=1, alpha=0.3)
      colors = np.array([x for x in 'bgrcmykbgrcmykbgrcmykbgrcmyk'])
      colors = np.hstack([colors] * 20)
      sc = plt.scatter(seperate[0], seperate[1], c=colors[pt_colors].tolist(), s=counts, cmap=cm, marker="s")
      plt.axis(f.get_axes())
      plt.show()


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

if __name__ == "__main__":
  pts = []
  DIM=2



#  center_1   =   (random.randint(-500,   -100),   random.randint(-100,   100))
#  center_2   =   (random.randint(-1000,   -500),   random.randint(-100,   100))
#  center_3   =   (random.randint(-1000,   1000),   random.randint(-100,   100))
#  center_4   =   (random.randint(-500,   500),   random.randint(-200,    200))
#  add_gaussian(pts, center_1, num=100, mean=20)
#  add_gaussian(pts, center_2, num=100, mean=25)
#  add_gaussian(pts, center_3, num=100, mean=25)
#
#  add_uniform(pts, center_1, num=100, mean=10)
#  add_uniform(pts, center_1, num=100, mean=100)
#  add_uniform(pts, center_4, num=100, mean=100)
#
#  fluster(pts)

  # Generate datasets.  We choose the size big enough  to  see  the  scalability
  # of the algorithms,  but  not  too  big  to  avoid  too  long  running  times
  n_samples = 150
  import sys
  if len(sys.argv) > 1:
    n_samples = int(sys.argv[1])

  noisy_circles   =    datasets.make_circles(n_samples=n_samples,    factor=0.5,
                                        noise=.05)
  noisy_circles2   =    datasets.make_circles(n_samples=n_samples,    factor=0.7,
                                        noise=.05)
  noisy_moons = datasets.make_moons(n_samples=n_samples, noise=.05)
  blobs = datasets.make_blobs(n_samples=n_samples, random_state=8)
  no_structure = np.random.rand(n_samples, 2), None

  fluster(noisy_circles[0])
  fluster(noisy_circles2[0])
  fluster(noisy_moons[0])
  fluster(blobs[0])
  fluster(no_structure[0])
