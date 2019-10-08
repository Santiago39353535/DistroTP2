import socket

CHUNK_SIZE = 1024

def recv_numeros(socket):
	buf = ''
	while '\n' not in buf:
		recv, addr = socket.recvfrom(1)
		buf += recv.decode()
	return buf

def send_ack(socket,server_address,ack):
	val = str(ack) + '\n'
	socket.sendto(val.encode(),server_address)

def upload_file(server_address, src, name):
	# TODO: Implementar UDP upload_file client
	print('UDP: upload_file({}, {}, {})'.format(server_address, src, name))
	
	own_adress = ("127.0.0.1","8081")
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(own_address)

	inicio = 0
	fin = 1

	#Three-way-Handshake
	s.sendto('inicio'.encode(),server_address)

	ack_recv = recv_numero(s)
	if( ack_recv != inicio):
		raise Exeption("Problema ACK sincronizaciion")
	

	send_ack(s,server_address,inicio)

	#Fin de la sincroizacion
	
	esperado = 10
	s.sendto("upl".encode(),server_address)
	ack_recv = recv_numero(s)
	if( ack_recv != esperado):
		raise Exeption("Problema ACK sincronizaciion de operacion")
	esperado++
	
	f = open(src, "rb")
	content = f.read(CHUNK_SIZE)

	while content:
		s.sendto((str(len(content))+'\n'+content).encode(),server_address)
		ack_recv = recv_numero(s)
		if( ack_recv == esperado):
			esperado++
			content = f.read(CHUNK_SIZE)

	print("Informando Fin de Archivo")
	#fin de la coneccion
	s.sendto('fin'.encode(),server_address)
	ack_recv = recv_numeros(s)
	recv, addr = socket.recvfrom(3)
	if( recv.decode() != 'fin'):
		 raise Exeption("Problema cierre de coneccion")
	send_ack(s,server_address,fin)

