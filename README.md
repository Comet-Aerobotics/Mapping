# Mapping
Sub-repository for mapping & localization subteam.
We have been working on developing a pipeline that allows the rover to detect and navigate towards an AprilTag.

`mapping.sh`: startup script that runs the entire mapping pipeline (setting up rtabmap (localization), foxglove (visualizing the 3D map produced by depth camera), and nav2 (framework for rover's navigation and path planning). Think of it as the "ON" switch.

`nav_apriltag.py`: A Python ROS 2 node that processes AprilTag detections, calculates a navigation goal near the detected tag, and sends the goal to Nav2 for path planning and navigation. Note that it instructs the rover to stop at a small distance away from the AprilTag to avoid a traffic accident (crashing into the tag).

-----------------------------------------------------------
## Terminology
**3D Point Cloud:**  A collection of 3D points with (x, y, z) coordinates.

**2D Occupancy Map:**    A flat, top-down floor plan made of tiny squares that tells a rover where it can and cannot go.

**RTAB-Map (Real-Time Appearance-Based Mapping):**  A SLAM framework the rover uses to construct a 3D point cloud map of its environment based on sensor data (e.g., depth data from OAK-D camera). We use Foxglove to visualize this 3D map. 
+ Think of this as how the rover "sees" its environment.

    <img width="373" height="296" alt="image" src="https://github.com/user-attachments/assets/eb614306-b7e5-48ba-9745-1b616eb319b4" />

  <sub>Example of a 3d point cloud map. </sub>
+ RTAB-Map also outputs a 2D occupancy map that is used by Nav2 for path planning.
  

**Nav2:**  A ROS 2 navigation framework that uses path-planning algorithms (e.g., Dijkstra, A*, etc.) to help the rover maneuver through obstacles and reach its destination (goal).
+ Nav2 constructs a costmap based on the 2D occupancy map, which tells the rover how "expensive" or dangerous it is to drive over different spots in an area.
  
  <img width="384" height="175" alt="image" src="https://github.com/user-attachments/assets/475dc22a-a292-4cec-b114-9fd95a8eb6b2" />

+ This is particularly essential for AprilTag detection, where the tag is set as the goal.
  

**AprilTag:**  A visual marker for 3D pose & orientation estimation. When the depth camera (OAK-D) detects an AprilTag, it can estimate:
+ The camera's 3D position (X, Y, Z) with respect to the AprilTag's position.
+ The camera's 3D orientation (Roll, Pitch, Yaw), which indicates how the tag is rotated relative to the camera.

  <img width="161" height="155" alt="image" src="https://github.com/user-attachments/assets/e8295b59-0ef3-4fdf-a95c-baa9c0bf11c1" />

## Pipeline

Run `./mapping.sh` to launch the following necessary processes for mapping and localization.
1. RTAB-Map: creates a 3D map of the environment
2. apriltag_ros: detects AprilTags
3. nav_apriltag.py: sends a destination goal (AprilTag) to Nav2
4. Nav2: plans a path and computes velocities.
   + Output movement commands to ROS 2 topic `/cmd_vel` (Command Velocity).
5. Foxglove Bridge: transfers data to Foxglove.
6. Foxglove: UI that displays maps, poses, topics, and logs.
   
## Progress So Far
As of now, we have accomplished the following:
+ Successfully fed depth data from OAK-D camera into RTAB-Map and generated a partial 3D point cloud map and viewed it in Foxglove.
+ Integrated `nav_apriltag.py` into `mapping.sh` that established AprilTag as the goal using Nav2.
+ Successfully detected the AprilTag and output log messages and the tag's ID to Foxglove's UI.
However, we still need to test this script on the physical rover to ensure it navigates to the AprilTag properly.

What has not been implemented:
+ Navigation to other types of goals (e.g., construction zone, berm zone).



