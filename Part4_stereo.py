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
        self.CONFIG = config_()
        #pose_error_para
        self.init_time = time.time()
        self.previous_time = time.time()
        self.previous_position = np.array([0,0,0])
        self.pose_error = False
        self.cv_image_disparity = np.zeros((640,480,1), dtype=np.uint8)
        self.rsp_js = []
        self.step = 0
        self.SaveSyncedAll_start = time.time()
        self.bridge = CvBridge()
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
        # OWC 計算座標點
        self.cal_coordinate_only = self.OWC.cal_coordinate_only
        # OWC 連接Vaidio計算物件框
        #self.connect_vaidio = self.OWC.connect_vaidio
        # 同步三個訂閱訊息時間，符合條件時回呼callback
        # 測試過，q_size = 10 ，slop = 0.1為最穩定比對數
        ts = message_filters.ApproximateTimeSynchronizer([self.sub_left, self.sub_right, self.sub_pose], 10, 0.1,False)
        ts.registerCallback(self.callback_all)
    # 從stereo 計算disparity的函式
    # 輸入為左右眼相機照片，輸出為disparity
    def stereo_match(self,imgL, imgR):
        # disparity range is tuned for 'aloe' image pair
        window_size = 3
        min_disp = 16
        num_disp = 112 - min_disp
        stereo = cv2.StereoSGBM_create(minDisparity=min_disp,
                                       numDisparities=num_disp,
                                       blockSize=11,
                                       P1=8 * 3 * window_size ** 2,
                                       P2=32 * 3 * window_size ** 2,
                                       disp12MaxDiff=1,
                                       uniquenessRatio=10,
                                       speckleWindowSize=100,
                                       speckleRange=32
		                               )
        # print('computing disparity...')
        disp = stereo.compute(imgL, imgR).astype(np.float32) / 16.0
        return disp
    # child thread connect vaidio
    def connect_vaidio_job(self,cv_image_left):
        connect_vaidio_start = time.time()
        self.rsp_js, rsp_time = self.api.connect_vaidio_only(cv_image_left)
        connect_vaidio_end = time.time()
        # print("connect_vaidio_time:",connect_vaidio_end-connect_vaidio_start)
    def disparity_job(self,cv_image_left,cv_image_right):
        self.cv_image_disparity = self.stereo_match(cv_image_left,cv_image_right)
    def callback_all(self, data_left, data_right, data_pose):
        print("step: ",self.step)
        callback_start = time.time()
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
            
        # get depth image
        try:
            t2 = threading.Thread(target = self.connect_vaidio_job, args=[cv_image_left])
            t1 = threading.Thread(target = self.disparity_job, args=[cv_image_left,cv_image_right])
            # 執行該子執行緒
            t1.start()
            # 執行該子執行緒
            t2.start()
            t1.join()
            t2.join()
            dfs3D = self.dfsto3D(self.cv_image_disparity,self.UAV_type)
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
                self.previous_time = now
                self.previous_position = now_position
                if speed>5:
                    self.pose_error = True
            if self.pose_error == True:
                print("============pose_error===============")
        except CvBridgeError as e:
            print(e)
            return
        
        # get object coordinate and save image
        try:
            frame, disparity, dfs_frame, coordinate_time = self.cal_coordinate_only(self.rsp_js, cv_image_left, self.cv_image_disparity, dfs3D,pose_array, self.UAV_type, self.step)
            self.step += 1
            #print("calculate_coordinate: ",round(coordinate_time,6))
            direct = "./syc_result/"
            cv2.imwrite(direct+"frame{0}.jpg".format(self.step),frame)
        except CvBridgeError as e:
            print(e)
            return
        callback_end = time.time()
        #print("callback_end:",round(callback_end-callback_start,6))
class UAVObjectLocalization:
    def __init__(self):
        self.test = "part4"
        self.CONFIG = config_()
    def UAVision(self):
        rospy.init_node('my_node', anonymous=True)
        ip = SaveSyncedAll(self.CONFIG.UAV_type)
        rospy.spin()

