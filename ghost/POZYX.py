
from time import sleep,time

from pypozyx.definitions.bitmasks import POZYX_INT_MASK_IMU
from pypozyx import *

class Pozyx_Obj(object):
	"""Continuously calls the Pozyx positioning function and prints its position."""

	def __init__(self, pozyx, anchors, algorithm=POZYX_POS_ALG_UWB_ONLY, dimension=POZYX_3D, height=1000, remote_id=None):
		self.pozyx = pozyx

		self.anchors = anchors
		self.algorithm = algorithm
		self.dimension = dimension
		self.height = height
		self.remote_id = remote_id

	def setup(self):
		"""Sets up the Pozyx for positioning by calibrating its anchor list."""
		print("------------POZYX POSITIONING V1.1 -------------")
		print("NOTES: ")
		print("- No parameters required.")
		print()
		print("- System will auto start configuration")
		print()
		print("- System will auto start positioning")
		print("------------POZYX POSITIONING V1.1 --------------")
		print()
		print("START Ranging: ")
		self.pozyx.setUWBSettings([4,0,2,0x0C,15.0])
		self.pozyx.setPositionFilter(FILTER_TYPE_MOVINGAVERAGE,2)
		self.pozyx.clearDevices(self.remote_id)
		self.setAnchorsManual()
		sleep(1)
		
		#Configuration for Orientation
		self.current_time = time()

	def loop(self):
		"""Performs positioning and displays/exports the results."""
		position = Coordinates()
		status = self.pozyx.doPositioning(
			position, self.dimension, self.height, self.algorithm, remote_id=self.remote_id)
		if status == POZYX_SUCCESS:
			self.printPublishPosition(position)
		else:
			self.printPublishErrorCode("positioning")
			
		sensor_data = SensorData()
		calibration_status = SingleRegister()
		if self.remote_id is not None or self.pozyx.checkForFlag(POZYX_INT_MASK_IMU, 0.01) == POZYX_SUCCESS:
			status = self.pozyx.getAllSensorData(sensor_data, self.remote_id)
			status &= self.pozyx.getCalibrationStatus(calibration_status, self.remote_id)
			if status == POZYX_SUCCESS:
				self.publishSensorData(sensor_data, calibration_status)
			
		
		magnetic = {'x':sensor_data.magnetic[0],'y':sensor_data.magnetic[1],'z':sensor_data.magnetic[2],'A':sensor_data.euler_angles[0]}
		xyz = {'x':position[0],'y':position[1],'z':position[2]}
		return (xyz,magnetic)

	def publishSensorData(self, sensor_data, calibration_status):
		"""Makes the OSC sensor data package and publishes it"""
		print(sensor_data.magnetic)
				
	def printPublishPosition(self, position):
		"""Prints the Pozyx's position and possibly sends it as a OSC packet"""
		network_id = self.remote_id
		if network_id is None:
			network_id = 0
		print("POS ID {}, x(mm): {pos.x} y(mm): {pos.y} z(mm): {pos.z}".format(
			"0x%0.4x" % network_id, pos=position))

	def printPublishErrorCode(self, operation):
		"""Prints the Pozyx's error and possibly sends it as a OSC packet"""
		error_code = SingleRegister()
		network_id = self.remote_id
		if network_id is None:
			self.pozyx.getErrorCode(error_code)
			print("ERROR %s, local error code %s" % (operation, str(error_code)))
			return
		status = self.pozyx.getErrorCode(error_code, self.remote_id)
		if status == POZYX_SUCCESS:
			print("ERROR %s on ID %s, error code %s" %
				  (operation, "0x%0.4x" % network_id, str(error_code)))
		else:
			self.pozyx.getErrorCode(error_code)
			print("ERROR %s, couldn't retrieve remote error code, local error code %s" %
				  (operation, str(error_code)))
			# should only happen when not being able to communicate with a remote Pozyx.

	def setAnchorsManual(self):
		"""Adds the manually measured anchors to the Pozyx's device list one for one."""
		status = self.pozyx.clearDevices(self.remote_id)
		for anchor in self.anchors:
			status &= self.pozyx.addDevice(anchor, self.remote_id)
		if len(self.anchors) > 4:
			status &= self.pozyx.setSelectionOfAnchors(POZYX_ANCHOR_SEL_AUTO, len(self.anchors))
		return status

	def printPublishConfigurationResult(self):
		"""Prints and potentially publishes the anchor configuration result in a human-readable way."""
		list_size = SingleRegister()

		status = self.pozyx.getDeviceListSize(list_size, self.remote_id)
		print("List size: {0}".format(list_size[0]))
		if list_size[0] != len(self.anchors):
			self.printPublishErrorCode("configuration")
			return
		device_list = DeviceList(list_size=list_size[0])
		status = self.pozyx.getDeviceIds(device_list, self.remote_id)
		print("Calibration result:")
		print("Anchors found: {0}".format(list_size[0]))
		print("Anchor IDs: ", device_list)

		for i in range(list_size[0]):
			anchor_coordinates = Coordinates()
			status = self.pozyx.getDeviceCoordinates(
				device_list[i], anchor_coordinates, self.remote_id)
			print("ANCHOR,0x%0.4x, %s" % (device_list[i], str(anchor_coordinates)))

	def printPublishAnchorConfiguration(self):
		"""Prints and potentially publishes the anchor configuration"""
		for anchor in self.anchors:
			print("ANCHOR,0x%0.4x,%s" % (anchor.network_id, str(anchor.coordinates)))