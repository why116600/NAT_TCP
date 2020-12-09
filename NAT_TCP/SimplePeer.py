import socket
import _thread
import time
import sys
from threading import Event

_bRunning=True
created_event=Event()

def traverse_thread(addr1,addr2):
	skt=socket.socket(socket.AF_INET,socket.SOCK_STREAM,socket.IPPROTO_TCP)
	skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	skt.settimeout(1)
	skt.bind(addr1)
	created_event.set()
	while _bRunning:
		try:
			skt.connect(addr2)
			while _bRunning:
				skt.send('Hello!NAT!'.encode())
				time.sleep(1)
			skt.close()
		except BaseException:
			continue
	print('end traverse')
	skt.close()


def main():
	if len(sys.argv)<2:
		print('wrong arguments!')
		return
	myport=int(sys.argv[1])
	my_addr=('0.0.0.0',myport)
	if len(sys.argv)>3:
		target_addr=(sys.argv[2],int(sys.argv[3]))
		_thread.start_new_thread(traverse_thread,(my_addr,target_addr))
		created_event.wait()

	if len(sys.argv)>4:
		try:
			while True:
				time.sleep(1)
		except BaseException:
			return
	try:
		main_skt=socket.socket(socket.AF_INET,socket.SOCK_STREAM,socket.IPPROTO_TCP)
		main_skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		main_skt.bind(my_addr)
		main_skt.listen(10)
		print('start listening to ',my_addr)
		while True:
			skt,addr=main_skt.accept()
			print(addr,' connected')
			try:
				while True:
					data=skt.recv(1024)
					print('received:',data.decode())
			except BaseException as e1:
				print('client receiving error:',repr(e1))
				skt.close()
	except BaseException as e:
		print('exception happend:',repr(e))
	_bRunning=False

if __name__=='__main__':
	main()