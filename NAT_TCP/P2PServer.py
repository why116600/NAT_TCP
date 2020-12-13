import socket
import struct
import sys

def EncodeAddr(addr):
	data=struct.pack('=Hi',addr[1],len(addr[0]))
	return data+addr[0].encode()

def main():
	myport=1234
	clients=[]
	if len(sys.argv)>1:
		myport=int(sys.argv[1])
	try:
		main_skt=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		main_skt.bind(('0.0.0.0',myport))
		main_skt.listen(0)
		while True:
			cli=main_skt.accept()
			clients.append(cli)
			if (len(clients)%2)==0:
				print('got a p2p between ',clients[-1][1],' and ',clients[-2][1])
				clients[-1][0].send(EncodeAddr(clients[-2][1]))
				clients[-2][0].send(EncodeAddr(clients[-1][1]))
	except BaseException as e:
		print('end with ',repr(e))
		for cli in clients:
			cli[0].close()
		main_skt.close()

if __name__=='__main__':
	main()