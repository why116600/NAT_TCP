import socket
import struct
import sys

def BroadcastAddress(target,address):
	print('broadcast address to ',target)
	for i,(skt,addr1) in enumerate(target):
		data=struct.pack('=Hi',addr1[1],len(address))
		for skt1,addr2 in address:
			data+=struct.pack('i',len(addr2[0]))
			data+=addr2[0].encode()
			data+=struct.pack('=H',addr2[1])
		print('send ',data,' to ',addr1)
		try:
			skt.send(data)
		except BaseException:
			print('client ',addr1,' goes wrong')
			del target[i]
			

def main():
    defender=[]
    attacker=[]
    server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    #server_socket.settimeout(10)
    port=1234
    if len(sys.argv)>1:
        port=int(sys.argv[1])
    server_socket.bind(('0.0.0.0',port))
    server_socket.listen(0)
    try:
        while True:
            cli=server_socket.accept()
            cli[0].settimeout(10)
            try:
                data=cli[0].recv(1)
                cli_type=struct.unpack('=b',data)
                if cli_type[0]==1:
                    print('got defender client:',cli)
                    defender.append(cli)
                    BroadcastAddress(defender,attacker)
                elif cli_type[0]==2:
                    print('got attacker client:',cli)
                    attacker.append(cli)
                    BroadcastAddress(attacker,defender)
                    BroadcastAddress(defender,attacker)
                else:
                    print('wrong client')
                    cli[0].close()
            except BaseException as e1:
                print('client ',cli[1],' exception:',repr(e1))
                cli[0].close()
    except BaseException as e:
        print('exception happenned:',repr(e))
    finally:
        server_socket.close()
        
    pass

if __name__=='__main__':
    main()