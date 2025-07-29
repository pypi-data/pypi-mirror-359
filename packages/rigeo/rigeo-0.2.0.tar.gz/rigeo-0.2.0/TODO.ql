= rigeo TODO =
* consider adding a `scale` parameter to the transform method
  - this would become a more general affine transform in this case
* better test coverage
  - capsule realizability
* multiBody API
  - support mesh shapes
  - test with different shapes (cylinders, in particular)
* consider adding `tol` for checking realizability
* tolerance reforms: support atol and rtol?
* improve and release docs
* random module
  - implement uniform sampling of psd matrices with constant trace
  - could also do uniform sampling of cylinder, capsule (though annoying)
* clean up ellipsoid implementation with better handling of zero half extents
  - use _z function
