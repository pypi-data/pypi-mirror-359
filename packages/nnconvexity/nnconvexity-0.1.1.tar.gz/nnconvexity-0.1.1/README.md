# Convexity of representations
This package contains methods to compute convexity scores to measure convexity of latent representations of neural networks as defined in

Tětková, L., Brüsch, T., Dorszewski, T. et al. On convex decision regions in deep network representations. Nat Commun 16, 5419 (2025). https://doi.org/10.1038/s41467-025-60809-y

**Paper:** [https://www.nature.com/articles/s41467-025-60809-y](https://www.nature.com/articles/s41467-025-60809-y)

**Documentation:** [https://nnconvexity.readthedocs.io/en/latest/](https://nnconvexity.readthedocs.io/en/latest/)

**Source code:** [https://github.com/LenkaTetkova/nnconvexity](https://github.com/LenkaTetkova/nnconvexity)

See [code](https://github.com/LenkaTetkova/Convexity-of-representations.git) for the paper containing also a demo for using this package.

It provides functions for two types of convexity:
- Euclidean: sample points on a segment between two points of the same class and evaluate whether they are classified into the same class.
- graph: approximation of convexity on a manifold -- construct a graph based on nearest neighbors and evaluate proportion of the shortest paths that go through the same class.
