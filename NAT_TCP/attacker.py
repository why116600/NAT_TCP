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
	target_addr=[]
	try:
		transfer_socket.connect(server_addr)
		transfer_socket.send(struct.pack('b',2))
		nCli=0
		while nCli<=0:
			data=ReceiveData(transfer_socket,6)
			myport,nCli=struct.unpack('=Hi',data)
			if nCli<0:
				print('wrong transfer server!')
				pass
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
		pass
	finally:
		transfer_socket.close()

	my_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	my_socket.settimeout(3)
	print('connect to ',target_addr[0])
	for i in range(10):
		try:
			my_socket.connect(target_addr[0])
			print('connected to the server:',target_addr[0])
			while True:
				my_socket.send('Hello!NAT!'.encode())
				time.sleep(1)
		except BaseException:
			print('exception happend!')
			time.sleep(1)

if __name__=='__main__':
	main()