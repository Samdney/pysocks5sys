#!/usr/bin/env python3
  
#_____________________________________________________________________________
#
# A very simple target server for SOCKS5 (RFC 1928) proxy server for switching the gender in arbitrary natural text
# Only plaintext analysis. No encryption, etc. ... => plaintext
#
# Author:   Samdney  <contact@carolin-zoebelein.de>   D4A7 35E8 D47F 801F 2CF6 2BA7 927A FD3C DE47 E13B 
# License:  See LICENSE for licensing information
#_____________________________________________________________________________

# TODO: configfile/argparsing
# TODO: logging
# TODO: bufferhandling is very bad! A lot of bugs! Values have NO fixed size!
# TODO: connections run in troubles if data > buffer_size

import socket
import string
import sys

# **********
# Config
# **********
target_host	= "127.0.0.1"
target_port	= 8888
target_addr	= (target_host,target_port)

buffer_size	= 1024
max_conn 	= 5

# Respond message for client
rp_msg				= "She is a nice girl."
# **********

def main():
	print("[*] Starting Target Server ...")

	# Socket Init
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind(target_addr)
		sock.listen(max_conn)
		print("[*] Initializing Sockets ... Done")
		print("[*] Sockets Binded Successfully ... Done")
		print("[*] Server Started Successfully [ %d ] ... Done" % (target_port))
	except Exception as e:
		print("[*] Unable To Initialize Socket")
		sys.exit(2)	# Error number?

	# Communication	
	while True:
		try:
			conn, client_addr = sock.accept()
			print("[*] Connected Successfully With Client ...")

			data = conn.recv(buffer_size)

			if data:
				print("[*] Received Data From Client ...")
				print("\t\t=> " + data.decode())

				conn.sendall(rp_msg.encode())
				print("[*] Send Response to Client ...")
				print("\t\t=> " + rp_msg)			

			else:
				print("[*] Received No Valid Data from Client")
				break

		except Exception as e:
			print("[*] Unable To Communicate with Client")
			sys.exit(2)	# Error number?

	sock.close()

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

