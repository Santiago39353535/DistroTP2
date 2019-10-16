import socket
import sys, traceback
import os.path
import hashlib

CHUNK_SIZE = 1024
RECV = 1500

#header IFSSSSSAAAAATTTT

def mandar_mensaje(s,addr,inicio,fin,seq,ack,tam,data):
	m = hashlib.md5()
	m.update((str(inicio)+str(fin)+str(seq).zfill(5)+str(ack).zfill(5)+str(tam).zfill(4)+data).encode())
	checksum = m.hexdigest()
	msg = str(inicio)+str(fin)+str(seq).zfill(5)+str(ack).zfill(5)+str(tam).zfill(4)+checksum+data
	s.sendto(msg.encode(),addr)

def recibir_mensaje(s):
	m = hashlib.md5()
	recv, addr = s.recvfrom(RECV)
	recv = recv.decode()
	inicio = int(recv[0])
	fin = int(recv[1])
	seq = int(recv[2:7])#del 0 al 5 sin incluir
	ack = int(recv[7:12])
	tam = int(recv[12:16])
	checksum_r = recv[16:48]
	data = recv[48:48+int(tam)]
	m.update((recv[0:16]+recv[48:48+int(tam)]).encode())
	checksum_c = m.hexdigest()
	validacion = checksum_c == checksum_r
	return (inicio,fin,seq,ack,tam,data,validacion)

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
			inicio_r, fin_r, seq_r, ack_r, tam_r, data_r, validacion = recibir_mensaje(s)
			time_outs_consecutivos = 0
			if validacion:
				if inicio == 1 and  ack_r == esperado:
					ack_e = seq_r
					seq_e += 1
					break
					#mandar_mensaje(s,server_address,inicio,fin,seq_e,ack_e,tam_e,data_e) puedo avisar junto al primer chunk
				else:
					print("falla en protocolo entre conexiones")
					s.close()
					sys.exit(1)
		except socket.timeout:
			time_outs_consecutivos += 1
			if time_outs_consecutivos == 100:
				print("Problema de sincronizacion con el servidor")
				s.close()
				sys.exit(1)


	inicio = 0
	seq_e += 1
	s.settimeout(0.1)
	#Empiezo a mandar archivo
	if os.path.exists(src):
		f = open(src, "r")
		data_e = f.read(CHUNK_SIZE)
		print("Se empieza a mandar el archivo")
		esperado = seq_e
		try:
			while data_e:
				try:
					tam_e = len(data_e)
					mandar_mensaje(s,server_address,inicio,fin,seq_e,ack_e,tam_e,data_e)

					inicio_r, fin_r,seq_r, ack_r, tam_r, data_r, validacion = recibir_mensaje(s)
					time_outs_consecutivos = 0
					if validacion:
						if( fin_r == 1):
							print("server error")
							raise Exception("server error")
						if( ack_r == esperado):
							seq_e += 1
							esperado = seq_e
							if(seq_e == 99999):
								seq_e = 0
							data_e = f.read(CHUNK_SIZE)
				except socket.timeout:
					time_outs_consecutivos += 1
					if time_outs_consecutivos == 100:
						print("Server desconectado")
						raise Exception("server error")
		except Exception as e:
			f.close()
			s.close()
			sys.exit(1)

		print("Informando Fin de Archivo")
		f.close()
	else:
		print("El archivo no existe")
	#fin de la coneccion
	while True:
		try:
			inicio = 0
			fin = 1
			ack_e = 0
			tam_e = 0
			data_e = ''
			esperado = seq_e
			mandar_mensaje(s,server_address,inicio,fin,seq_e,ack_e,tam_e,data_e)
			inicio_r, fin_r,seq_r, ack_r, tam_r, data_r, validacion = recibir_mensaje(s)
			time_outs_consecutivos = 0
			if validacion:
				if ack_r == esperado:
					break
		except socket.timeout:
			time_outs_consecutivos += 1
			if time_outs_consecutivos == 50:
				break
	s.close()
