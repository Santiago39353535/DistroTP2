import socket
import sys, traceback

CHUNK_SIZE = 1024
RECV = 1500
#header IFSSSSSAAAAATTTT

def mandar_mensaje(s,addr,inicio,fin,seq,ack,tam,data):
	msg = str(inicio)+str(fin)+str(seq).zfill(5)+str(ack).zfill(5)+str(tam).zfill(4)+data
	s.sendto(msg.encode(),addr)

def recibir_mensaje(s):
	recv, addr = s.recvfrom(RECV)
	recv = recv.decode()
	inicio = int(recv[0])
	fin = int(recv[1])
	seq = int(recv[2:7])#del 0 al 5 sin incluir
	ack = int(recv[7:12])
	tam = int(recv[12:16])
	data = recv[16:16+int(tam)]
	return (inicio,fin,seq,ack,tam,data)

def upload_file(server_address, src, name):
	# TODO: Implementar UDP upload_file client
	print('UDP: upload_file({}, {}, {})'.format(server_address, src, name))
	time_outs_consecutivos = 0
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	#three way handshake
	inicio = 1
	fin = 0
	seq_e = 0
	ack_e = 0
	tam_e = 3 + len(name)
	data_e = 'upl' + name
	s.settimeout(0.1)
	time_outs_consecutivos = 0

	while True:
		try:
			mandar_mensaje(s,server_address,inicio,fin,seq_e,ack_e,tam_e,data_e)
			esperado = seq_e
			inicio_r, fin_r, seq_r, ack_r, tam_r, data_r = recibir_mensaje(s)
			if inicio == 1 and  ack_r == esperado:
				ack_e = seq_r
				seq_e += 1
				break
				#mandar_mensaje(s,server_address,inicio,fin,seq_e,ack_e,tam_e,data_e) puedo avisar junto al primer chunk
			else:
				print("falla en protocolo entre conexiones")
				sys.exit(1)
		except socket.timeout:
			time_outs_consecutivos += 1
			if time_outs_consecutivos == 20:
				print("Problema de sincronizacion con el servidor")
				sys.exit(1)


	inicio = 0
	seq_e += 1
	s.settimeout(0.1)
	#Empiezo a mandar archivo
	f = open(src, "r")
	data_e = f.read(CHUNK_SIZE)
	print("Se empieza a mandar el archivo")
	esperado = seq_e
	while data_e:
		try:
			tam_e = len(data_e)
			mandar_mensaje(s,server_address,inicio,fin,seq_e,ack_e,tam_e,data_e)

			inicio_r, fin_r,seq_r, ack_r, tam_r, data_r = recibir_mensaje(s)
			time_outs_consecutivos = 0
			if( ack_r == esperado):
				seq_e += 1
				esperado = seq_e
				data_e = f.read(CHUNK_SIZE)
		except socket.timeout:
			time_outs_consecutivos += 1
			if time_outs_consecutivos == 100:
				print("Server desconectado")
				sys.exit(1)




	print("Informando Fin de Archivo")

	#fin de la coneccion
	while True:
		try:
			inicio = 0
			fin = 1
			ack_e = 0
			tam_e = 0
			data_e = ''
			mandar_mensaje(s,server_address,inicio,fin,seq_e,ack_e,tam_e,data_e)
			if ack_r == esperado:
				break
			inicio_r, fin_r,seq_r, ack_r, tam_r, data_r = recibir_mensaje(s)
		except socket.timeout:
			time_outs_consecutivos += 1
			if time_outs_consecutivos == 20:
				break

	f.close()
	s.close()
