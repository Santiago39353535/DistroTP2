import socket

RECV = 1500
#header SSSSSAAAAATTTT

def start_server(server_address, storage_dir):
	# TODO: Implementar UDP server
	print('UDP: start_server({}, {})'.format(server_address, storage_dir))

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(server_address)
	#s.settimeout(1)

	fin = 0



	recv, addr = s.recvfrom(RECV)
	recv = recv.decode()
	seq_r = int(recv[0:5])#del 0 al 5 sin incluir
	ack_r = int(recv[5:10])
	tam_r = int(recv[10:14])
	data_r = recv[14:14+int(tam_r)]

	seq_e = 0
	ack_e = seq_r
	tam_e = 0
	data_e = ''
	msg = str(seq_e).zfill(5)+str(ack_e).zfill(5)+str(tam_e).zfill(4)+data_e
	s.sendto(msg,addr)

	f = open("storage/ejempplo","wb")

	while True:
			recv, addr = s.recvfrom(RECV)
			recv = recv.decode()
			seq_r = int(recv[0:5])#del 0 al 5 sin incluir
			ack_r = int(recv[5:10])
			tam_r = int(recv[10:14])
			data_r = recv[14:14+int(tam_r)]
			#no soporta perdida de paquete
			if data_r == 'fin':
				break
			send_ack(s,addr,esperado)
			#perdida de paquete rompe, poner en header num de seq
			f.write(recv.decode())

	f.close()
	s.close()
