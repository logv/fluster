# fluster

fluster is a floodfill-like clustering algorithm that uses density histograms
to cluster points. fluster is **iterative** in that it runs multiple passes
until no more cells can be joined.  fluster is **adaptive** in that it changes
the neighborhood window size and similarity threshold of cells after each
iteration.

# usage

    # cluster 114 points
    python cluster_demo.py 114

# example results

[imgur album](http://imgur.com/a/trDgo) of clustering results on variable
number of points. notice that fluster algorithm is on the way right and is
comparable to DBSCAN and Birch in results.

# algorithm

* split the space into NxN cells, where N is proportional to the log(len(points))
* count the number of points that fall into each cell, this is the **density map**
* let join\_distance = 2, overlap\_distance = 0.5, join\_delta = 0.5, overlap_delta = 0.05

* while there are no joins left:
  * go through each cell and examine its neighbors within join\_distance from cell:
    * let c1 = density of cell1, c2 = density of cell2 and cell\_similarity = abs(c1 - c2) / (c1 + c2)
    * join the two cells if cell\_similarity < overlap\_distance
  * join\_distance += join\_delta
  * overlap\_distance -= overlap\_delta

# variables

* number of grid cells (**N**) is between 25 and 53
* overlap threshold (**overlap\_distance**) starts between 0.5 and 0.7 and decreases with each iteration
* neighbor distance (**join\_distance**) is between 2 and 5 and increases with each iteration

# notes

* fluster is similar to DBSCAN but not as cool
* its unknown how tuned or fit the parameters are for general purpose use
* fluster's adaptive approach may over-fit or be over-aggressive
* fluster looks to work well from n = 50 to n = 1500 in cluster_demo
