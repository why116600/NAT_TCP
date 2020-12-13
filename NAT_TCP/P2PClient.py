import socket
import struct
import sys
import threading
import time

_running=True

def ReceiveFrom(skt,data_len):
	pos=0
	buffer=b''
	while pos<data_len:
		data=skt.recv(data_len-pos)
		if len(data)<=0:
			return b''
		buffer=buffer+data
		pos+=len(data)
	return buffer

def HoleThread(skt,target_addr):
	print('start traverse to ',target_addr)
	try:
		skt.connect(target_addr)
		print('connected to ',target_addr)
		while _running:
			skt.send('Hello!NAT!'.encode())
			time.sleep(1.5)
	except BaseException as e:
		print('HoleThread ends with ',repr(e))
		return
	print('HoleThread ends normally.')


def main():
	if len(sys.argv)<3:
		print('wrong arguments!')
		return
	server_addr=(sys.argv[1],int(sys.argv[2]))
	bSucceeded=False

	main_skt=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	hole_skt=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	listen_skt=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

	main_skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	hole_skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	listen_skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	try:
		main_skt.connect(server_addr)
		data=ReceiveFrom(main_skt,6)
		port,addr_len=struct.unpack('=Hi',data[:6])
		data=ReceiveFrom(main_skt,addr_len)
		target_addr=(data.decode(),port)
		my_addr=main_skt.getsockname()
		hole_skt.bind(my_addr)
		listen_skt.bind(my_addr)
		listen_skt.listen(0)
		th=threading.Thread(target=HoleThread,args=(hole_skt,target_addr))
		th.start()
		skt,addr=listen_skt.accept()
		bSucceeded=True
		print('got a connection from ',addr)
		while True:
			data=skt.recv(1024)
			if len(data)<=0:
				break
			print('received message:',data.decode())

	except BaseException as e:
		print('end with ',repr(e))
	finally:
		if bSucceeded:
			skt.close()
		_running=False
		main_skt.close()
		hole_skt.close()
		listen_skt.close()
	
	pass

if __name__=='__main__':
	main()