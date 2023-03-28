import Part1_CTATS
import Part2_CPL
import Part3_COL
import Part4_stereo
import Part4_sift
import time
from DB_SQL import DB_connect
import sys
from voxl_control import Check_UAV
from configGUI import ExecuteGUI
from chessboard_GUI import ExecutechessGUI
from Vaidio_API import API
import time
if __name__ == '__main__':
    # Config GUI
    ExecGUI = ExecuteGUI()

    # Chessboard GUI
    Execute_chessGUI = ExecutechessGUI()
    # Check DB
    print("\n<Try to Connect DB>")
    time.sleep(2)
    DBCONN = DB_connect()
    DB_test = DBCONN.ConnectTest()
    
    # Check Vaidio
    print("\n<Try to Connect Vaidio>")
    time.sleep(2)
    api = API()
    Vaidioconn = api.VaidioConnectTest()
    # Check UAV
    #print("\n<Connect UAV>")
    # Check = Check_UAV()
    # UAV_conn = Check.check()
    while True:
        input_name = input("\n\n\nplease enter method number: \n 00. ExecuteConfigGUI \n 01. ExecuteChessboardGUI \n 1. CamTakingAprilTagShot \n 2. CamPoseLocalization \n 3. CamObjectLocalization \n 4. UAVObjectLocalization \n 5. CloseALL \n ")
        if input_name == "00":
            ExecGUI.exec()
        if input_name == "01":
            Execute_chessGUI.exec()
        if input_name=="1":
            CTATS = Part1_CTATS.CamTakingAprilTagShot()
            CTATS.CommitDB()
        if input_name=="2":
            CPL = Part2_CPL.CamPoseLocalization()
            CPL.start()
        if input_name=="3":
            COL = Part3_COL.CamObjectLocalization()
            COL.run()
        if input_name=="4":
            while True:
                number = input("please enter UAVObjectLocalization method number: \n 1. Stereo \n 2. SIFT \n o. Back to previous leverl.")
                if number == "1":
                    UAVOL = Part4_stereo.UAVObjectLocalization()
                    UAVOL.UAVision()
                if number == "2":
                    UAVOL = Part4_sift.UAVObjectLocalization()
                    UAVOL.UAVision()
                if number == "o":
                    break
                else:
                    print("Error input.  \n Please enter number 1, 2 or input word 'o' to back to previous leverl. \n ")
                    continue
        if input_name=="5":
            sys.exit()
        else:
            print("Error input. \n Please enter number 00, 01, 2, 3, 4, 5")
            continue

            

    