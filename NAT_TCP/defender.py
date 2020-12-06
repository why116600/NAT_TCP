import socket
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
	client_addr=[]
	myport=0
	try:
		transfer_socket.connect(server_addr)
		data=struct.pack('=b',1)
		transfer_socket.send(data)
		nCli=0
		while nCli<=0:
			data=ReceiveData(transfer_socket,6)
			if len(data)<=0 or data==b'':
				print('wrong server!')
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
			client_addr.append((strIP,port[0]))
	except BaseException as e:
		print('transfer server socket exception:',repr(e))
		return

	print('got my port:',myport)
	test_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	#test_socket.settimeout(1)
	test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	for cli in client_addr:
		try:
			print('go through ',cli)
			test_socket.connect(cli)
			#test_socket.close()
		except BaseException as e:
			print('cannot connect of course:',repr(e))
			continue
	
	trans_addr=transfer_socket.getsockname()
	test_addr=test_socket.getsockname()
	#myport=test_addr[1]
	print('listen to ',(trans_addr[0],test_addr[1]))
	server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind((trans_addr[0],test_addr[1]))
	server_socket.listen(0)
	while True:
		try:
			cli=server_socket.accept()
			skt=cli[0]
			print('got client:',cli[1])
			while True:
				data=cli[0].recv(1000)
				s=data.decode()
				print('received message:',s)
		except BaseException as e:
			print('end with ',repr(e))
			skt.close()
			break
	server_socket.close()
	transfer_socket.close()


	pass

if __name__=='__main__':
	main()