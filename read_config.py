import configparser
import numpy as np
# config檔
config = configparser.ConfigParser()
config.read('config.ini')

class config_:
    def __init__(self):

        # MYSQL
        self.DB_host = config['MYSQL']['host']
        self.DB_user = config['MYSQL']['user']
        self.DB_password = config['MYSQL']['password']
        self.DB_database = config['MYSQL']['database']

        # apriltag設定，family和apriltag大小
        self.apriltag_family = config['apriltag']['family']
        self.apriltag_pic_length = float(config['apriltag']['pic_length'])

        # Vaidio帳密
        self.username = config['vaidio']["username"]
        self.password = config['vaidio']["password"]
        self.Vaidio_IP = config['vaidio']["IP"]
        self.object_detect_url = 'http://{0}/ainvr/api/detection/objects?plugins=PeopleCountingEngine'.format(self.Vaidio_IP)

        # 影像resize大小
        self.img_size_640 = eval(config['img_size']["640"])
        self.cameraIDs = self.CameraIDs()

        #  UAV 
        self.UAV_type = config['UAV_type']["UAV_name"]
        self.UAV_Camera_intrinsic = self.uav_intrinsic_dict(self.UAV_type)
        self.broad_left_eye_coordinate = eval(config['UAV_intrinsic']["deck"])["left_eye_coordinate"]
        self.seeker_left_eye_coordinate = eval(config['UAV_intrinsic']["seeker"])["left_eye_coordinate"]

        # SIFT
        self.good_match_distance_threshold = config["SIFT"]["match_threshold"]
    # 所有 camera ID
    def CameraIDs(self):
        keylist = dict(config['Camera_intrinsic']).keys()
        cameraID_List = []
        for key in keylist:
            cameraID_List.append(eval(config['Camera_intrinsic'][key])['cameraID'])
        return cameraID_List

    #　調用UAV相機內參
    def uav_intrinsic_dict(self,UAV_name):
        [fx,fy,cx,cy] = eval(config['UAV_intrinsic'][UAV_name])['mtx']
        dist = eval(config['UAV_intrinsic'][UAV_name])['dist']
        dist = np.array([dist])
        UAV_Camera_intrinsic={'mtx':np.array([[fx,0,cx],[0,fy,cy],[0,0,1]]),
                        'dist':dist}
        return UAV_Camera_intrinsic
    
    # 調用對應IPCAM 內參
    def camera_intrinsic_dict(self,CAM_name):
        [fx,fy,cx,cy] = eval(config['Camera_intrinsic'][CAM_name])['mtx']
        dist = eval(config['Camera_intrinsic'][CAM_name])['dist']
        dist = np.array([dist])
        Camera_intrinsic={'mtx':np.array([[fx,0,cx],[0,fy,cy],[0,0,1]]),
                        'dist':dist}
        return Camera_intrinsic
    
    #UAVisionObjectLocalization
    def Q_Array(self,UAV_name):

        [fx_l,fy_l,Cx_l,Cy_l] = eval(config['stereo']['stereo_intrinsics_'+UAV_name])['M1']
        [fx_r,fy_r,Cx_r,Cy_r] = eval(config['stereo']['stereo_intrinsics_'+UAV_name])['M2']
        [Tx,_,_] = eval(config['stereo']['stereo_extrinsics_'+UAV_name])['T']

        # C++參數設置https://blog.csdn.net/Gordon_Wei/article/details/86319058
        # C++ https://www.796t.com/post/N2JrdGk=.html
        #python https://github.com/PacktPublishing/OpenCV-with-Python-By-Example/blob/master/Chapter11/stereo_match.py
        Q = np.float32([[1, 0, 0, -1*Cx_l],
                        [0,-1, 0,  1*Cy_l], 
                        [0, 0, 0, -1*fx_l], 
                        [0, 0, -1/Tx, ((Cx_l-Cx_r)/Tx)]])
        return Q
    
    #SIFT_UAVisionObjectLocalization
    def Q_parameter(self,UAV_name):
        [fx_l,fy_l,Cx_l,Cy_l] = eval(config['stereo']['stereo_intrinsics_'+UAV_name])['M1']
        [fx_r,fy_r,Cx_r,Cy_r] = eval(config['stereo']['stereo_intrinsics_'+UAV_name])['M2']
        [Tx,_,_] = eval(config['stereo']['stereo_extrinsics_'+UAV_name])['T']
        return fx_l,fy_l,Cx_l,Cy_l,Tx