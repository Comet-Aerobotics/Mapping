
#!/usr/bin/env python3

import sys
import math
import rclpy

# ROS2 Python imports
from rclpy.node import Node
from rclpy.time import Time
from rclpy.action import ActionClient

from apriltag_msgs.msg import AprilTagDetectionArray
from nav2_msgs.action import NavigateToPose
from action_msgs.msg import GoalStatus
from tf2_ros import Buffer, TransformListener, TransformException

"""
map:	    A reference coordinate system for the environment
base_link:	A reference coordinate system attached to the rover's body
oak:	    A coordinate system attached to OAK-D camera
tag36h11:6:	A coordinate system attached to AprilTag 6

"""

# Create a ROS2 node that navigates to a specific AprilTag when detected.
class TagNavigator(Node):
    def __init__(self, target_id):
        super().__init__('tag_navigator')

        # Initialize the target AprilTag ID and related parameters
        self.target_id = target_id
        self.tag_frame = f'tag36h11:{target_id}'        # TF frame name for the AprilTag
        self.stop_distance = 0.8                        # meters away from the tag
        self.busy = False                               # Flag to indicate if the node is currently navigating
        self.finished = False                           # Flag to indicate if the navigation is complete

        # Set up the TF2 buffer and listener to get transforms
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(
            self.tf_buffer, self    
        )

        # Create an action client for navigation
        self.nav_client = ActionClient(                 # create a ROS2 action client
            self, NavigateToPose, '/navigate_to_pose'   # action name
        )

        # Subscribe to AprilTag detections
        self.subscription = self.create_subscription(   # create a ROS2 subscriber
            AprilTagDetectionArray,                     # message type we want to receive 
            '/detections',                              # topic name
            self.detection_callback,                    # function to call when msg is received
            10                                          # depth of the msg queue
        )

        # Apriltag scanning message
        self.get_logger().info(
            f'Scanning for AprilTag {target_id}...'
        )

    # Callback function for AprilTag detections (callback function gets executed automatically when an event occurs)
    def detection_callback(self, msg):
        if self.busy or self.finished:
            return

        ids = [d.id for d in msg.detections]            # Get a list of detected AprilTag IDs from msg

        if self.target_id not in ids:
            return

        self.get_logger().info(                         # AprilTag found
            f'Found AprilTag {self.target_id}!'
        )

        self.navigate()                                 # Call nav funct. to move rover to AprilTag

    # Navigate to the AprilTag using the Nav2 action server
    #                                                    ------------  
    #                     -----------                    | AprilTag |
    #                     |         |                    -----------
    #                     |  Rover  |
    #                     |         |
    #                     -----------

    def navigate(self):
        try:
            # Position of AprilTag relative to 
            # map frame (global coordinate frame)
            tag_tf = self.tf_buffer.lookup_transform(       # Time() requests the latest transform from the TF2 buffer
                'map', self.tag_frame, Time()               # map--target coordinate frame, 
            )                                               # tag_frame--source coordinate frame

            # Position of rover relative to map frame
            robot_tf = self.tf_buffer.lookup_transform(
                'map', 'base_link', Time()
            )

        # Print warning if TF2 fails to retrieve transform and position info
        except TransformException as exc:
            self.get_logger().warn(
                f'Waiting for TF: {exc}'
            )
            return

        # Prevent navigation towards old AprilTag positions
        tag_stamp = Time.from_msg(tag_tf.header.stamp)      # convert ROS timestamp into Python ROS2 Time obj and store in tag_stamp
        age = (
            self.get_clock().now() - tag_stamp              # compute age of AprilTag detection 
        ).nanoseconds / 1e9

        if age < 0 or age > 1.0:                            # age is neg indicatesrecordings from the future
            self.get_logger().warn('Tag transform is stale')# age > 1.0 sec indicates that the transform is too old
            return

        """
        
        𝓒𝓪𝓵𝓬𝓾𝓵𝓪𝓽𝓮 𝓭𝓲𝓼𝓽𝓪𝓷𝓬𝓮 𝓫𝓮𝓽𝔀𝓮𝓮𝓷 𝓻𝓸𝓿𝓮𝓻 𝓪𝓷𝓭 𝓐𝓹𝓻𝓲𝓵𝓣𝓪𝓰 𝓾𝓼𝓲𝓷𝓰 𝓽𝓱𝓮𝓲𝓻 𝓻𝓮𝓵𝓪𝓽𝓲𝓿𝓮 𝓹𝓸𝓼 𝓽𝓸 𝓽𝓱𝓮 𝓶𝓪𝓹 𝓯𝓻𝓪𝓶𝓮
    
        """
        tx = tag_tf.transform.translation.x                 # AprilTag x_pos relative to map frame
        ty = tag_tf.transform.translation.y                 # AprilTag y_pos relative to map frame

        rx = robot_tf.transform.translation.x               # rover x_pos relative to map frame
        ry = robot_tf.transform.translation.y               # rover y_pos relative to map frame

        
        dx = tx - rx                                        # distance between rover and AprilTag in x direction
        dy = ty - ry                                        # distance between rover and AprilTag in y direction

        # Compute Euclidean distance between rover and AprilTag
        distance = math.hypot(dx, dy)

        # Stops the rover if it is already within the stopping distance
        if distance <= self.stop_distance:
            self.get_logger().info(
                'Already within stopping distance'
            )
            self.finished = True
            return

        # Approach the AprilTag but stop at a specified distance away from it
        gx = tx - self.stop_distance * dx / distance        # x_pos of goal relative to map frame
        gy = ty - self.stop_distance * dy / distance        # y_pos of goal relative ot map frame
        
        # Compute the angle of the displacement vector from the rover and AprilTag 
        # with respoect to the positive x-axis
        yaw = math.atan2(dy, dx) 

        """
        pose: PoseStamped Object containing:
        + header: coordinate frame and timestamp
        + pose: position and orientation
        """
        # Create a navigation goal object
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = 'map'

        # retrieve the current time and convert it to a ROS2 timestamp message
        goal.pose.header.stamp = (
            self.get_clock().now().to_msg()
        )

        # Set the goal position and orientation based on the computed values
        goal.pose.pose.position.x = gx
        goal.pose.pose.position.y = gy
        goal.pose.pose.orientation.z = math.sin(yaw / 2)
        goal.pose.pose.orientation.w = math.cos(yaw / 2)

        # Print warning if Nav2 is not ready to receive goals
        if not self.nav_client.server_is_ready():
            self.get_logger().warn('Nav2 is not ready')
            return

        # Set the busy flag to True to indicate that the node is currently navigating
        self.busy = True 

        # Log the goal pos
        self.get_logger().info(
            f'Goal: x={gx:.2f}, y={gy:.2f}'
        )

        # Send goal to Nav2
        future = self.nav_client.send_goal_async(goal) 
        # When this Future finishes, automatically execute my goal_response() function.
        future.add_done_callback(self.goal_response) 


    def goal_response(self, future):
        try:
            handle = future.result()
        except Exception as exc:
            self.get_logger().error(str(exc))
            self.busy = False
            self.finished = True
            return

        # Nav2 rejected goal
        if not handle.accepted:
            self.get_logger().error('Nav2 rejected goal')
            self.busy = False
            self.finished = True
            return

        self.get_logger().info('Nav2 accepted goal')

        """

        'future': object representing the result of an asynchronous operation that may finish later
    
        """
        future = handle.get_result_async()
        future.add_done_callback(self.goal_result)

    def goal_result(self, future):
        try:
            status = future.result().status

            # Successfully reached the goal
            if status == GoalStatus.STATUS_SUCCEEDED:
                self.get_logger().info('Tag reached!')
            else:
                self.get_logger().warn(
                    f'Navigation ended with status {status}'
                )

        except Exception as exc:
            self.get_logger().error(str(exc))

        self.finished = True


def main():
    # Check if the correct number of command-line arguments is provided
    if len(sys.argv) != 2:
        print('Usage: python3 navgoal_apriltag.py TAG_ID')
        return

    # Validate that the provided TAG_ID is an integer
    try:
        tag_id = int(sys.argv[1])
    except ValueError:
        print('TAG_ID must be an integer')
        return

    # Initialize the ROS2 Python client library
    rclpy.init()
    node = TagNavigator(tag_id)

    try:
        while rclpy.ok() and not node.finished:
            # Processes at most one ready callback and wait no longer than 0.1s if nothing is ready
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        # Clean up and shut down the ROS2 node
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
