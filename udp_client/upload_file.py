import socket
import sys, traceback

CHUNK_SIZE = 1024
RECV = 1500
#header SSSSSAAAAATTTT

def mandar_mensaje(s,addr,seq,ack,tam,data):
	msg = str(seq).zfill(5)+str(ack).zfill(5)+str(tam).zfill(4)+data
	s.sendto(msg.encode(),addr)

def recibir_mensaje(s):
	recv, addr = s.recvfrom(RECV)
	recv = recv.decode()
	seq = int(recv[0:5])#del 0 al 5 sin incluir
	ack = int(recv[5:10])
	tam = int(recv[10:14])
	data = recv[14:14+int(tam)]
	return (seq,ack,tam,data)

def upload_file(server_address, src, name):
	# TODO: Implementar UDP upload_file client
	print('UDP: upload_file({}, {}, {})'.format(server_address, src, name))

	own_address = ("127.0.0.1",8081)
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(own_address)
	#s.settimeout(1)



	#Three-way-Handshake

	#try:
	#	s.sendto('inicio'.encode(),server_address)
	#	ack_recv = recv_numeros(s)
	#	if( ack_recv != inicio):
	#		raise Exeption("Problema ACK sincronizaciion")
	#	send_ack(s,server_address,inicio)
	#except socket.timeout:
	#	print("Timeout sincronizacion")
	#	sys.exit(1)

	#Fin de la sincroizacion


	#Mando comando
	seq_e = 10
	ack_e = 0
	tam_e = 3
	data_e = 'upl'
	mandar_mensaje(s,server_address,seq_e,ack_e,tam_e,data_e)

	esperado = seq_e

	seq_r, ack_r, tam_r, data_r = recibir_mensaje(s)

	if( ack_r != esperado):
		raise Exeption("Problema ACK sincronizaciion de operacion")
	seq_e += 1

	#mando nombre del archivo
	print(name)
	mandar_mensaje(s,server_address,seq_e,ack_e,len(name),name)

	esperado = seq_e

	seq_r, ack_r, tam_r, data_r = recibir_mensaje(s)

	if( ack_r != esperado):
		raise Exeption("Problema ACK sincronizaciion de operacion")
	seq_e += 1


	#Empiezo a mandar archivo
	f = open(src, "r")
	data_e = f.read(CHUNK_SIZE)

	i = 1
	while data_e:
		i += 1
		tam_e = len(data_e)
		mandar_mensaje(s,server_address,seq_e,ack_e,tam_e,data_e)
		esperado = seq_e
		seq_r, ack_r, tam_r, data_r = recibir_mensaje(s)
		if( ack_r == esperado):
			seq_e += 1
			data_e = f.read(CHUNK_SIZE)


	print("Informando Fin de Archivo")

	#fin de la coneccion

	ack_e = 0
	tam_e = 3
	data_e = 'fin'
	mandar_mensaje(s,server_address,seq_e,ack_e,tam_e,data_e)
	f.close()
	s.close()
