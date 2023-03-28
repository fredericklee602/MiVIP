# Part 2 UAV找April Tag，並求相機姿態
import cv2
import rospy
from cv_bridge import CvBridge, CvBridgeError
import numpy as np 
import voxl_control
import math
import glob


# cvbridge = CvBridge()
drone = voxl_control.Drone()
FRAME_COUNT = 0
qvio_saver = []
img_size = (640,480)
break_while = False
def image_callback():
    global FRAME_COUNT
    global break_while
    # img = drone.l_img
    # img = cv2.resize(img, img_size, interpolation=cv2.INTER_CUBIC)
    # cv2.imshow("drone",img)
    pose_data = drone.state.pose_array
    # Limg = drone.r_img
    # if Limg.shape==(480,640):
    #     print(Limg.shape)
    #     break_while = True
    # Rimg = drone.r_img
    if len(pose_data)==7:
        print("Found UAV Pose")
        break_while = True
    # if Limg

if __name__ == '__main__':
    rospy.init_node('my_node')
    rospy.sleep(0.1)
    while True:
        image_callback()
        if break_while==True:
            break
        if cv2.waitKey(1) & 0xFF == 27: # 按ESC键退出
            break
