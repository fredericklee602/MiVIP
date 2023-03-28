import pymysql.cursors
import pandas as pd
import numpy as np
from read_config import config_
import random
import time
class DB_connect():
	def __init__(self):
		self.CONFIG = config_()
		self.host = self.CONFIG.DB_host
		self.user = self.CONFIG.DB_user
		self.password = self.CONFIG.DB_password
		self.database = self.CONFIG.DB_database
	def ConnectTest(self):
		conn = False
		try:
			connection = pymysql.connect(host=self.host,
										user=self.user,
										password=self.password,
										database=self.database,
										cursorclass=pymysql.cursors.DictCursor)
			print("Successfully connected to the database [{0}].".format(self.database))
			conn = True
		except:
			print("Error when Connecting to DB. Please confirm the database connection status.")
		return conn
	def CommitAprilTag(self, CameraName, CameraID, AprilTag,tags_number):
		# Connect to the database
		connection = pymysql.connect(host=self.host,
				                     user=self.user,
				                     password=self.password,
				                     database=self.database,
				                     cursorclass=pymysql.cursors.DictCursor)
		# AprilTag data processing
		AprilTag = AprilTag.replace("   ",",").replace("  ",",").replace(" ",",").replace("\n","")
		print("AprilTag",AprilTag)
		with connection:
			with connection.cursor() as cursor:
				# Create a new record
				sql = "SELECT * FROM AzionDB.ipcam  WHERE CameraName='{0}';".format(CameraName)
				cursor.execute(sql)
				connection.commit()
				data = cursor.fetchall()
				if len(data)>0:
					sql = "UPDATE `ipcam` SET  `AprilTagCorner`='{0}',`CameraID` = {1}, `CameraPose` = '{2}', `TagID`= {3} WHERE CameraName='{4}';".format(AprilTag,CameraID,None, tags_number,CameraName)
					cursor.execute(sql)
					connection.commit()
					print("UPDATE AprilTag CameraName : ".format(CameraName))
				else:
					sql = "INSERT INTO `ipcam` (`CameraName`,`CameraID`, `CameraPose`,`AprilTagCorner`,`TagID`) VALUES('{0}',{1},'{2}','{3}',{4});".format(CameraName, CameraID, '', AprilTag,tags_number)
					cursor.execute(sql)
					connection.commit()
					print("INSERT AprilTag CameraName : ".format(CameraName))
	def SelectAprilTag(self,tags_number):
		# Connect to the database
		connection = pymysql.connect(host=self.host,
				                     user=self.user,
				                     password=self.password,
				                     database=self.database,
				                     cursorclass=pymysql.cursors.DictCursor)
		with connection:
			with connection.cursor() as cursor:
				sql = "SELECT * FROM AzionDB.ipcam  WHERE TagID={0};".format(tags_number)
				cursor.execute(sql)
				connection.commit()
				data = cursor.fetchall()
				if len(data)>0:
					apriltag = np.array(eval(data[0]["AprilTagCorner"]))
					if len(apriltag)==0:
						print("DB does not have AprilTag number {0}").format(tags_number)
				else:
					apriltag = None
					print("DB does not have AprilTag number {0}").format(tags_number)
		return apriltag	
	def CommitCameraPose(self, CameraName, TagID, CameraPose):
		# Connect to the database
		connection = pymysql.connect(host=self.host,
				                     user=self.user,
				                     password=self.password,
				                     database=self.database,
				                     cursorclass=pymysql.cursors.DictCursor)

		with connection:
			with connection.cursor() as cursor:
				# Create a new record
				sql = "SELECT * FROM AzionDB.ipcam  WHERE TagID={0};".format(TagID)
				cursor.execute(sql)
				connection.commit()
				data = cursor.fetchall()
				if len(data)>0:
					sql = "UPDATE `ipcam` SET  `CameraPose`='{0}' WHERE TagID={1};".format(CameraPose,TagID)
					cursor.execute(sql)
					connection.commit()
					print("UPDATE CameraPose CameraName : ".format(CameraName))
				else:
					sql = "INSERT INTO `ipcam` (`CameraName`,`TagID`,`CameraPose`) VALUES('{0}',{1},'{2}');".format(CameraName, TagID, CameraPose)
					cursor.execute(sql)
					connection.commit()
					print("INSERT CameraPose CameraName : ".format(CameraName))
	def SelectCameraPose(self, CAM_NAME):
		# Connect to the database
		connection = pymysql.connect(host=self.host,
				                     user=self.user,
				                     password=self.password,
				                     database=self.database,
				                     cursorclass=pymysql.cursors.DictCursor)
		with connection:
			with connection.cursor() as cursor:
				# Create a new record
				sql = "SELECT * FROM AzionDB.ipcam WHERE CameraName='{0}';".format(CAM_NAME)
				cursor.execute(sql)
				connection.commit()
				data = cursor.fetchall()
				if len(data)>0:
					data_list = pd.DataFrame(data)["CameraPose"][0].split("|||")
					rvec = eval(data_list[0].replace("\n",","))
					tvec = eval(data_list[1].replace("\n",","))
					rvec = np.array(rvec)
					tvec = np.array(tvec)
		return rvec, tvec
	def CommitObjectCoordinate(self,sceneID, objectname, coordinate):
		# Connect to the database
		connection = pymysql.connect(host=self.host,
				                     user=self.user,
				                     password=self.password,
				                     database=self.database,
				                     cursorclass=pymysql.cursors.DictCursor)

		with connection:
			with connection.cursor() as cursor:
				sql = "INSERT INTO `object_coordinate` (`sceneID`,`objectname`,`coordinate`,`date`) VALUES('{0}','{1}','{2}',NOW());".format(sceneID, objectname, coordinate)
				cursor.execute(sql)
				connection.commit()
				print("INSERT sceneID {0} objectname : {1}".format(sceneID, objectname))
	
	def SelectNewCoordinate(self):
		# Connect to the database
		connection = pymysql.connect(host=self.host,
				                     user=self.user,
				                     password=self.password,
				                     database=self.database,
				                     cursorclass=pymysql.cursors.DictCursor)
		with connection:
			with connection.cursor() as cursor:
				# Create a new record
				sql = "SELECT * FROM AzionDB.object_coordinate order by date Desc LIMIT 0 , 1;"
				cursor.execute(sql)
				# connection.commit()
				data = cursor.fetchall()
				newestsceneID = data[0]["sceneID"]
				sqlselect = "SELECT * FROM AzionDB.object_coordinate WHERE sceneID = {0} AND date > DATE_SUB(NOW(),INTERVAL  2 second)".format(newestsceneID)
				cursor.execute(sqlselect)
				# connection.commit()
				data = cursor.fetchall()
				return data
	def SelectTest(self):
		# Connect to the database
		connection = pymysql.connect(host=self.host,
				                     user=self.user,
				                     password=self.password,
				                     database=self.database,
				                     cursorclass=pymysql.cursors.DictCursor)
		with connection:
			with connection.cursor() as cursor:
				# Create a new record
				sql = "SELECT * FROM AzionDB.object_coordinate;"
				cursor.execute(sql)
				data = cursor.fetchall()
				df = pd.DataFrame(data)
				return df
	def CommitTest(self):
		while True:
			df = pd.read_csv("test.csv")
			last_sceneID = 0
			for i,raw in df.iterrows():
				true_sceneID, objectname, coordinate = raw["sceneID"], raw["objectname"], raw["coordinate"]
				if last_sceneID!=true_sceneID:
					time.sleep(1)
					last_sceneID = true_sceneID
				sceneID = true_sceneID
				diffx = random.randint(-20,20)
				diffy = random.randint(-20,20)
				coordinate = eval(coordinate)
				coordinate[0][0] = coordinate[0][0] + diffx
				coordinate[1][0] = coordinate[1][0] + diffy
				if objectname=="head":
					print(str(coordinate))
					self.CommitObjectCoordinate(sceneID, objectname, str(coordinate))
if __name__ == '__main__':
	DBCONN = DB_connect()
	DBCONN.CommitTest()