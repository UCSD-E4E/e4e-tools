#!/usr/bin/env python

import serial
import struct

def get_checksum(data):
	checksum_byte1 = 0
	checksum_byte2 = 0
	for i in range(len(data)):
		checksum_byte1 += ord(data[i])
		checksum_byte2 += checksum_byte1
	return chr(checksum_byte1 & 0xFF) + chr(checksum_byte2 & 0xFF)

def get_packet(descriptor_set, field_descriptor, field_data):
	try:
		payload_len = chr(len(field_data) + 0x2)
	except:
		payload_len = chr(0x2)
	cmd = ''
	cmd += chr(0x75) # 'u'
	cmd += chr(0x65) # 'e'
	cmd += chr(descriptor_set)
	cmd += payload_len
	cmd += payload_len
	cmd += chr(field_descriptor)
	if field_data is not None:
		cmd += field_data
	cmd += get_checksum(cmd)
	return cmd

s = serial.Serial('/dev/ttyACM0')

while True:
	# sync to first byte
	char = s.read()
	if ord(char) == 0x75:
		# sync to 2nd byte
		char = s.read()
		if ord(char) == 0x65:
			# read descriptor set byte
			descriptor_set = s.read()
			payload_length = s.read()
			field_length = s.read()
			field_descriptor = s.read()

			# FIXME handle multiple reply in 1 packet
			if payload_length == field_length:
				data = ''
				for i in range(ord(payload_length)-2):
					data += s.read()
				checksum_byte1 = s.read()
				checksum_byte2 = s.read()

				# verify checksum
				if get_checksum('ue' + descriptor_set + payload_length + field_length + field_descriptor + data) == checksum_byte1 + checksum_byte2:

					# base command set
					if ord(descriptor_set) == 0x01:

						# ACK/NACK
						if ord(field_descriptor) == 0xF1:
							if ord(data[1]) == 0x00:
								print "0x%x: ACK"%ord(data[0])
							else:
								print "0x%x: NACK"%ord(data[0])

					# AHRS data set
					elif ord(descriptor_set) == 0x80:

						# euler angles
						if ord(field_descriptor) == 0x0C:
							roll = struct.unpack('f', ''.join(reversed(data[0:4])))[0]
							pitch = struct.unpack('f', ''.join(reversed(data[4:8])))[0]
							yaw = struct.unpack('f', ''.join(reversed(data[8:12])))[0]
							print roll, pitch, yaw

						# quaternion
						elif ord(field_descriptor) == 0x0A:
							q0 = struct.unpack('f', ''.join(reversed(data[0:4])))[0]
							q1 = struct.unpack('f', ''.join(reversed(data[4:8])))[0]
							q2 = struct.unpack('f', ''.join(reversed(data[8:12])))[0]
							q3 = struct.unpack('f', ''.join(reversed(data[12:16])))[0]
							print("%f %f %f %f" % (q0, q1, q2, q3))


						# wrapped ahrs
						elif ord(field_descriptor) == 0x82:
							print 'wrapped ahrs'

					# 3DM command set
					elif ord(descriptor_set) == 0x0C:
						if ord(field_descriptor) == 0xF1:
							if ord(data[1]) == 0x00:
								print "0x%x: ACK"%ord(data[0])
							else:
								print "0x%x: NACK"%ord(data[0])

					# GPS data set
					elif ord(descriptor_set) == 0x81:
						print 'GPS!'
			# payload_length != field_length
			else:
				print 'uneven payload lengths %x:%x'%(ord(payload_length), ord(field_length))
