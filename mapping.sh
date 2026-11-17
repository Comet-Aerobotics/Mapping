#!/bin/bash

# 1. Launch RTAB-Map (Reverted to default so it tracks the camera)
gnome-terminal -- bash -c "ros2 launch depthai_ros_driver rtabmap.launch.py; exec bash"
gnome-terminal -- bash -c "sleep 10; ros2 service call /reset_odom std_srvs/srv/Empty {}; exec bash"

# 2. Static Transform (Flipped: oak is now the parent of base_link)
gnome-terminal -- bash -c "ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 oak base_link; exec bash"

# 3. Nav2 Bringup (Kept your corrected 12s and 20s delays)
gnome-terminal -- bash -c "sleep 12; ros2 launch nav2_bringup navigation_launch.py use_sim_time:=false; exec bash"
gnome-terminal -- bash -c "sleep 20; ros2 topic pub -1 /initialpose geometry_msgs/msg/PoseWithCovarianceStamped '{header: {frame_id: 'map'}, pose: {pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}'; exec bash"

# 4. AprilTag Node (Added the required tag family parameter)
gnome-terminal -- bash -c "ros2 run apriltag_ros apriltag_node --ros-args -r image_rect:=/oak/rgb/image_raw -r camera_info:=/oak/rgb/camera_info -p family:=\"36h11\"; exec bash"

# 5. Foxglove Bridge
gnome-terminal -- bash -c "ros2 launch foxglove_bridge foxglove_bridge_launch.xml; exec bash"

# 6. Apriltag Navigation Python Script (UPDATE THE PATH TO YOUR FILE)
gnome-terminal -- bash -c "sleep 10; while true; do python3 /home/caerobotics2/YOUR_WORKSPACE/src/YOUR_PACKAGE/navgoal_apriltag.py 6; echo 'Scan complete. Press Enter to scan for Tag 6 again, or Ctrl+C to quit.'; read; done"