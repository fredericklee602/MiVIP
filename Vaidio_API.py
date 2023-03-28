from read_config import config_
from urllib.request import urlopen
import requests
import cv2
import numpy as np
import time
class API:
    def __init__(self):
        self.CONFIG = config_()
        self.Vaidio_IP = self.CONFIG.Vaidio_IP
    def streaming(self,cameraID):
        url = "http://{0}/ainvr/api/streaming/{1}/live.jpg".format(self.Vaidio_IP,cameraID)
        return url

    def scenes_objects(self,scene_ID):
        url = "http://{0}/ainvr/api/scenes/{1}/objects".format(self.Vaidio_IP,scene_ID)
        return url

    def scenes_image(self,scene_ID):
        url = "http://{0}/ainvr/api/scenes/{1}".format(self.Vaidio_IP,scene_ID)
        return url

    def detection_objects(self):
        url = 'http://{0}/ainvr/api/detection/objects?plugins=PeopleCountingEngine'.format(self.Vaidio_IP)
        return url

    def VaidioConnectTest(self):
        url = "http://{0}/ainvr/api/ainvrs".format(self.Vaidio_IP)
        response = requests.get(url, auth=(self.CONFIG.username, self.CONFIG.password))
        if response.status_code == 200:
            print("Successfully connected to the Vaidio IP [{0}].".format(self.Vaidio_IP))
            return True
        else:
            print("Error when Connecting to Vaidio IP [{0}]. Please confirm the Vaidio connection status.".format(self.Vaidio_IP))
            return False
        
    def cameras_information(self):
        url = "http://{0}/ainvr/api/cameras".format(self.Vaidio_IP)
        response = requests.get(url, auth=(self.CONFIG.username, self.CONFIG.password))
        if response.status_code == 200:
            return response.json()["content"]
        else:
            print("Error when Connecting to Vaidio IP [{0}]. Please confirm the Vaidio connection status.".format(self.Vaidio_IP))
            return False
    # Part1
    def GetStreamImage(self, cameraID):
        url = self.streaming(cameraID)
        req = urlopen(url)
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        # Origin Image
        img = cv2.imdecode(arr, -1) # 'Load it as it is'
        img = cv2.resize(img,self.CONFIG.img_size_640, interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        return img, gray

    # Part3
    def GetImage(self,scene_ID):
        url = self.scenes_image(scene_ID)
        response = requests.get(url, auth=(self.CONFIG.username, self.CONFIG.password))
        file_url = response.json()["file"]
        req = urlopen(file_url)
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        img = cv2.imdecode(arr, -1)
        return img

    # Part3
    def ObjectDetect(self, scene_ID):
        object_url = self.scenes_objects(scene_ID)
        object_response = requests.get(object_url, auth=(self.CONFIG.username, self.CONFIG.password))
        obj_list = object_response.json()
        return obj_list

    # Part4
    # frame:origin scene
    def connect_vaidio_only(self,frame):
        rsp_start = time.time()
        # image array to byte and post it to vaidio
        success, frame_encoded = cv2.imencode('.jpg', frame)
        assert success # always check for errors, at least fail hard
        frame_bytes = frame_encoded.tobytes() # numpy array to bytes object
        response = requests.post(self.CONFIG.object_detect_url, auth=(self.CONFIG.username, self.CONFIG.password), files={'file': frame_bytes})
        rsp_js = response.json()
        rsp_time = time.time()-rsp_start
        return rsp_js, rsp_time
    
    def cameraIDs(self):
        info = self.cameras_information()
        cameraID_list = []
        for dict_ in info:
            cameraID_list.append([dict_["name"],dict_["cameraId"]])
        return cameraID_list
