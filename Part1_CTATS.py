# Part 1 Vaideo存照片
# 讀取Vaidio圖片
import cv2
from urllib.request import urlopen
import numpy as np
import apriltag
import os
from DB_SQL import DB_connect
from read_config import config_
from Vaidio_API import API

class CamTakingAprilTagShot:
    def __init__(self):

        self.CONFIG = config_()
        self.at_detector = apriltag.Detector(apriltag.DetectorOptions(families=self.CONFIG.apriltag_family))
        # MySQL DB
        self.DBCONN = DB_connect()
        self.api = API()
    def CommitDB(self):
        # All camera ID in config.ini
        # cameraID_List = [1]
        cameraID_List = []
        cameraname_List = []
        for list_ in self.api.cameraIDs():
            cameraname_List.append(list_[0])
            cameraID_List.append(list_[1])
        while len(cameraID_List) !=0 :
            cameraID_List_ = cameraID_List
            # for cameraID in cameraID_List_:
            for i in range(len(cameraID_List_)):
                cameraID = cameraID_List_[i]
                # Get live streaming Image
                img, gray = self.api.GetStreamImage(cameraID)
                tags = self.at_detector.detect(gray)
                
                # 如果有偵測到apriltag，則存取apriltag資訊及該圖片到資料夾
                if len(tags)>0:
                    tags_number = tags[0].tag_id
                    img_dir = "./images_stream_{0}".format(tags_number)
                    isExist = os.path.exists(img_dir)
                    if not isExist:
                        os.mkdir(img_dir)
                    cv2.imwrite("./images_stream_{0}/apriltag.png".format(tags_number), img, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
                    corners = tags[0].corners
                    print("corners",corners)
                    print(type(corners))
                    CameraName = cameraname_List[i]
                    self.DBCONN.CommitAprilTag(CameraName, cameraID, str(corners),tags_number)
                    print("{0}有偵測到apritag ID NO.{1}".format(CameraName,tags_number))
                    cameraID_List.remove(cameraID)
                elif len(tags)==0:
                    CameraName = "CAM" + str(cameraID)
                    print("{0}未偵測到到任何apriltag。".format(CameraName))

