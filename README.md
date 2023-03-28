# World_Coordinate_synchronous

## 專案說明

* 現今攝像機可能有多個擺放於某些空間中，各相機均可以計算出各自的相機坐標系
<img src="https://github.com/frederickazion/World_Coordinate_synchronous/blob/main/github_img/%E5%9C%96%E7%89%871.png" width="500" height="300" alt="fig1"/><br/>
* 想要完成多個相機世界座標同步，我們利用UAV及AprilTag來計算各個相機的世界座標及旋轉角度。
* UAV初始點做為世界座標原點，用qvio輸出的UAV姿態當作回推依據，並加上各AprilTag的拍攝相互對應關係，計算出相機世界座標姿態。

<img src="https://github.com/frederickazion/World_Coordinate_synchronous/blob/main/github_img/%E5%9C%96%E7%89%872.png" width="500" height="300" alt="fig1"/><br/>
## Vaidio定位流程
1. Vaidio上設定連線IPCAM
2. 編輯設定檔AprilTag Size、MySQL Config、Vaidio Config
3. 計算IPCAM Camera Instrict GUI
4. 擺設AprilTag於IPCAM可拍攝位置，紀錄ApriTag 2D點位到MySQL
5. 連接UAV，於所有AprilTag拍攝並與對應IPCAM拍攝的2D點計算出IPCAM姿態，且存到MySQL
6. Vaidio Alert 設置
7. Vaidio Alert接收端，計算物件座標，寫入MySQL
8. (另外)UAV相機計算物件座標
### 整體架構圖
![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/architect_all.png)

## Vaidio上設定連線IPCAM
* 連接串流影像的IPCAM

![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/Vaidio_connect_IPCAM.png)
* 可即時辨識物件

![FLOW](https://github.com/frederickazion/World_Coordinate_synchronous/blob/main/github_img/%E5%9C%96%E7%89%873.png)

* Vaidio會依照畫面改變或是一段時間存取多張圖片，可依照時間範圍做搜尋。

![FLOW](https://github.com/frederickazion/World_Coordinate_synchronous/blob/main/github_img/%E5%9C%96%E7%89%874.png)

* Vaidio API http://{VaidioIP}//ainvr/api/scenes?cameraIds={ID}&start={start}&end={end}
* 輸入：Camera ID、開始日期時間、結束日期時間，可搜尋多張圖片訊息。
* 輸出：sceneId、datetime、cameraId、file、source、cameraName

![FLOW](https://github.com/frederickazion/World_Coordinate_synchronous/blob/main/github_img/%E5%9C%96%E7%89%875.png)

## main.py
1. 呼叫DB_SQL.py函式連接DB確認是否連線
2. 呼叫Vaidio.py函式連接Vaidio確認是否連線
3. 初始結束後，要求輸入00、01、1~4的數字
![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/main_first.png)
### 整體關聯圖
![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/flow_chart_initi.png)

### 程式元件
1. main.py：主程式，初始確定連接MySQL、Vaidio，初始畫面，輸入0~4的數字選擇所要的步驟。
2. DB_SQL.py：所有需要跟DB互動的動作都會使用該程式中函式。
3. Vaidio_API.py：所有需要與Vaidio連線、物件偵測、Vaidio Alert等等函式。
4. configGUI.py：輸入MiVIP Config的界面。
5. config.ini：所有有關MiVIP的配置存放。
6. read_config.py：讀取config.ini後轉成可被使用的資料型態之變數或函式。
7. Part1_CTATS.py：CamTakingAprilTagShot，存取AprilTag Corners到DB。
8. Part2_CPL.py：CamPoseLocalization，連接UAV，移動UAV拍攝到AprilTag，計算IPCAM Pose，將Pose寫入DB。
9. Part3_COL.py：CamObjectLocalization，架設HTTP，接收Vaidio偵測到物件的Alert訊息，將物件世界座標寫進DB。
10. Part4_sift.py：連接UAV，以SIFT當作特徵匹配計算深度，再計算世界座標，並寫入DB。
11. Part4_stereo.py：連接UAV，以Stereo計算深度，再計算世界座標，並寫入DB。
12. UAVisionObjectLocalization_.py：負責做物件座標深度計算函式。
## configGUI.py 00
* 編輯設定檔
* AprilTag Size、MySQL Config、Vaidio Config
![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/GUI.png)
## chessboard_GUI.py 01
* 計算IPCAM Camera Instrict GUI
* 輸入對應的IPCAM ID
* chessboard 方寬長度
* 蒐集data數量

![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/chessboard_config.png)

## Part1_CTATS.py
* 紀錄IPCAM Pose
* 擺設AprilTag於IPCAM可拍攝位置，紀錄ApriTag 2D點位到MySQL
* 架構圖

![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/part1.png)

### 程式細節
1. read_config.py 取得cameraIDs、apriltag_family
2. Vaidio_API.py GetStreamImage() 輸入cameraIDs，每個IPCAM即時拍照
3. 拍到符合apriltag_family的圖後使用DB_SQL.py CommitAprilTag()存取該AprilTag Corners 2D點位到DB

![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/flow_chart_1.png)


## Part2_CPL.py
* 連接UAV，於所有AprilTag拍攝並與對應IPCAM拍攝的2D點計算出IPCAM姿態，且存到MySQL
* 架構圖

![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/part2.png)
### 程式細節
1. ROS Launch得先連接上UAV。
2. read_config.py取得apriltag_family、apriltag_length、UAV_Camera_intrinsic
3. 拍攝過程找到與apriltag_family相符的AprilTag，DB_SQL.py函式SelectAprilTag()輸入tagID拿取apriltag corners 2D點位
4. 利用apriltag_length、UAV_Camera_intrinsic及apriltag corners 2D點位，以solvepnp計算出IPCAM Pose
5. DB_SQL.py CommitCameraPose()函式將IPCAM Pose寫入DB

![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/flow_chart_2.png)

### Part1、Part2 picture
![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/IPCAM_POSE_report.png)

## Vaidio Alert 設置
![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/Vaidio_alert_set.png)

## Part3_COL.py
* Vaidio Alert接收端
* 計算物件座標，寫入MySQL
* 下圖左為Vaidio回傳圖片，右為計算物件及座標

![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/Vaidio_alert_to_DB.png)
* 架構圖

![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/part3.png)
### 程式細節
1. read_config.py取得IPCAM_camera_intrinsic
2. 架設HTTP，接收Vaidio Alert，取得CameraName、SceneID
3. Vaidio_API.py GetImage()、ObjectDetect()函式輸入SceneID，得到圖片以及Object bounding box
4. DB_SQL.py SelectCameraPose()輸入CameraName得到IPCAM Pose
5. Object bounding box、物件大小、IPCAM Pose，solvepnp計算物件世界座標
6. DB_SQL.py CommitObjectCoordinate()函式，將物件世界座標寫入DB

![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/flow_chart_3.png)

## Part4_sift.py、Part4_stereo.py
### UAV定位
1. 透過WIFI與無人機連線
2. 訂閱無人機ROS Topic取得無人機之資訊
3. 執行程式，選擇Stereo or SIFT
* 計算後的物件座標存到DB
![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/UAV_localize2.png)
* 架構圖
![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/part4.png)
### 程式細節
1. 可以選擇要使用1. Stereo OR 2. SIFT
2. UAVObjectLocalization_.py專門計算物件座標
3. read_config.py取得UAV_left_eye_coordinate、Q_parameter()、SIFT_good_match_distance_threshold、Q_Array()
4. Vaidio_API.py connenct_vaidio_only()函式，拍攝過程中不停上傳圖片到Vaidio，並且回傳物件結果。此部份使用Thread執行。
5. Part4_stereo.py disparity計算部份使用Thread執行。
6. Part4_sift.py SIFT_Match計算部份使用Thread執行。
7. 針對物件框內深度進行物件座標計算。
8. DB_SQL.py CommitObjectCoordinate()，物件座標存到DB
![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/flow_chart_4.png)

## map_GUI.py

1. 於路徑底下放入室內地圖roommap.png
2. 編輯室內實際長寬
3. UAV初始點盡量設置於map左上方，以x軸為N，以y軸為E，初始計算IPCAM位姿
4. 開啟所有Alert接收
5. 或是啟動無人機計算物件座標
6. 讀取幾秒前DB資料並劃出人走過位置

![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/3dmap2d.png)
![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/3dmap2d_2.png)

## 技術細節
### IPCAM定位
1. 訂定座標系 (AprilTag座標系)
2. AprilTag到UAV相機座標系的旋轉及位移 (UAV拍攝時的UAV相機座標系)
3. UAV初始位置座標系(世界座標系)
4. 計算世界座標系中IPCAM 的旋轉及位移

![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/IPCAM_localize.png)
### Solvepnp
* 原世界坐標系中的點pi，經過相機旋轉位移後會得到新的相機坐標系並得到2D座標點ui
* 由原3D點座標與拍攝到的2D點座標對應，能得知坐標系的R,t，旋轉及位移。
![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/solvepnp.png)
* 數學計算公式

![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/solvepnp2.png)
* 清楚原物件多點3D世界座標，如AprilTag四個角點(設定中心為原點)
* 相機旋轉位移後拍攝到的AprilTag 四個角點2D點座標可以做對應
* 此時即可算出相機跟原世界座標的位移及旋轉
* IPCAM或UAV拍攝AprilTag得到的AprilTag 2D點位與確定好的AprilTag座標點對應，即可算出IPCAM及UAV的座標關係及旋轉。

### 固定相機位姿量測: seeker
![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/seeker_test.png)
### 固定相機位姿量測: m500
![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/m500_test.png)
### IPCAM Vaidio Alert(人頭定位)
* 發現有人頭或人體發出Vaidio Alert
* 依照輸入物件可能大小，並標定物件格的四個3D角點
* 物件框四個3D角點與圖片2D角點做Solvepnp，能算出IPCAM相機坐標系的人頭座標
* 再由IPCAM的世界座標姿態計算出人頭或人身的世界座標。
![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/head_localize.png)
### Stereo 物件座標
* Z = fx*B / (x - x’)
* (x - x’) = disparity
* X = baseline*(left_image_x-ox)/disparity
* Y = (fx*baseline*(left_image_y-oy))/(fy*disparity)

![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/stereo_localize.png)
![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/stereo_localize2.png)
### Stereo 物件座標(filter)
* MAD：絕對中位差
* 𝑀𝐴𝐷= 〖𝑚𝑒𝑑𝑖𝑎𝑛〗_𝑖(| 𝑋_𝑖− 〖𝑚𝑒𝑑𝑖𝑎𝑛〗_𝑗 (𝑋_𝑗) |)
* 離Bounding Box內的中間值很遠的會被濾掉(與中間值距離大於MAD)
* 剩餘取平均為物件座標
* UAV Pose回推物件世界座標

![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/stereo_filter.png)

### 無人機之物件定位結果(視差圖)
![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/disparity_test.png)
### SIFT 物件座標
* SIFT先取兩圖中相互匹配的點
* 再取左圖的物件框中的點找匹配點
* 匹配點計算disparity
* disparity算3D點
* 相同過濾方式，再取平均得到物件座標
* UAV Pose回推物件世界座標

![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/sift_localize.jpg)
![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/sift_localize2.jpg)
### 無人機之物件定位結果(SIFT視差圖)
![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/sift_test.png)
### 無人機深度計算時間花費(視差圖法)
* 主機規格: i7-8550 @1.8GHZ, 16GB RAM
* 每Frame總處理時間: 0.156秒/frame (樣本數22)
* Thread加速，每Frame總處理時間: 0.092秒/frame 
* 影像大小：640x480 gray

![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/disparity_time_cost.png)
### 無人機深度計算時間花費(SIFT特徵點法)
* 主機規格: i7-8550 @1.8GHZ, 16GB RAM
* 每Frame總處理時間: 0.197秒/frame (樣本數24)
* Thread加速，每Frame總處理時間: 0.143秒/frame 
* 影像大小：640x480 gray

![FLOW](https://github.com/frederickazion/MiVIP-Project/blob/main/Sys_DB_World_Coordinate_synchronous-main/github_img/sift_time_cost.png)
