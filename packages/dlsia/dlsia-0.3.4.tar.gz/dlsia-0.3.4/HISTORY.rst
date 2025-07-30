=======
History
=======

dlsia: Deep Learning for Scientific Image Analysis

0.2.0 (2023-01-26)
------------------
* First release - a rename of a previous project to better reflect name and scope.


0.3.0 (2023-01-26)
------------------
* Bug fixes and minor updates

0.3.1 (2023-01-26) 
------------------
* New way to train networks
* Bug fixes
* Updated doc issues

0.3.2 (2025-04-17)
------------------
* Bug fixes
* Updated doc issues
* Added Cerberus

0.3.4 (2025-01-27)
------------------
* Added instance segmentation utilities with merging and fixed-size region extraction
* Added merge_close_instances() for iterative merging of close objects
* Added get_object_bounding_boxes() generator for flexible region extraction
* Added extract_object_region_fixed_size() for fixed-size patches with multi-channel support
* Added extract_all_objects_fixed_size() for batch extraction
* Support for both 2D and 3D (multi-channel) images
* Removed debug print statements from watershed function
