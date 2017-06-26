#!/usr/bin/env python3

#_____________________________________________________________________________
#
# A very simple client for SOCKS5 (RFC 1928) proxy server
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
# TODO: something wrong with error/except, etct... handling, wrong place for closing socket?
# TODO: correction of sys.error number and handling
# TODO: check steps of SOCKS5 connection implementation for details of protocol specification, see section: Addressing


import socket
import string
import sys

from socks5 import *

Socks5_Protocol = Protocol()

# **********
# Config
# **********
proxy_host	= "127.0.0.1"
proxy_port	= 1080
proxy_addr	= (proxy_host, proxy_port)

target_host	= "127.0.0.1"
target_port	= 8888								# TODO: CAUSED BY BUG, THIS IS TEMPORARY HARDCODED in socks5.py!!!!!
target_addr	= (target_host,target_port)

# SOCKS5 - Hallo
VER 				= Socks5_Protocol.VER
NMETHODS 			= b'\x01'	# TODO: Further methods hast still to be written
METHODS				= Socks5_Protocol.METHOD_NOAUTH

# SOCKS5 - Connecting
CMD					= Socks5_Protocol.CMD_CONNECT
RSV					= Socks5_Protocol.RSV
ATYP				= Socks5_Protocol.ATYP_IPV4

# Message for Target Server
msg = "Hallo"
# **********

def main():
	print("[*] Starting Client ...")
	
	# *****
	# SOCKS5
	# *****
	Socks5_Client = Client()	
	Socks5_Client.init_socketToProxy(socket.AF_INET, socket.SOCK_STREAM, proxy_addr)

	try:
		print("[*] Start Initialization of SOCKS5 Connection")
		#s = 0
		
		print("[*] *** Hallo ***")	
		# Step 1: Send "Hallo" - VER+NMETHODS+METHODS
		#s = 1
		Socks5_Client.hallo_send(VER,NMETHODS,METHODS)		
		
		# Step 2: Receive answer "Hallo" from Proxy Server - VER+METHOD
		#s = 2
		Socks5_Client.hallo_recv()
		
		print("[*] *** Connecting ***")	
		# Step 3: Send request details - VER+CMD+RSV+ATYP+DST.ADDR+DST.PORT
		#s = 3
		# TODO: Depending of atyp, generating of valid (DST_ADDR,DST_PORT) format
		DST_ADDR			= socket.inet_aton(target_host)
		DST_PORT			= str(target_port).encode()				# TODO: Bug for target_port: byte <-> string <-> int switching!!!!
		Socks5_Client.connect_send(VER,CMD,RSV,ATYP,DST_ADDR,DST_PORT)
				
		# Step 4: Receive request details from proxy - VER+REP+RSV+ATYP+DST.ADDR+DST.PORT
		#s = 4
		Socks5_Client.connect_recv()
		print("[*] *** Connecting: Finished ***")
			
		# *****
		# Communication with Target Server
		# *****
		print("[*] *** Start Communication With Target Server ***")
		
		# Send Hallo
		Socks5_Client.sockToProxy.sendall(msg.encode())		
		print("[*] Send Greeting To Target Server ... Done")

		# Receiving Data
		buf_res	= 1024
		data = Socks5_Client.sockToProxy.recv(buf_res)
		# TODO: Check if the receiving msg is valid, at all! (No empty string!)
		
		if data:
			print("[*] Received Message from Target Server")
			rp_msg = data.decode()
			print("\t\t=> " + rp_msg)
		else:
			print("[*] Received No Valid Data from Target Server")
			sys.exit(2)	# Error number?
		
		print("[*] Shutdown Client ...")
		#Socks5Client.sockToProxy.close()
				
	except Exception as e:		
		print("[*] Unable To Communicate With Proxy Server") 
		sys.exit(2)	# Error number?
	finally:
		# Close socket 
		Socks5Client.sockToProxy.close()


if __name__=='__main__':
	try:
		main()
	except KeyboardInterrupt:
		print("\n[*] User Requested An Interrupt")
		print("[*] Application Exiting ...")
		sys.exit()	# Error number?
	except Exception as e:
		# TODO: Something wrong with exeption/error/sys.error handling. This message shut not appear after shutting down of client
		print("[*] An Unexpected Error occured.")
		sys.exit(2)	# Error number?

