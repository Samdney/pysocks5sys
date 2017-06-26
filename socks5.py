#!/usr/bin/env python3
  
#_____________________________________________________________________________
#
# socks5 protocol
#
# Author:   Samdney  <contact@carolin-zoebelein.de>
# D4A7 35E8 D47F 801F 2CF6 2BA7 927A FD3C DE47 E13B 
# License:  See LICENSE for licensing information
#_____________________________________________________________________________

"""
***Summary: SOCKS Protocol Version 5 - rfc1928 - (For TCP-based clients only)***
	(From: https://tools.ietf.org/html/rfc1928)

3.  Procedure for TCP-based clients
=> 	TCP-based client opens a TCP connection to the appropiate SOCKS port on the
	SOCKS server 
=>	SOCKS service conventionally located on TCP port 1080
=> 	If the client's connection request succeeds:
		=> Client enters a negotiation for the authentication method to be used,
		authenticates with the chosen method, then sends a relay request.
		=> SOCKS server: Establishes the appropriate connection or denies it. 

	[Notes-Diagrams:
	- Decimal numbers == length of the correspondending field in octets
	- 'Variable' == corresponding field has a variable length defined either by an
   		associated (one or two octet) length field, or by a data type field]

	1. Client to Server:
	 			   +----+----------+----------+
                   |VER | NMETHODS | METHODS  |
                   +----+----------+----------+
                   | 1  |    1     | 1 to 255 |
                   +----+----------+----------+
	VER = 0x05	Protocol version
	
	NMETHODS	Number of method identifier octets that
   	appear in the METHODS field

	2. Server to Client: METHOD selection message
                         +----+--------+
                         |VER | METHOD |
                         +----+--------+
                         | 1  |   1    |
                         +----+--------+
	Server select one method, given in METHODS and sends selection message.
	
	Values for METHOD:
	=> 0x00 NO AUTHENTICATION REQUIRED
    => 0x01 GSSAPI
    => 0x02 USERNAME/PASSWORD
    => 0x03 to X'7F' IANA ASSIGNED
    => 0x80 to X'FE' RESERVED FOR PRIVATE METHODS
    => 0xFF NO ACCEPTABLE METHODS => Client must close the connection

   The client and server then enter a method-specific sub-negotiation.

   Compliant implementations MUST support GSSAPI and SHOULD support
   USERNAME/PASSWORD authentication methods.

4.  Requests
=>	Client sends request details  
=> 	If negotiated method includes encapsulation...
	=> These requests MUST be encapsulated in the method-
   dependent encapsulation.

	3. Client to Server: sends SOCKS request

        +----+-----+-------+------+----------+----------+
        |VER | CMD |  RSV  | ATYP | DST.ADDR | DST.PORT |
        +----+-----+-------+------+----------+----------+
        | 1  |  1  | X'00' |  1   | Variable |    2     |
        +----+-----+-------+------+----------+----------+

	VER	= 0x05	Protocol version	

    CMD
	=> CONNECT			= 0x01
    => BIND 			= 0x02
	=> UDP ASSOCIATE 	= 0x03
    => RSV    			RESERVED
    
	ATYP   address type of following address
    => IP V4 address	= 0x01
    => DOMAINNAME 		= 0x03
    => IP V6 address	= 0x04
    => DST.ADDR       	desired destination address
	=> DST.PORT 		desired destination port in network octet order
    
	=> SOCKS server evaluate request, and return one or more reply messages, as
   		appropriate for the request type.

5.  Addressing
=>	In an address field (DST.ADDR, BND.ADDR), the ATYP field specifies
   the type of address contained within the field:

		=> 0x01	= version-4 IP address, with a length of 4 octets
		=> 0x03	= a fully-qualified domain name, first octet of the address field 
			contains the number of octets of name that follow, there is no terminating 
			NUL octet.
		=> 0x04	= version-6 IP address, with a length of 16 octets.

6.  Replies
=>	Server evaluates the request, and returns a reply formed as follows:

        +----+-----+-------+------+----------+----------+
        |VER | REP |  RSV  | ATYP | BND.ADDR | BND.PORT |
        +----+-----+-------+------+----------+----------+
        | 1  |  1  | X'00' |  1   | Variable |    2     |
        +----+-----+-------+------+----------+----------+

  	VER	= 0x05	Protocol version

	REP    		Reply field:
	=> 0x00		succeeded
    => 0x01 	general SOCKS server failure
    => 0x02 	connection not allowed by ruleset
    => 0x03 	Network unreachable
    => 0x04 	Host unreachable
    => 0x05 	Connection refused
    => 0x06 	TTL expired
    => 0x07 	Command not supported
    => 0x08 	Address type not supported
    => 0x09 	to X'FF' unassigned
    => RSV    	RESERVED
    => ATYP   	address type of following address

	=> IP V4 address	= 0x01
    => DOMAINNAME		= 0x03
    => IP V6 address	= 0x04
    => BND.ADDR       	server bound address
    => BND.PORT       	server bound port in network octet order

   Fields marked RESERVED (RSV) must be set to X'00'.

   If the chosen method includes encapsulation for purposes of
   authentication, integrity and/or confidentiality, the replies are
   encapsulated in the method-dependent encapsulation.

=> CONNECT
	=> Reply to CONNECT, BND.PORT contains
		=> port number that the server assigned to connect to the target host
	=> BND.ADDR containts: 
		=> the associated IP address. 

  => It is expected that the SOCKS server will use DST.ADDR and DST.PORT, and the
   client-side source address and port in evaluating the CONNECT request.

=> BIND
	=> Used in protocols which require the client to accept connections from
	 the server, like FTP.
		=> uses the primary client-to-server connection for commands and
   			status reports, but may use a server-to-client connection for
   			transferring data on demand (e.g. LS, GET, PUT).
   	=> It is expected that the client side of an application protocol will
   		use the BIND request only to establish secondary connections after a
   		primary connection is established using CONNECT.  
	=> In is expected that a SOCKS server will use DST.ADDR and DST.PORT in 
		evaluating the BIND request.

   =>	Two replies are sent from the SOCKS server to the client during a
   		BIND operation.
		=>	The first is sent after the server creates and binds
   			a new socket.
			=> The BND.PORT field contains the port number that the
   				SOCKS server assigned to listen for an incoming connection.
			=>	The BND.ADDR field contains the associated IP address.  
			=> The client will typically use these pieces of information to notify 
				(via the primary or control connection) the application server of the 
				rendezvous address.  
		=> The second reply occurs only after the anticipated incoming
   			connection succeeds or fails.
   		=> In the second reply, the BND.PORT and BND.ADDR fields contain the
   			address and port number of the connecting host.

=> Reply Processing
	=> When a reply (REP value other than 0x00) indicates a failure
		=> SOCKS server MUST terminate the TCP connection shortly after sending
   			the reply.
		=> This must be no more than 10 seconds after detecting the
   			condition that caused a failure.

   	=> If the reply code (REP value of 0x00) indicates a success, and the
   		request was either a BIND or a CONNECT, 
		=> Client may now start passing data.
		=> If the selected authentication method supports encapsulation for the purposes 
			of integrity, authentication and/or confidentiality
			=> the data are encapsulated using the method-dependent encapsulation.
"""
# TODO: logging
# TODO: Check steps of SOCKS5 connection implementation for details of protocol specification/see section: Addressing

import socket
import string
import sys

class Protocol():

	def __init__(self):
		self.VER	= b'\x05'
		self.RSV	= b'\x00'
	
		# Hallo
		self.METHOD_NOAUTH 		= b'\x00'
    	#self.METHOD_GSSAPI 	= b'\x01'		# TODO, not supported until now
    	#self.METHOD_USERNAME   = b'\x02'		# TODO, not supoorted until now
    	##self.METHOD_IANAASS   = b'\x03'		# TODO, not supported until now
    	##self.METHOD_PRIV 		= b'\x80'		# TODO, not supported until now
		self.METHOD_NOACCEPT	= b'\xFF'

		# Connecting
		self.CMD_CONNECT 		= b'\x01'
   		#self.CMD_BIND 			= b'\x02'		# TODO, not supported until now
   		#self.CMD_UDP 			= b'\x03'		# TODO, not supported until now

		self.ATYP_IPV4			= b'\x01'		
   		#self.ATYP_DOMAINNAME   = b'\x03'		# TODO, not supported until now
   		#self.ATYP_IPV6 		= b'\x04'		# TODO, not supported until now

		self.REP_SUCCESSED 		= b'\x00'
    	#self.REP_SERVERFAIL	= b'\x01'		# TODO, not supported until now	
    	#self.REP_NOTALLOWED 	= b'\x02'		# TODO, not supported until now
    	#self.REP_NETUNREACH	= b'\x03'		# TODO, not supported until now
    	#self.REP_HOSTUNREACH	= b'\x04'		# TODO, not supported until now
    	#self.REP_CONNREFUSED	= b'\x05'		# TODO, not supported until now
    	#self.REP_TTLEXPIRED 	= b'\x06'		# TODO, not supported until now
    	#self.REP_NOTSUPPORTED  = b'\x07'		# TODO, not supported until now
    	#self.REP_ADDRESSNOTSUP = b'\x08'		# TODO, not supported until now


class Client():
	
	def __init__(self):
		self.sockToProxy = None

	def init_socketToProxy(self,protocol_family, socket_type,proxy_addr):
		try:
			sockToProxy = socket.socket(protocol_family, socket_type)
			sockToProxy.connect(proxy_addr)
			self.sockToProxy = sockToProxy
			print("[*] Initializing Socket ... Done")
		except Exception as e:
			print("[*] Unable To Initialize Socket")
			sys.exit(2)	# Error number?		

	def hallo_send(self, VER, NMETHODS,METHODS):
		msg_s1				= VER + NMETHODS + METHODS
		self.sockToProxy.sendall(msg_s1)
		#print(msg_s1)
		print("[*] Step 1: Send Greeting To Proxy Server ... Done")

	def hallo_recv(self):
		buf_s2		= 1024
		data_s2 = self.sockToProxy.recv(buf_s2)	
		#print(data_s2)

		Socks5_Protocol = Protocol()
		if data_s2[0] != Socks5_Protocol.VER[0]:
			print("[*] SOCKS Version not Supported.")
			sys.exit(2) # Error number?
			
		data_s2_method = data_s2[1:len(data_s2)]
		if data_s2_method.decode() == Socks5_Protocol.METHOD_NOACCEPT[0]:
			print("[*] No Acceptable Method")
			sys.exit(2) # Error number?
		
		print("[*] Step 2: Received Valid Answer From Proxy Server ... Done")
		
	def connect_send(self,VER,CMD,RSV,ATYP,DST_ADDR,DST_PORT):
		msg_s3				= VER + CMD + RSV + ATYP + DST_ADDR + DST_PORT
		#print(msg_s3)
		self.sockToProxy.sendall(msg_s3)
		print("[*] Step 3: Send Request Details To Proxy Server ... Done")

	def connect_recv(self):
		buf_s4		= 1024
		data_s4 = self.sockToProxy.recv(buf_s4)
		if data_s4:
			# TODO Check data if it is valid!!!
			print("[*] Step 4: Received Valid Answer From Proxy Server ... Done")
		else:
			print("[*] Received No Valid Data From Proxy Server")
			sys.exit(2)	# Error number?


class Proxy():
	
	def __init__(self):
		self.sockToClient	= None
		self.atyp 			= ""
		self.target_host 	= ""
		self.target_port	= 8888		# TODO: BUG, TEMPORARY HARD CODED PORT FOR TARGET
		self.cmd			= None
		self.connect_data	= None

	def init_socketToClient(self,protocol_family, socket_type,proxy_addr,max_conn):
		try:
			sockToClient = socket.socket(protocol_family, socket_type)
			sockToClient.bind(proxy_addr)
			sockToClient.listen(max_conn)
			self.sockToClient = sockToClient
			#print("[*] Initializing Sockets ... Done")
			#print("[*] Sockets Binded Successfully ... Done")
			print("[*] Server Started Successfully [ %d ] ... Done" % (proxy_addr[1]))
		except Exception as e:
			print("[*] Unable To Initialize Socket")
			sys.exit(2)	# Error number?

	def hallo_recv(self,conn):
		buf_s1		= 1024
		data_s1 	= conn.recv(buf_s1)
		#print(data_s1)

		Socks5_Protocol = Protocol()
		if data_s1[0] != Socks5_Protocol.VER[0]:
			print("[*] SOCKS Version not Supported.")
			sys.exit(2)	# Error number?	
		
		NO_METHODS = b'\x00'
		if data_s1[1] == NO_METHODS[0]:
			print("[*] No Methods Supported by Client")
			sys.exit(2)	# Error number?	
		
		data_s1_method = data_s1[2:len(data_s1)]
		# TODO: At the moment only one method supported, hence no problem
		# If more methods are support, we need an loop over all methods and have to compare
		if data_s1_method.decode() == Socks5_Protocol.METHOD_NOACCEPT[0]:
			print("[*] No Acceptable Method")
			sys.exit(2)	# Error number?	
		
		print("[*] Step 1: Receive Valid Greeting From Client ... Done")

	def hallo_send(self, VER, METHOD,conn):
		msg_s2				= VER + METHOD
		conn.sendall(msg_s2)
		print("[*] Step 2: Send Answer To Client ... Done")

	def connect_recv(self,conn):
		buf_s3				= 1024
		data_s3 			= conn.recv(buf_s3)
		self.connect_data	= data_s3
		#print(data_s3)
		
		Socks5_Protocol = Protocol()
		if data_s3[0] != Socks5_Protocol.VER[0]:
			print("[*] SOCKS Version not Supported.")
			sys.exit(2)	# Error number?	
		
		# atyp, target_host, target_port
		# CORRECTION OF BUFFER STRING ECT STUFF EVERYWHERE!
		if data_s3[3] == Socks5_Protocol.ATYP_IPV4[0]:
			# ATYP_IPV4: TODO: That's dirty!
			self.atyp = b'\x01'
			
			i = 8
			tmp_host = data_s3[4:i]
			target_host_as = socket.inet_ntoa(tmp_host)
			#print(target_host_as)
			self.target_host = target_host_as
			
			# ############################
			# TODO: BUG
			# TEMPORARY HARD CODED PORT FOR TARGET
			self.target_port = 8888
			# ############################
		
		#if data_s3[3] == Socks5_Protocol.ATYP_DOMAINNAME[0]:
    		# ATYP_DOMAINNAME
			# TODO
			# self.atyp = b'\x03'
		
		#if data_s3[3] == Socks5_Protocol.ATYP_IPV6[0]:
			# ATYP_IPV6
			# TODO
			# self.atyp = b'\x04'
		
		# cmd
		if data_s3[1] == Socks5_Protocol.CMD_CONNECT[0]:
			#CONNECT
			self.cmd = Socks5_Protocol.CMD_CONNECT[0]
		
		#if data_s3[1] == Socks5_Protocol.CMD_BIND[0]:
			# BIND
			# self.cmd = Socks5_Protocol.CMD_BIND[0]
		
		#if data_s3[1] == Socks5_Protocol.CMD_UDP[0]:
			# UDP ASSOCIATE
			# self.cmd = Socks5_Protocol.CMD_UDP[0]
		
	def connect_reply(self,conn):
		# TODO: That's dirty! Can be done nicer!
		Socks5_Protocol = Protocol()
		REP = Socks5_Protocol.REP_SUCCESSED[0]
		msg_tmp = self.connect_data.decode()
		msg_s4 = str(msg_tmp[0])+str(REP)+str(msg_tmp[2:])
		#print(msg_s4.encode())
		conn.sendall(msg_s4.encode())
		print("[*] Step 4: Send Answer To Client ... Done")

