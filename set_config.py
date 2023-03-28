import configparser
config = configparser.ConfigParser()
config['apriltag'] = {'pic_length':17.3/2,
                      'family':'tag36h11'}
config['vaidio'] = {'username':'admin',
                    'password':'admin888',
                    'IP':'192.168.100.122'}
config['Camera_intrinsic'] = {
                              'CAM0':{'mtx':[480.08274897,640.42426497,322.3045579,237.74001277],
                                 'dist':[-0.38319973,  0.26434886, -0.00780246, -0.00402194, -0.12994215],
                                 'img_size':(640,480),
                                 'Account': 'admin',
                                 'Code': 'admin',
                                 'URL': '192.168.100.241:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif'},
                              'CAM1':{'mtx':[452.0470078,604.14752415,326.74924085,221.17155039],
                                 'dist':[-0.37682073,  0.24138815, -0.00053286, -0.00297059, -0.11777432],
                                 'img_size':(640,480),
                                 'Account': 'admin',
                                 'Code': 'admin',
                                 'URL': '192.168.100.242:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif'}
                             }
config['UAV_intrinsic'] = {'UAV_broad':{'mtx':[498.8283486506022,499.4135404584406,369.0487560590798,253.4824839360555],
                                        'dist':[-0.1657184435996157, 0.05895088459980649, 0.0011006326035910502, 0.00046100699953617906],
                                        'img_size':(640,480),
                                        'left_eye_coordinate':[[10],[-4],[0]]}
                          }
config['img_size'] = {'640':(640,480)}
with open('config.ini', 'w') as configfile:
    config.write(configfile)
another_config = configparser.ConfigParser()
another_config.read('config.ini')
import numpy as np
[fx,fy,cx,cy] = eval(another_config['Camera_intrinsic']['CAM1'])['mtx']
dist = eval(another_config['Camera_intrinsic']['CAM1'])['dist']
dist = np.array([dist])
Camera_intrinsic={'mtx':np.array([[fx,0,cx],[0,fy,cy],[0,0,1]]),
                  'dist':dist}
print(Camera_intrinsic)
