import socket
import struct
import sys
import json

class PACKET_FILTER:
	def __init__(self):
		self.filter_data={}

	def load_file(self,filename):
		with open(filename,'r') as fp:
			json_str=fp.readline()
		self.filter_data=json.loads(json_str)

	def check_tcp(self,tcp_header):
		src_port=-1
		dst_port=-1
		if 'src_port' in self.filter_data.keys():
			src_port=self.filter_data['src_port']
		if 'dst_port' in self.filter_data.keys():
			dst_port=self.filter_data['dst_port']
		if src_port>=0 and tcp_header.src_port==src_port:
			return True
		if dst_port>=0 and tcp_header.dst_port==dst_port:
			return True
		return src_port<0 and dst_port<0

class IP_HEADER:
	def __init__(self,data):
		self.protocal_names={1:'ICMP',6:'TCP',17:'UDP'}
		self.total_size=struct.unpack('=H',data[2:4])[0]
		self.flag=struct.unpack('=H',data[4:6])[0]<<3
		self.flag|=struct.unpack('=B',data[6:7])[0]&0x7
		self.TTL=struct.unpack('=B',data[8:9])[0]
		p=struct.unpack('=B',data[9:10])[0]
		self.protocal=p
		if p in self.protocal_names.keys():
			self.protocal_name=self.protocal_names[p]
		else:
			self.protocal_name=str(p)
		self.src_address='%u.%u.%u.%u'%struct.unpack('=BBBB',data[12:16])
		self.dst_address='%u.%u.%u.%u'%struct.unpack('=BBBB',data[16:20])

	def to_string(self):
		return 'total_size=%d,flag=%05x,TTL=%d,protocal=%s,src_ip=%s,dst_ip=%s'%(\
				self.total_size,\
				self.flag,\
				self.TTL,\
				self.protocal_name,\
				self.src_address,\
				self.dst_address)

	def __str__(self):
		return self.to_string()

class TCP_HEADER:
	def __init__(self,data):
		self.src_port=struct.unpack('!H',data[0:2])[0]
		self.dst_port=struct.unpack('!H',data[2:4])[0]
		self.order=struct.unpack('!I',data[4:8])[0]
		self.ack_order=struct.unpack('!I',data[8:12])[0]
		self.flag=struct.unpack('!H',data[12:14])[0]

	def to_string(self):
		mystr= 'src_port=%u,dst_port=%u,order=%u,ack=%u'%(self.src_port,self.dst_port,self.order,self.ack_order)
		if self.flag&0x0400:
			mystr+=',URG'
		if self.flag&0x0800:
			mystr+=',ACK'
		if self.flag&0x1000:
			mystr+=',PSH'
		if self.flag&0x2000:
			mystr+=',RST'
		if self.flag&0x4000:
			mystr+=',SYN'
		if self.flag&0x8000:
			mystr+=',FIN'
		return mystr

	def __str__(self):
		return self.to_string

def main():
	filter=PACKET_FILTER()
	if len(sys.argv)>1:
		filter.load_file(sys.argv[1])
	ip_offset=0
	try:
		try:
			skt=socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.IPPROTO_IP)
			skt.bind(('0.0.0.0',0))
			skt.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
		except OSError:
			skt=socket.socket(socket.PF_PACKET,socket.SOCK_RAW,socket.htons(2048))
			ip_offset=14
	except BaseException as e:
		print('started with error:',repr(e))
		return
	try:
		while True:
			buffer,addr=skt.recvfrom(65536)
			if len(buffer)<20:
				continue
			pos=ip_offset
			ip_header=IP_HEADER(buffer[pos:])
			pos+=20
			show_text=str(addr)+','+ip_header.to_string()
			if ip_header.protocal==6:
				tcp_header=TCP_HEADER(buffer[pos:])
				show_text+=','+tcp_header.to_string()
				pos+=20
				if not filter.check_tcp(tcp_header):
					continue
			else:
				continue
			print(show_text)
			print(buffer[pos:])
	except BaseException as e:
		print('end with ',repr(e))
	finally:
		skt.close()


if __name__=='__main__':
	main()
