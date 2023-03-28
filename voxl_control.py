#!/usr/bin/env python
import rospy
import mavros
import sys
import numpy as np
import math
from std_msgs.msg import Empty, UInt8, Bool, Float64
from mavros_msgs.msg import State, PositionTarget, Altitude
from mavros_msgs.srv import SetMode, CommandTOL, CommandBool
from geometry_msgs.msg import PoseStamped
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
from scipy.spatial.transform import Rotation as R 

import time

class DroneState:
    def __init__(self):
        self.pose_array = np.array([1, 2, 3, 4, 5, 6, 7],dtype='f')
        self.mode = ""
        self.yaw = 0.0

class Control():
    def __init__(self):
        self.cmd()

    def cmd(self):
        self.pub = rospy.Publisher('/mavros/setpoint_raw/local', PositionTarget, queue_size=10)  
        
    def linear(self,vx,vy,vz,oy):
        vel_msg = PositionTarget()
        vel_msg.coordinate_frame = 1
        vel_msg.type_mask = 1991
        vel_msg.velocity.x = vx
        vel_msg.velocity.y = vy
        vel_msg.velocity.z = vz
        vel_msg.yaw_rate = oy
        self.pub.publish(vel_msg)
        
    def target_pose(self,mask,px,py,pz,tyaw):#all:3064 pass_angular:4088
        pose_msg = PositionTarget()
        pose_msg.coordinate_frame = 1
        pose_msg.type_mask = mask
        pose_msg.position.x = px
        pose_msg.position.y = py
        pose_msg.position.z = pz
        pose_msg.yaw = tyaw
        self.pub.publish(pose_msg)
        
class Drone():
    def __init__(self):
        self.state=DroneState()
        self.cvbridge = CvBridge()
        self._sensor()
        self.l_img = np.zeros((640,480,1), dtype=np.uint8)
        self.r_img = np.zeros((640,480,1), dtype=np.uint8)
        self.sim_img = np.zeros((640,480,1), dtype=np.float32)

    def pos(self,data):
        self.state.pose_array[0] = data.pose.position.x
        self.state.pose_array[1] = data.pose.position.y
        self.state.pose_array[2] = data.pose.position.z
        self.state.pose_array[3] = data.pose.orientation.x
        self.state.pose_array[4] = data.pose.orientation.y
        self.state.pose_array[5] = data.pose.orientation.z
        self.state.pose_array[6] = data.pose.orientation.w
        Euler = R.from_quat([data.pose.orientation.x,data.pose.orientation.y,data.pose.orientation.z,data.pose.orientation.w]).as_euler('zyx')
        self.state.yaw = Euler[0]

    def state_cb(self,data):
        self.state.mode = data.mode
        
    def image_cb(self,data):
        self.l_img = self.cvbridge.imgmsg_to_cv2(data,"mono8")
    def r_image_cb(self,data):
        self.r_img = self.cvbridge.imgmsg_to_cv2(data,"mono8")
    def sim_image_cb(self,data):
        self.sim_img = self.cvbridge.imgmsg_to_cv2(data,"32FC1")
        self.sim_img = np.uint8(self.sim_img)
    
    def _sensor(self):#rostopic subscriber
        rospy.Subscriber('/qvio/pose', PoseStamped, self.pos, queue_size=1)
        rospy.Subscriber('/mavros/state', State, self.state_cb)
        rospy.Subscriber("/stereo/left", Image, self.image_cb, queue_size = 1, buff_size=2**24)
        rospy.Subscriber("/stereo/right", Image, self.r_image_cb, queue_size = 1, buff_size=2**24)
        rospy.Subscriber("/airsim_node/PX4/front_left_custom/DepthPlanar", Image, self.sim_image_cb, queue_size = 1, buff_size=2**24)
        
class Check_UAV:
    def __init__(self):
        self.drone = Drone()
        self.break_while = [False,False,False]
    def image_callback(self):
        pose_data = self.drone.state.pose_array
        Limg = self.drone.l_img
        Rimg = self.drone.r_img
        if len(pose_data)==7 and self.break_while[0]==False:
            print("Found UAV Pose")
            self.break_while[0]=True
        if Limg.shape==(480,640) and self.break_while[1]==False:
            print("Found Stereo Left")
            self.break_while[1]=True
        if Rimg.shape==(480,640) and self.break_while[2]==False:
            print("Found Stereo Right")
            self.break_while[2]=True
    def check(self):
        rospy.init_node('my_node')
        rospy.sleep(0.1)
        start = time.time()
        while True:
            self.image_callback()
            if self.break_while==[True,True,True]:
                break
            now = time.time()
            if now-start>3:
                break
        if self.break_while[0]==False:
            print("Didn't Find UAV Pose.")
        if self.break_while[1]==False:
            print("Didn't Find Stereo Left.")
        if self.break_while[2]==False:
            print("Didn't Find Stereo Right.")
        return self.break_while
        
        
