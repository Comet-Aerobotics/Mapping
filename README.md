# Mapping
Sub-repository for mapping &amp; localization subteam.

mapping.sh: this is the main script that runs the mapping pipeline (setting up rtabmap (localization), foxglove (visualizing the 3D map produced by depth camera), and nav2 (framework for rover's navigation and path planning.)

nav_apriltag.py: this is a Python script that publishes a ROS2 Node. Its purpose is to scan an AprilTag, set it as the goal, and instruct the rover to navigate to it following Nav2's built in path finding algorithm. 

A more comprehensive documentation regarding the uses and purposes of mapping.sh and nav_apriltag.py will be published shortly...
