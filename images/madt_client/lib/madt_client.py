import zmq
import os
import json
import time

time0 = time.time()

class MADT_Client():
	def __init__(self, socket_name):
		self.madt_ctx = zmq.Context()
		self.madt_sock = self.madt_ctx.socket(zmq.PUSH)
		#self.madt_sock.bind('ipc:///lab/lab.sock')
		self.countOfMessages = 0
		self.socket_name = socket_name
		self.path = "/lab/"+ socket_name +"/fallback_sock_" + os.environ['HOSTNAME'] +  ".txt"
		try:
			os.remove(self.path)
		except FileNotFoundError:
			pass
		if socket_name == 'packets':
			self.send_fallback = self.send_packets_data_fallback
		else:
			self.send_fallback = self.send_msg_fallback
		

	def send(self, status, log, traffic):
		print('sending', status, log, traffic)
		self.madt_sock.send_json({
	        'hostname': os.environ['HOSTNAME'],
	        'traffic': traffic,
	        'status': status,
	        'log': log })
	
	def send_msg_fallback(self, status, log, traffic):
		if self.countOfMessages > 1000: 
			try:
				os.remove(self.path)
				self.countOfMessages = 0
			except FileNotFoundError:
				pass

		try:
			f = open(self.path, "a")
			f.write(str(self.countOfMessages) + '&' + json.dumps({
				'hostname': os.environ['HOSTNAME'],
				'traffic': traffic,
				'status': status,
				'log': log }) + '#')
			f.close()
			self.countOfMessages += 1
		except Exception as e:
			pass

	def send_packets_data_fallback(self, source, destination, ttl, checkSum):
		if self.countOfMessages > 100000: 
			try:
				os.remove(self.path)
				self.countOfMessages = 0
			except FileNotFoundError:
				pass

		try:
			f = open(self.path, "a")
			f.write(str(self.countOfMessages) + '&' + json.dumps({
				'hostname': os.environ['HOSTNAME'],
				'source': source,
				'destination': destination,
				'checkSum': checkSum,
				'ttl': ttl,
				'time': int(((time.time() - time0) % 10**5) * 10**12),
				}) + '#')
			f.close()
			self.countOfMessages += 1
		except Exception as e:
			pass


