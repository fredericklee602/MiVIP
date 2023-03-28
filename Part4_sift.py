#! /usr/bin/env python
import cv2
import rospy
from cv_bridge import CvBridge, CvBridgeError
import numpy as np 
from sensor_msgs.msg import Image
import message_filters
from geometry_msgs.msg import PoseStamped
import UAVisionObjectLocalization_
import time
import threading
from read_config import config_
from Vaidio_API import API


class SaveSyncedAll:

    def __init__(self,UAV_type):
        self.step = 0
        #pose_error_para
        self.init_time = time.time()
        self.previous_time = time.time()
        self.previous_position = np.array([0,0,0])
        self.pose_error = False
        self.rsp_js = []
        self.queryKeypoints = []
        self.trainKeypoints = []
        self.matches = []
        
        # bridge to convert date
        self.bridge = CvBridge()
        
        # subscribe data from rostopic
        self.sub_left = message_filters.Subscriber("/stereo/left",Image, queue_size = 1, buff_size=2**24)
        self.sub_right = message_filters.Subscriber("/stereo/right",Image, queue_size = 1, buff_size=2**24)
        self.sub_pose = message_filters.Subscriber("/qvio/pose", PoseStamped, queue_size = 1, buff_size=2**24)
        
        # UAV type
        self.UAV_type = UAV_type
        # 計算物件座標點類別OWC
        self.OWC = UAVisionObjectLocalization_.Object_World_Coordinate()
        # OWC 轉換disparity成3D座標點 
        self.dfsto3D = self.OWC.dfsto3D
        # 連接Vaidio
        self.api = API()
        # self.api.connect_vaidio_only = API.connect_vaidio_only
        # OWC SIFT_Match
        self.SIFT_Match = self.OWC.SIFT_Match
        # OWC 計算物件座標
        self.calc_coordinate = self.OWC.calc_coordinate

        # 同步三個訂閱訊息時間，符合條件時回呼callback
        # 測試過，q_size = 10 ，slop = 0.1為最穩定比對數
        ts = message_filters.ApproximateTimeSynchronizer([self.sub_left, self.sub_right, self.sub_pose], 10, 0.1,False)
        ts.registerCallback(self.callback_all)
    # child thread connect vaidio
    def connect_vaidio_job(self,cv_image_left):
        self.rsp_js, rsp_time = self.api.connect_vaidio_only(cv_image_left)
    def SIFT_match_job(self,left_frame, right_frame):
        self.queryKeypoints, self.trainKeypoints, self.matches = self.SIFT_Match(left_frame, right_frame)
    def callback_all(self, data_left, data_right, data_pose):
        print("step:",self.step)
        # get left image
        try:
            cv_image_left = self.bridge.imgmsg_to_cv2(data_left, "mono8")
        except CvBridgeError as e:
            print(e)
            return

        # get right image
        try:
            cv_image_right = self.bridge.imgmsg_to_cv2(data_right, "mono8")
        except CvBridgeError as e:
            print(e)
            return
            
        # get pose
        # get pose error
        try:
            now = time.time()
            pose_array = self.OWC.POS(data_pose)
            if now-self.init_time>3:
                now_position = pose_array[:3]
                distance = ((now_position[0]-self.previous_position[0])**2 + (now_position[1]-self.previous_position[1])**2 + (now_position[2]-self.previous_position[2])**2)**(1/2)
                speed = (distance)/(now-self.previous_time)
                print("Speed: {0} m/s".format(speed))
                self.previous_time = now
                self.previous_position = now_position
                if speed>5:
                    self.pose_error = True
            if self.pose_error == True:
                print("============pose_error===============")

        except CvBridgeError as e:
            print(e)
            return
        
        # get depth image
        try:
            t2 = threading.Thread(target = self.connect_vaidio_job, args=[cv_image_left])
            t1 = threading.Thread(target = self.SIFT_match_job, args=[cv_image_left, cv_image_right])
            # 執行該子執行緒
            t1.start()
            # 執行該子執行緒
            t2.start()
            t1.join()
            t2.join()
            frame, coordinate_time = self.calc_coordinate(cv_image_left,pose_array, self.UAV_type, self.rsp_js, self.queryKeypoints, self.trainKeypoints, self.matches, self.step)
            self.step += 1
            # print("coordinate_time:",coordinate_time)
            direct = "./syc_result/"
            cv2.imwrite(direct+"frame.jpg",frame)
        except CvBridgeError as e:
            print(e)
            return
class UAVObjectLocalization:
    def __init__(self):
        self.test = "part4"
        self.CONFIG = config_()
    def UAVision(self):
        rospy.init_node('my_node', anonymous=True)
        ip = SaveSyncedAll(self.CONFIG.UAV_type)
        rospy.spin()