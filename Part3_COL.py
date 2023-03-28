# part3 Vaideo 物件座標讀取
import math
import numpy as np
import json
from flask import Flask, request
from flask_restful import Api
from flask_restful import Resource
import cv2
# inv輸出反矩陣
from numpy.linalg import inv
from DB_SQL import DB_connect
from read_config import config_
from Vaidio_API import API
class WorldObjectCoordinate:
    def __init__(self):
        self.step = 0
        # 連線DB
        self.DBCONN = DB_connect()
        self.CONFIG = config_()
        self.api = API()
    def World_Object_Coordinate(self,sceneID,CAM_NAME,shape,Camera_intrinsic):
        # CAMID = CAM_NAME.replace("CAM","")
        cam_rvec, cam_tvec = self.DBCONN.SelectCameraPose(CAM_NAME)
        img = self.api.GetImage(sceneID)
        # record original image size
        img_height = img.shape[0]
        img_width= img.shape[1]
        img = cv2.resize(img,shape, interpolation=cv2.INTER_CUBIC)
        # 放大縮小比例, for resizing object bounding box
        x_scale = shape[0] / img_width
        y_scale = shape[1] / img_height
        # 物件在相機坐標系下的座標點
        object_cam_coordinate = {}
        obj_count = 0
        with open('object_size.json') as f:
            object_size = json.load(f)
        obj_list = self.api.ObjectDetect(sceneID)
        for obj in obj_list:
            objectType = obj["objectType"]
            # calculate the location of an object at a time
            # retrieve the bounding box of this object
            obj_bbox = [int(obj["x"]*x_scale),int(obj["y"]*y_scale),int(obj["w"]*x_scale),int(obj["h"]*y_scale)]
            # 設定bounding box 真實寬高
            h = None
            w = None
            # if objectType not in object_size.keys():
            #     # 物件如沒被設定
            #     print("{0}不在{1}設定檔案中".format(objectType,'object_size.json'))
            #     print("請在{0}檔案新增該物件".format('object_size.json'))
            #     continue
            if objectType != "head":
                continue
            elif objectType in object_size.keys():
                h = object_size[objectType]["height"]
                w = object_size[objectType]["width"]
                if h>0 and w>0:
                    print("預設物件{0}大小：{1}".format(objectType,object_size[objectType]))
                else:
                    print("預設物件{0}大小：{1}，可能有誤，請更改物件大小數值。".format(objectType,object_size[objectType]))
                    continue
            objectPoints = np.array([[[-1*h/2, -1*w/2, 0],
                                    [1*h/2, -1*w/2, 0], 
                                    [1*h/2, 1*w/2, 0], 
                                    [-1*h/2, 1*w/2, 0]]],
                                    dtype=np.float32)

            # object bounding box (x,y,w,h) ==> coordinates of object boudning box corners 影像平面2D座標
            imgPoints = np.array([[[obj_bbox[0],obj_bbox[1]],[obj_bbox[0]+obj_bbox[2],obj_bbox[1]],[obj_bbox[0]+obj_bbox[2],obj_bbox[1]+obj_bbox[3]],
                                [obj_bbox[0],obj_bbox[1]+obj_bbox[3]]]],
                                    dtype=np.float32)

            # 計算點座標 calculate 3D coordinates of object bounding box coners 
            _, rvec, tvec = cv2.solvePnP(objectPoints, imgPoints, Camera_intrinsic["mtx"], Camera_intrinsic["dist"])
            
            cam_rvec_matrix = cv2.Rodrigues(cam_rvec)[0]    # 旋轉向量->旋轉矩陣
            # 轉到UAV座標系上且轉到NED
            # NEDUAVcor_obj_tvec = np.dot(np.array([[0,0,1],[1,0,0],[0,1,0]]),np.dot(inv(cam_rvec_matrix),tvec-cam_tvec))
            EDNUAVcor_obj_tvec = np.dot(inv(cam_rvec_matrix),tvec) + cam_tvec
            NEDUAVcor_obj_tvec = np.dot(np.array([[0,0,1],[1,0,0],[0,1,0]]),EDNUAVcor_obj_tvec)
            object_cam_coordinate.update({obj_count:{objectType:{'CAM_point':tvec,
                                                    'UAV_point':NEDUAVcor_obj_tvec}}})
            obj_count = obj_count+1
            print("World Coordinate:")
            print(NEDUAVcor_obj_tvec)
            print("----------------")
            self.DBCONN.CommitObjectCoordinate(sceneID, objectType, str(NEDUAVcor_obj_tvec).replace("\n ",","))
            print("---DB Commit---")
        # 存取物件座標dict
        img_file = './object_cam_coordinate/photo_scene_ID_{0}.jpg'.format(sceneID)
        cv2.imwrite(img_file, img)
class PrintHelloWorld(Resource):
    def get(self):
        return {
            'message': 'Hello Wrold!'
        }, 200

class ObjectItem(Resource):
    def __init__(self):
        self.item = {}
        self.WOC = WorldObjectCoordinate()
        self.CONFIG = config_()
    # 取得所有品項
    def get(self):
        return self.item, 200
    
    def post(self):
        data = request.get_json()
        print(data)
        self.item = {
                  "VaidioIp": data["VaidioIp"],
                  "AlertImage": data["AlertImage"],
                  "NvrId": data["NvrId"],
                  "CameraName": data["CameraName"],
                  "CameraId": data["CameraId"],
                  "RoiId": data["RoiId"],
                  "EventTimeStamp": data["EventTimeStamp"],
                  "SceneID": data["SceneID"]
                }
        CAM_NAME = data["CameraName"]
        Camera_intrinsic = self.CONFIG.camera_intrinsic_dict(CAM_NAME)
        # resize image size to (640,480)
        shape = self.CONFIG.img_size_640
        self.WOC.World_Object_Coordinate(data["SceneID"],CAM_NAME,shape,Camera_intrinsic)
        return self.item, 201
class Post_test(Resource):
    def post(self):
        data = request.get_json()
        print(data)
        return 202
class CamObjectLocalization:
    def __init__(self):
        self.app = Flask(__name__)
        self.Flaskapi = Api(self.app)
        self.Flaskapi.add_resource(PrintHelloWorld, "/print_hello_world/")
        self.Flaskapi.add_resource(ObjectItem, "/object_item/")
        self.Flaskapi.add_resource(Post_test, "/Post_test/")
    def run(self):
        self.app.run(host="0.0.0.0", port=5000)
