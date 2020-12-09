import socket
import time
import struct
import sys


def ReceiveData(skt,dataLen):
	pos=0
	data=b''
	while pos<dataLen:
		buf=skt.recv(dataLen-pos)
		if len(buf)<=0:
			return b''
		data+=buf
		pos+=len(buf)
	return data

def main():
	server_addr=(sys.argv[1],int(sys.argv[2]))
	transfer_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	transfer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	#transfer_socket.settimeout(1)
	target_addr=[]
	try:
		transfer_socket.connect(server_addr)
		transfer_socket.send(struct.pack('b',2))
		nCli=0
		while nCli<=0:
			data=ReceiveData(transfer_socket,6)
			if len(data)<=0 or data==b'':
				print('wrong server data!')
				return
			myport,nCli=struct.unpack('=Hi',data)
			if nCli<0:
				print('wrong transfer server!')
				return
		for i in range(nCli):
			data=ReceiveData(transfer_socket,4)
			iplen=struct.unpack('i',data)
			data=ReceiveData(transfer_socket,iplen[0])
			strIP=data.decode()
			data=ReceiveData(transfer_socket,2)
			port=struct.unpack('=H',data)
			target_addr.append((strIP,port[0]))
	except BaseException as e:
		print('transfer server socket exception:',repr(e))
		return

	
	trans_addr=transfer_socket.getsockname()
	for i in range(20):
		try:
			my_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			my_socket.bind(trans_addr)
			my_socket.settimeout(1)
			print(i,':connect to ',target_addr[0])
			my_socket.connect(target_addr[0])
			print('connected to the server:',target_addr[0])
			while True:
				my_socket.send('Hello!NAT!'.encode())
				time.sleep(1)
		except BaseException as e:
			print('exception happend!',repr(e))
			#time.sleep(1)
		finally:
			my_socket.close()


	transfer_socket.close()

if __name__=='__main__':
	main()