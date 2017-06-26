#!/usr/bin/env python3

#_____________________________________________________________________________
#
# A very simple proxy for SOCKS5 (RFC 1928) proxy server
# Only plaintext analysis. No encryption, etc. ...
#
# Author:   Samdney  <contact@carolin-zoebelein.de>   
#			D4A7 35E8 D47F 801F 2CF6 2BA7 927A FD3C DE47 E13B 
# License:  See LICENSE for licensing information
#_____________________________________________________________________________

# TODO: configfile/argparsing
# TODO: logging
# TODO: bufferhandling is very bad! A lot of bugs! Values have NO fixed size!
# TODO: connections run in troubles if data > buffer_size
# TODO: buffer sizes
# TODO: correction of sys.error number and handling
# TODO: check steps of SOCKS5 connection implementation for details of protocol specification, see section: Addressing

import socket
import string
import sys

from socks5 import *
from myproxyfilter import *

Socks5_Protocol = Protocol()

# **********
# Config
# **********
proxy_host	= "127.0.0.1"
proxy_port	= 1080
proxy_addr	= (proxy_host, proxy_port)

max_conn 	= 5

# SOCKS5 - Hallo
VER 				= Socks5_Protocol.VER
METHOD				= Socks5_Protocol.METHOD_NOAUTH
# **********

class ProxyToServer():

	def __init__(self):
		self.msg_from_target	= ""
		self.sockToTarget 		= None
		self.data_client		= None

	def ConnectToTargetServer(self,target_addr):
		# Socket Init
		try:
			sockToTarget = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sockToTarget.connect(target_addr)
			self.sockToTarget = sockToTarget
			print("[*] Initializing Sockets To Target Server... Done")
		except Exception as e:
			print("[*] Unable To Initialize Socket To Target Server")
			sys.exit(2)	# Error number?

	def recv_data(self,conn):
		buf_client		= 1024
		self.data_client 	= conn.recv(buf_client)

	# TODO: This Should be parted in SendDataToTargetServer(...) and ReceiveDataFromTargetServer(...)
	def CommunicationWithTargetServer(self,msg_for_target):
		buffer_size = 1024
		try:
			# Forward msg from Client to Target Server
			self.sockToTarget.sendall(msg_for_target.encode())
			print("[*] Forward Message from Client to Target Server ... Done")
			
			# Receive response msg target_rp_msg from Target Server
			data_target = self.sockToTarget.recv(buffer_size)
			if data_target:
				print("[*] Received Message from Target Server")
				self.msg_from_target = data_target.decode()
				#print(data_target.decode())
			else:
				print("[*] Received No Valid Data from Target Server")
				sys.exit(2)	# Error number?
			
		except Exception as e:
			print("[*] Unable To Communicate with Target Server")
			sys.exit(2)	# Error number?
		#finally:
			# Close socket 
			#sockToTarget.close()
			#print("SOCK")
	
	def close(self):
		self.sockToTarget.close()

def main():
	print("[*] Starting Proxy Server ...")

	# *****
	# SOCKS5
	# *****
	Socks5_Proxy = Proxy()
	Socks5_Proxy.init_socketToClient(socket.AF_INET, socket.SOCK_STREAM, proxy_addr,max_conn)
	
	while True:	
		try:
			conn, client_addr = Socks5_Proxy.sockToClient.accept()
			
			print("[*] Start Initialization of SOCKS5 Connection To Client")
			#s = 0
			
			print("[*] *** Hallo ***")
			# Step 1: Receive "Hallo" from Client - VER+NMETHODS+METHODS
			#s = 1
			Socks5_Proxy.hallo_recv(conn)
			
			# Step 2: Send answer Hallo to Client - VER+METHOD
			#s = 2
			Socks5_Proxy.hallo_send(VER,METHOD,conn)
			
			print("[*] *** Connecting ***")	
			# Step 3: Receive request details from Client - VER+CMD+RSV+ATYP+DST.ADDR+DST.PORT
			#s = 3
			Socks5_Proxy.connect_recv(conn)
			
			if Socks5_Proxy.cmd == Socks5_Protocol.CMD_CONNECT[0]:
				#CONNECT
				print("[*] Step 3: Start To Connect To Target Server ...")
				
				target_addr = (Socks5_Proxy.target_host,Socks5_Proxy.target_port)

				ProxyTargetConn = ProxyToServer()
				ProxyTargetConn.ConnectToTargetServer(target_addr)
				
				# Step 4: Send reply back to client - VER+REP+RSV+ATYP+BND.ADDR+BND.PORT
				#s = 4
				Socks5_Proxy.connect_reply(conn)
				print("[*] Initializing Socket To Target Server... Done")

				print("[*] *** Connecting: Finished ***")
								
				# *****
				# Communication with Target Server
				# *****
				print("[*] *** Start Communication With Target Server ***")
				
				ProxyTargetConn.recv_data(conn)
				if ProxyTargetConn.data_client:
					msg_for_target = ProxyTargetConn.data_client.decode()
					ProxyTargetConn.CommunicationWithTargetServer(msg_for_target)
					
					print("[*] Forwarding Response From Target Server to Client ...")
								
					rp_msg_from_target = ProxyTargetConn.msg_from_target
					print("\t\t=> " + rp_msg_from_target)
										
					# ********************
					# MyProxyFilter
					# ********************
					# Choose Kind of Filter
					print("[*] Proxyfilter")
					filter_switch 			= 1			# 0: Filter of, 1: Filter on - simple_switch, 2: Filter on - lingu_switch (not implemented until now)
					myfilter 				= gender_filter()
					
					myfilter.change_msg(filter_switch,rp_msg_from_target)
					
					New_rp_msg_from_target 	= myfilter.msg_new
					print("\t\t=> " + New_rp_msg_from_target)
					# ********************
					conn.sendall(New_rp_msg_from_target.encode())
					print("[*] ... Done")
				else:
					print("[*] Received No Valid Data from Client")
					sys.exit(2)	# Error number?	
				
			#if Socks5_Proxy.cmd == str(Socks5_Protocol.CMD_BIND):
				# BIND
				# TODO

			#if Socks5_Proxy.cmd == str(Socks5_Protocol.CMD_UDP):
				# UDP ASSOCIATE
				# TODO
			
		except Exception as e:
			print("[*] Unable To Communicate With Client")
			sys.exit(2)	# Error number?		

	Socks5_Proxy.sockToClient.close()
	ProxyTargetConn.close()


if __name__=='__main__':
	try:
		main()
	except KeyboardInterrupt:
		print("\n[*] User Requested An Interrupt")
		print("[*] Application Exiting ...")
		sys.exit()	# Error number?
	except Exception as e:
		print("[*] An Unexpected Error occured.")
		sys.exit(2)	# Error number?

