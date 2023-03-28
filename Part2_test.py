# Part 2 UAV找April Tag，並求相機姿態
import cv2
import rospy
import numpy as np 
import voxl_control
import math
import apriltag
# Rotation 轉換旋轉矩陣、歐拉角、四元數
from scipy.spatial.transform import Rotation as R
# inv輸出反矩陣
from numpy.linalg import inv
from read_config import config_
from DB_SQL import DB_connect


class CamPoseLocalization:
    def __init__(self):
        # 連線DB
        self.DBCONN = DB_connect()
        # config檔
        self.CONFIG = config_()
        
        # self.drone = voxl_control.Drone()

        # apriltag分析tag碼tag36h11
        self.at_detector = apriltag.Detector(apriltag.DetectorOptions(families=self.CONFIG.apriltag_family))

        #  Apriltag世界座標
        objectPoints = np.array([[-1, 1, 0],
                                [1, 1, 0], 
                                [1, -1, 0], 
                                [-1, -1, 0]],
                                dtype=np.float32)
        self.objectPoints = objectPoints*float(self.CONFIG.apriltag_pic_length)


        self.FRAME_COUNT = 0
    def Global_Coordinate_deck(self,obj_points,UAV_para,fix_cam_img_points,UAV_img_points,CAM_NUMBER,Camera_intrinsic):
        
        # UAV給定UAV座標及姿態
        UAV_pos = UAV_para[:3]
        UAV_orient = UAV_para[3:]
        Rmatrix_UAV = R.from_quat(UAV_orient)
        
        # UAV拍攝棋盤格影像點
        _, rvec, tvec = cv2.solvePnP(obj_points, UAV_img_points, self.CONFIG.UAV_Camera_intrinsic["mtx"], self.CONFIG.UAV_Camera_intrinsic["dist"])
        
        # UAV 相機坐標系 R T
        rvec_UAV = rvec
        tvec_UAV = tvec
        rvec_matrix_UAV = cv2.Rodrigues(rvec_UAV)[0]
        
        # UAV1 相機坐標系轉NED，並旋轉回UAV0相同基底坐標系
        m = np.dot(rvec_matrix_UAV,np.transpose(obj_points)) + np.transpose(tvec_UAV.repeat(4)).reshape(3,4)
        NED_chess_point = np.dot(Rmatrix_UAV.as_matrix(),np.dot(np.array([[0,0,1],[1,0,0],[0,1,0]]),m))
        x = UAV_pos[0]
        y = UAV_pos[1]
        z = UAV_pos[2]
        bias_UAV = np.array([[x*100],[y*100],[z*100]])
        #print("bias_UAV:",bias_UAV)
        # bias_UAV 機體中心座標移到左眼相機座標
        bias_UAV = bias_UAV + np.dot(Rmatrix_UAV.as_matrix(),np.array(self.CONFIG.broad_left_eye_coordinate))
        # ned_Chess為棋盤格所有點初始UAV坐標系座標點
        ned_Chess = bias_UAV.repeat(4).reshape(3,4) + NED_chess_point
        print("ned_Chess:",ned_Chess)
        
        # NED轉回相機坐標系再導入solvepnp得到固定相機姿態轉換
        ned_Chess_EDN = np.array([[0,0,1],[1,0,0],[0,1,0]])
        # 先用單一攝相頭
        _, rvec, tvec = cv2.solvePnP(np.transpose(np.dot(inv(ned_Chess_EDN),ned_Chess)), fix_cam_img_points, Camera_intrinsic["mtx"], Camera_intrinsic["dist"])
        #print('tvec',tvec)
        tvec_dist = math.sqrt(tvec[0]**2+tvec[1]**2+tvec[2]**2)
        rvec_matrix_CAM = cv2.Rodrigues(rvec)[0]
        
        # 固定相機相機坐標系再轉回UAV0 NED 坐標系
        NED_tvec = np.dot(np.array([[0,0,1],[1,0,0],[0,1,0]]),np.dot(inv(rvec_matrix_CAM),-tvec))
        NED_tvec_dist = math.sqrt(NED_tvec[0]**2+NED_tvec[1]**2+NED_tvec[2]**2)
        
        # 回推固定相機旋轉角度
        cam_img_rot = R.from_matrix(rvec_matrix_CAM).as_euler("zxy",degrees=True)
        cam_img_rot = np.dot(np.array([[0,0,-1],[-1,0,0],[0,-1,0]]),cam_img_rot)
        
        result_dict = {'NED_相機座標':NED_tvec,
                    'NED_相機歐拉旋轉':cam_img_rot,
                    'rvec':rvec,
                    'tvec':np.dot(inv(rvec_matrix_CAM),-tvec)}
        # 新增相機座標系的旋轉及位移
        return result_dict

    def Global_Coordinate_seeker(self,obj_points,UAV_para,fix_cam_img_points,UAV_img_points,CAM_NUMBER,Camera_intrinsic):
    
        # UAV給定UAV座標及姿態
        UAV_pos = UAV_para[:3]
        UAV_orient = UAV_para[3:]
        Rmatrix_UAV = R.from_quat(UAV_orient)
        
        # UAV拍攝棋盤格影像點
        _, rvec, tvec = cv2.solvePnP(obj_points, UAV_img_points, self.CONFIG.UAV_Camera_intrinsic["mtx"], self.CONFIG.UAV_Camera_intrinsic["dist"])
        
        # UAV 相機坐標系 R T
        rvec_UAV = rvec
        tvec_UAV = tvec
        rvec_matrix_UAV = cv2.Rodrigues(rvec_UAV)[0]
        
        # UAV1 相機坐標系轉NED，並旋轉回UAV0相同基底坐標系
        m = np.dot(rvec_matrix_UAV,np.transpose(obj_points)) + np.transpose(tvec_UAV.repeat(4)).reshape(3,4)
        NED_chess_point = np.dot(np.array([[0,0,1],[1,0,0],[0,1,0]]),np.dot(Rmatrix_UAV.as_matrix(),m))
        x = UAV_pos[0]
        y = UAV_pos[1]
        z = UAV_pos[2]
        bias_UAV = np.array([[x*100],[y*100],[z*100]])
        #print("bias_UAV:",bias_UAV)
        # bias_UAV 機體中心座標移到左眼相機座標
        bias_UAV = bias_UAV + np.dot(Rmatrix_UAV.as_matrix(),np.dot(np.array([[0,1,0],[0,0,1],[1,0,0]]), np.array(self.CONFIG.seeker_left_eye_coordinate)))
        NED_bias_UAV = np.dot(np.array([[0,0,1],[1,0,0],[0,1,0]]),bias_UAV)
        # ned_Chess為棋盤格所有點初始UAV坐標系座標點
        ned_Chess = NED_bias_UAV.repeat(4).reshape(3,4) + NED_chess_point
        print("ned_Chess:",[ned_Chess[0][0],ned_Chess[1][0],ned_Chess[2][0]])
        
        # NED轉回相機坐標系再導入solvepnp得到固定相機姿態轉換
        ned_Chess_EDN = np.array([[0,0,1],[1,0,0],[0,1,0]])
        # 先用單一攝相頭
        _, rvec, tvec = cv2.solvePnP(np.transpose(np.dot(inv(ned_Chess_EDN),ned_Chess)), fix_cam_img_points, Camera_intrinsic["mtx"], Camera_intrinsic["dist"])
        #print('tvec',tvec)
        tvec_dist = math.sqrt(tvec[0]**2+tvec[1]**2+tvec[2]**2)
        rvec_matrix_CAM = cv2.Rodrigues(rvec)[0]
        
        # 固定相機相機坐標系再轉回UAV0 NED 坐標系
        NED_tvec = np.dot(np.array([[0,0,1],[1,0,0],[0,1,0]]),np.dot(inv(rvec_matrix_CAM),-tvec))
        NED_tvec_dist = math.sqrt(NED_tvec[0]**2+NED_tvec[1]**2+NED_tvec[2]**2)
        
        # 回推固定相機旋轉角度
        cam_img_rot = R.from_matrix(rvec_matrix_CAM).as_euler("zxy",degrees=True)
        cam_img_rot = np.dot(np.array([[0,0,-1],[-1,0,0],[0,-1,0]]),cam_img_rot)
        
        result_dict = {'NED_相機座標':NED_tvec,
                    'NED_相機歐拉旋轉':cam_img_rot,
                    'rvec':rvec,
                    'tvec':np.dot(inv(rvec_matrix_CAM),-tvec)}
        # 新增相機座標系的旋轉及位移
        return result_dict
    
    def image_callback(self,UAV_type):
        global FRAME_COUNT
        img = self.drone.l_img
        img = cv2.resize(img, self.CONFIG.img_size_640, interpolation=cv2.INTER_CUBIC)
        tags = self.at_detector.detect(img)
        cv2.imshow("drone",img)
        if len(tags)>0:
            UAV_img_points = tags[0].corners 
            tag_ID = tags[0].tag_id
            k = cv2.waitKey(1)
            if self.FRAME_COUNT%30==0:
                print("有偵測到AprilTag")
                Camera_intrinsic = self.CONFIG.camera_intrinsic_dict('CAM' + str(tag_ID))
                fix_cam_img_points = self.DBCONN.SelectAprilTag(tag_ID)
                if UAV_type=="seeker":
                    result_dict = self.Global_Coordinate_seeker(self.objectPoints,self.drone.state.pose_array,fix_cam_img_points,UAV_img_points,tag_ID,Camera_intrinsic)
                if UAV_type=="deck":
                    result_dict = self.Global_Coordinate_deck(self.objectPoints,self.drone.state.pose_array,fix_cam_img_points,UAV_img_points,tag_ID,Camera_intrinsic)
                CAM_Coordinate, CAM_Rotation = result_dict["NED_相機座標"], result_dict["NED_相機歐拉旋轉"]
                CameraName = "CAM" + str(tag_ID)
                cameraID = tag_ID
                self.DBCONN.CommitCameraPose(CameraName, cameraID, str(result_dict["rvec"]) + "|||" + str(result_dict["tvec"]))
                print("已存取AprilTagNO."+str(tag_ID)+"相機姿態")
                print("座標點：", CAM_Coordinate)
                print("相機旋轉：", CAM_Rotation)
                print("請到下個目標點")
                cv2.waitKey(100)
        else:
            if self.FRAME_COUNT%30==0:
                print("UAV無偵測到AprilTag")
    def start(self):
        rospy.init_node('my_node')
        rospy.sleep(0.1)
        self.FRAME_COUNT = 0
        UAV_type = self.CONFIG.UAV_type
        while True:
            self.FRAME_COUNT += 1
            self.image_callback(UAV_type)
            if cv2.waitKey(1) & 0xFF == 27: # 按ESC键退出
                cv2.destroyAllWindows()
                break
    def _print_(self):
        print("UAV_type:",self.CONFIG.UAV_type)
    def test(self):
        tag_ID = 2
        Camera_intrinsic = self.CONFIG.camera_intrinsic_dict('CAM' + str(tag_ID))
        fix_cam_img_points = self.DBCONN.SelectAprilTag(tag_ID)
        print("fix_cam_img_points",fix_cam_img_points)
        print(self.objectPoints)
        _, rvec, tvec = cv2.solvePnP(self.objectPoints, fix_cam_img_points, Camera_intrinsic["mtx"], Camera_intrinsic["dist"])
        print("tvec",tvec)
        distance = (tvec[0]**2+tvec[1]**2+tvec[2]**2)**(1/2)
        print("distance",distance)
if __name__ == '__main__':
    CPL = CamPoseLocalization()
    # CPL.start()
    CPL.test()



