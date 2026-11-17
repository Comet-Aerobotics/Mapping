# Mapping
Sub-repository for mapping & localization subteam.

mapping.sh: this is the main script that runs the mapping pipeline (setting up rtabmap (localization), foxglove (visualizing the 3D map produced by depth camera), and nav2 (framework for rover's navigation and path planning.)

nav_apriltag.py: this is a Python script that publishes a ROS2 Node. Its purpose is to scan an AprilTag, set it as the goal, and instruct the rover to navigate to it following Nav2's built-in pathfinding algorithm. 

A more comprehensive documentation regarding the uses and purposes of mapping.sh and nav_apriltag.py will be published shortly...
-----------------------------------------------------------
## Terminology
**3D Point Cloud:**  A collection of 3D points with (x, y, z) coordinates.
**RTAB-Map (Real-Time Appearance-Based Mapping):**  A SLAM framework the rover uses to construct a 3D point cloud map of its environment based on sensor data (e.g., depth data from OAK-D camera). We use Foxglove to visualize this 3D map.
+ Thinks of this as how the rover "sees" its environment.

    <img width="373" height="296" alt="image" src="https://github.com/user-attachments/assets/eb614306-b7e5-48ba-9745-1b616eb319b4" />
    <sub>Example of a 3d point cloud map. </sub>


**Nav2:**  A ROS2 navigation framework that uses path-planning algorithms (e.g., Dijkstra, A*) to help the rover maneuver through obstacles and reach its destination.
+ This is particularly essential for AprilTag detection, where the tag is set as the goal.

**AprilTag:**  A visual marker for 3D pose & orientation estimation. When the depth camera (OAK-D) detects an AprilTag, it can estimate:
+ The camera's 3D position (X, Y, Z) with respect to the AprilTag's position.
+ The camera's 3D orientation (Roll, Pitch, Yaw), which indicates how the tag is rotated relative to the camera.

  <img width="161" height="155" alt="image" src="https://github.com/user-attachments/assets/e8295b59-0ef3-4fdf-a95c-baa9c0bf11c1" />

## Pipe Line (coming soon)
Run `./mapping.sh` to launch the following necessary processes for mapping and localization.
1. RTAB-Map: createa 3D map of the environment
2. apriltag_ros: detects AprilTags
3. nav_apriltag.py: senda destination goal (AprilTag) to Nav2
4. Nav2: plans a path and computes velocities.
   + Output movement commands to ROS 2 topic `/cmd_vel` (Command Velocity).
6. All data are published through ROS 2
7. Foxglove Bridge: transfers these data t0 Foxglove.
8. Foxglove: UI that displays maps, poses, topics, and logs.
   
## Progress So Far
As of now, we have accomplished the following:
+ Successfully feed depth data from OAK-D camera into RTAB-Map and generate a partial 3D point cloud map and view it in Foxglove.
+ Integrated `nav_apriltag.py` into `mapping.sh` that established AprilTag as the goal using Nav2.
+ Successfully detected the AprilTag and output log messages and the tag's ID to Foxglove's UI.
