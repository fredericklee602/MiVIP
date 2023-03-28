import cv2
import numpy as np
import math
import requests
from scipy.spatial.transform import Rotation as R
from numpy.linalg import inv
from DB_SQL import DB_connect
import time
from read_config import config_
from Vaidio_API import API

class Object_World_Coordinate():
    def __init__(self):
        self.CONFIG = config_()

        # UAV intrinsics extrinsics
        self.left_eye_coordinate = self.CONFIG.broad_left_eye_coordinate
        self.seeker_left_eye_coordinate = self.CONFIG.seeker_left_eye_coordinate
        self.fx_l,self.fy_l,self.Cx_l,self.Cy_l,self.Tx = self.CONFIG.Q_parameter(self.CONFIG.UAV_type)

        # MYSQL DB
        self.DBCONN = DB_connect()
        self.DBCommit_cycle = 20
        
        # setup sift
        self.sift = cv2.SIFT_create()
        self.matcher = cv2.BFMatcher()
        self.good_match_distance_threshold = int(self.CONFIG.good_match_distance_threshold)
    def POS(self,data):
        pose_array = np.array([1, 2, 3, 4, 5, 6, 7],dtype='f')
        pose_array[0] = data.pose.position.x
        pose_array[1] = data.pose.position.y
        pose_array[2] = data.pose.position.z
        pose_array[3] = data.pose.orientation.x
        pose_array[4] = data.pose.orientation.y
        pose_array[5] = data.pose.orientation.z
        pose_array[6] = data.pose.orientation.w
        return pose_array
    
    # 將物件的相機座標（obj_coordinate）透過UAV拍攝時位姿(UAV_para)，轉換為世界座標系
    # input 物件座標,UAV姿態參數
    # 回傳值：NED/m
    def Global_Coordinate(self,obj_coordinate,UAV_para):
        # UAV給定UAV座標及姿態
        UAV_pos = UAV_para[:3] # NED
        UAV_orient = UAV_para[3:] #NED
        Rmatrix_UAV = R.from_quat(UAV_orient)
        # EDS座標系轉NED
        NED_obj_coordinate = np.dot(Rmatrix_UAV.as_matrix(),np.dot(np.array([[0,0,-1],[1,0,0],[0,1,0]]),np.transpose(obj_coordinate)))
        x = UAV_pos[0]
        y = UAV_pos[1]
        z = UAV_pos[2]
        bias_UAV = np.array([[x],[y],[z]])
        # bias_UAV 機體中心座標移到左眼相機座標
        bias_UAV = bias_UAV + np.dot(Rmatrix_UAV.as_matrix(),np.array(self.left_eye_coordinate)*0.01)
        world_obj_coordinate = bias_UAV + np.transpose(np.array([NED_obj_coordinate]))
        return world_obj_coordinate
    
    # 將物件的相機座標（obj_coordinate）透過UAV拍攝時位姿(UAV_para)，轉換為世界座標系
    # input 物件座標,UAV姿態參數
	# 回傳值：NED/m
    def Global_Coordinate_seeker(self,obj_coordinate,UAV_para):
        #print("obj_coordinate(EDS)",obj_coordinate)
        # UAV給定UAV座標及姿態
        UAV_pos = UAV_para[:3] # EDN
        UAV_orient = UAV_para[3:] # EDN
        Rmatrix_UAV = R.from_quat(UAV_orient)
        # 將物件的相機座標旋轉至與UAV座標一致，再進行座標系轉換:EDS=>NED
        obj_coordinate = np.dot(np.array([[1,0,0],[0,1,0],[0,0,-1]]),np.transpose(obj_coordinate))
        NED_obj_coordinate = np.dot(np.array([[0,0,1],[1,0,0],[0,1,0]]),np.dot(Rmatrix_UAV.as_matrix(),obj_coordinate))
        #print("與世界座標旋轉對齊NED_obj_coordinate",np.transpose(NED_obj_coordinate))
        x = UAV_pos[0]
        y = UAV_pos[1]
        z = UAV_pos[2]
        bias_UAV = np.array([[x],[y],[z]])
        #print("UAV coordinate(EDN)", np.transpose(bias_UAV))
        # 單位換算cm=>m
        camera_coordinate_local = np.array(self.seeker_left_eye_coordinate)*0.01
        
        # 相機座標之座標系轉換：NED => EDN
        camera_coordinate_local = np.dot(np.array([[0,1,0],[0,0,1],[1,0,0]]),camera_coordinate_local)
        #print("camera_coordinate_local(EDN)",camera_coordinate_local)
        # 將相機座標進行旋轉及位移，轉換為左眼相機的世界座標：EDN
        camera_coordinate = bias_UAV + np.dot(Rmatrix_UAV.as_matrix(),camera_coordinate_local)
        #print("camera_coordinate_global(EDN)",np.transpose(camera_coordinate))
        # bias_UAV 機體中心座標移到左眼相機座標
        # 座標系變換：EDN => NED
        camera_coordinate = np.dot(np.array([[0,0,1],[1,0,0],[0,1,0]]), camera_coordinate)
        #print("camera_coordinate(NED)",np.transpose(camera_coordinate))
        world_obj_coordinate = camera_coordinate + np.transpose(np.array([NED_obj_coordinate]))
        return world_obj_coordinate

    #https://panjinquan.blog.csdn.net/article/details/121301896
    def dfsto3D(self, disparity_map, UAV_type):
        if UAV_type=="deck":
            Q = self.CONFIG.Q_Array(UAV_type)
        if UAV_type=="seeker":
            Q = self.CONFIG.Q_Array(UAV_type)
        points_3D = cv2.reprojectImageTo3D(disparity_map, Q, ddepth=cv2.CV_32F)
        points_3D = np.asarray(points_3D, dtype=np.float32)
        return points_3D

    #https://www.ray0728.cn/2021/06/11/%E7%A6%BB%E7%BE%A4%E7%82%B9%E8%BF%87%E6%BB%A4/
    # 距離整體方框中間值距離*2.5的過濾
    def __remove_outlier(self, points):
        median = np.median(points, axis=0)
        deviations = abs(points - median)
        mad = np.median(deviations, axis=0)
        remove_idx = np.where(deviations > mad)
        return np.delete(points, remove_idx, axis=0)

    # draw object recognition and coordinate on frame
    # Colors.
    def draw_label(self,frame, label, x, y,coordinate):
        """Draw text onto image at location."""
        # Text parameters.
        FONT_FACE = cv2.FONT_HERSHEY_SIMPLEX
        FONT_SCALE = 0.5
        THICKNESS = 1
        color = (255.0)
        # Get text size.
        string_coordinate = ", ".join([str(int(coordinate[0]*100)), str(int(coordinate[1]*100)), str(int(coordinate[2]*100))])
        # 字串可顯示大小
        text_size = cv2.getTextSize(label + string_coordinate, FONT_FACE, FONT_SCALE, THICKNESS)
        dim, baseline = text_size[0], text_size[1]
        # Use text size to create a BLACK rectangle.
        cv2.rectangle(frame, (x,y), (x + dim[0], y + dim[1] + baseline), (0,0,0), cv2.FILLED);
        # Display text inside the rectangle.
        cv2.putText(frame, label + string_coordinate, (x, y + dim[1]), FONT_FACE, FONT_SCALE, color, THICKNESS, cv2.LINE_AA)
    def calc_3D(self, fx, fy, ox, oy, baseline, disparity, left_image_x, left_image_y):
        z_3D=fx*baseline/disparity
        x_3D = baseline*(left_image_x-ox)/disparity
        y_3D = (fx*baseline*(left_image_y-oy))/(fy*disparity)
        return [x_3D, y_3D, z_3D]
    
    def filter_depth_outlier_in_roi(self, roi_depths):
        # Filter outlier, this is especially useful when roi contians many object.
        # There may be a better way.
        percentile_90th = np.percentile(roi_depths, 90)
        percentile_10th = np.percentile(roi_depths, 10)
        filtered_roi_depths = [depth for depth in roi_depths if (depth > percentile_10th) and (depth < percentile_90th)]
        average_depth_filtered = sum(filtered_roi_depths) / len(filtered_roi_depths) if len(filtered_roi_depths) > 0 else 0 

    # Simple Stereo
    def cal_coordinate_only(self, rsp_js, frame, disparity, dfs_frame,UAV_para, UAV_type, step):
        # object file
        object_name_list = []
        coordinate_list = []
        coordinate_start = time.time()
        for obj in rsp_js:
            x,y,w,h = obj['x'], obj['y'], obj['w'], obj['h']
            name = obj['objectType']
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255,0,0), 2)
            if int(x + w/2) < dfs_frame.shape[0] and int(y + h/2) < dfs_frame.shape[1] and name=="head":
                # 取bounding box範圍內的3D點做計算
                disparity_zone = disparity[x:x + w,y:y + h]
                # 只取disparity>0的pixel點
                disparity_zone_idx = np.where(disparity_zone > 0)
                dfs_zone = dfs_frame[x:x + w,y:y + h]
                dfs_zone_select = dfs_zone[disparity_zone_idx]
                # 刪除離群點
                dfs_zone_select = self.__remove_outlier(dfs_zone_select)
                #座標點加總平均
                if len(dfs_zone_select)>0:
                    coordinate = dfs_zone_select.sum(axis=0)/len(dfs_zone_select)
                    if UAV_type=="deck":
                        coordinate = self.Global_Coordinate(coordinate,UAV_para)
                    if UAV_type=="seeker":
                        coordinate = self.Global_Coordinate_seeker(coordinate,UAV_para)
                    coordinate = np.round(coordinate,2)
                    string_coordinate = ", ".join([str(coordinate[0]), str(coordinate[1]), str(coordinate[2])])
                    object_name_list.append(name)
                    coordinate_list.append("["+string_coordinate+"]")
                    self.draw_label(frame, name, x, y,coordinate)
                    cv2.rectangle(dfs_frame, (x, y), (x + w, y + h), (255,0,0), 2)
                    if step%self.DBCommit_cycle==0:
                        self.DBCONN.CommitObjectCoordinate(0, name, str(coordinate).replace("\n ",","))
                        print("---DB Commit---")
        coordinate_time = time.time()-coordinate_start
        print("偵測到：{0}".format(",".join(object_name_list)))
        print("coordinate:{0}".format(",".join(coordinate_list)))    
        return frame, disparity, dfs_frame, coordinate_time

    # SIFT
    def SIFT_Match(self,left_frame, right_frame):
        sift_start = time.time()
        queryKeypoints, queryDescriptors = self.sift.detectAndCompute(left_frame,None)
        trainKeypoints, trainDescriptors = self.sift.detectAndCompute(right_frame,None)
        matches = self.matcher.match(queryDescriptors,trainDescriptors)
        sift_end = time.time()
        print("sift_time:", sift_end-sift_start)
        return queryKeypoints, trainKeypoints, matches

    def calc_coordinate(self,left_frame,UAV_para, UAV_type, rsp_js, queryKeypoints, trainKeypoints, matches, step):
        object_name_list = []
        coordinate_list = []
        coordinate_start = time.time()
        good_matches = []
        for obj in rsp_js:
            x,y,w,h = obj['x'], obj['y'], obj['w'], obj['h']
            x1 = left_frame.shape[0]
            y1 = left_frame.shape[1]
            if int(x + w) < left_frame.shape[0]:
                x1 = int(x + w)
            if int(y + h) < left_frame.shape[1]:
                y1 = int(y + h)
            name = obj['objectType']
            #print(name)
            if name == "head":
                roi_depths = []
                for match in matches:
                    left_key_point_idx = match.queryIdx
                    right_key_point_idx = match.trainIdx

                    left_key_point = queryKeypoints[left_key_point_idx]
                    right_key_point = trainKeypoints[right_key_point_idx]
                    
                    #roi means Region of Interest, it is the bounding box of the object in this case
                    x_is_in_roi = (int(x) <= left_key_point.pt[0]) and (left_key_point.pt[0] <= int(x1))
                    y_is_in_roi = (int(y) <= left_key_point.pt[1]) and (left_key_point.pt[1] <= int(y1))
                    left_key_point_is_in_roi = y_is_in_roi and x_is_in_roi
                    if not left_key_point_is_in_roi: continue 
                    if match.distance > self.good_match_distance_threshold: continue #Filter mismatch. There may be a better way.
                    
                    good_matches.append(match)
                    disparity = abs(left_key_point.pt[0] - right_key_point.pt[0])
                    if disparity == 0: continue
                    fx, fy, ox, oy, baseline = self.fx_l,self.fy_l,self.Cx_l,self.Cy_l,self.Tx
                    left_image_x, left_image_y = left_key_point.pt[0], right_key_point.pt[0]
                    stereo_depth_of_current_pair = self.calc_3D(fx, fy, ox, oy, baseline, disparity, left_image_x, left_image_y)
                    roi_depths.append(stereo_depth_of_current_pair)
                if len(roi_depths) < 3:
                    coordinate_filtered = []
                if len(roi_depths) > 2:
                    coordinate_filtered = self.__remove_outlier(np.array(roi_depths))
                if len(coordinate_filtered)>0:
                    coordinate = coordinate_filtered.sum(axis=0)/len(coordinate_filtered)
                    if UAV_type=="deck":
                        coordinate = self.Global_Coordinate(coordinate,UAV_para)
                    if UAV_type=="seeker":
                        coordinate = self.Global_Coordinate_seeker(coordinate,UAV_para)
                    coordinate = np.round(coordinate,2)
                    self.draw_label(left_frame, name, x, y,coordinate)
                    string_coordinate = ", ".join([str(coordinate[0]), str(coordinate[1]), str(coordinate[2])])
                    coordinate_list.append("["+string_coordinate+"]")
                    object_name_list.append(name)
                    if step%self.DBCommit_cycle==0:
                        self.DBCONN.CommitObjectCoordinate(0, name, str(coordinate).replace("\n ",","))
                        print("---DB Commit---")
                cv2.rectangle(left_frame, (x, y), (x + w, y + h), (255,0,0), 2)
        coordinate_end = time.time()
        coordinate_time = coordinate_end - coordinate_start
        print("偵測到：{0}".format(",".join(object_name_list)))
        print("coordinate:{0}".format(",".join(coordinate_list)))    
        return left_frame, coordinate_time