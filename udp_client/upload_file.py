import socket
import sys, traceback

CHUNK_SIZE = 1024
RECV = 1500
#header SSSSSAAAAATTTT

def upload_file(server_address, src, name):
	# TODO: Implementar UDP upload_file client
	print('UDP: upload_file({}, {}, {})'.format(server_address, src, name))

	own_address = ("127.0.0.0",8079)
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

	seq_e = 10
	ack_e = 0
	tam_e = 3
	data_e = 'upl'
	msg = str(seq_e).zfill(5)+str(ack_e).zfill(5)+str(tam_e).zfill(4)+data_e
	s.sendto(msg.encode(),server_address)

	esperado = seq_e
	recv, addr = s.recvfrom(RECV)
	recv = recv.decode()
	seq_r = int(recv[0:5])#del 0 al 5 sin incluir
	ack_r = int(recv[5:10])
	tam_r = int(recv[10:14])
	data_r = recv[14:14+int(tam_r)]

	if( ack_r != esperado):
		raise Exeption("Problema ACK sincronizaciion de operacion")
	seq_e += 1
	f = open(src, "rb")

	while data_e:
		try:
			data_e = f.read(CHUNK_SIZE)
			tam_e = len(data_e)
			msg = str(seq_e).zfill(5)+str(ack_e).zfill(5)+str(tam_e).zfill(4)+data_e
			s.sendto(msg.encode(),server_address)
			esperado = seq_e

			recv, addr = s.recvfrom(RECV)
			recv = recv.decode()
			seq_r = int(recv[0:5])#del 0 al 5 sin incluir
			ack_r = int(recv[5:10])
			tam_r = int(recv[10:14])
			data_r = recv[14:14+int(tam_r)]
			if( ack_r == esperado):
				seq_e += 1
				data_e = f.read(CHUNK_SIZE)
		except socket.timeout:
			pass

	print("Informando Fin de Archivo")

	#fin de la coneccion

	ack_e = 0
	tam_e = 3
	data_e = 'fin'
	msg = str(seq_e).zfill(5)+str(ack_e).zfill(5)+str(tam_e).zfill(4)+data_e
	s.sendto(msg.encode(),server_address)
	f.close()
	s.close()
