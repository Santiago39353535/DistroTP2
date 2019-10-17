import socket
import sys, traceback
import os.path
import hashlib

CHUNK_SIZE = 1024
RECV = 1500

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

def download_file(server_address, name, dst):
	# TODO: Implementar UDP download_file client
	print('UDP: download_file({}, {}, {})'.format(server_address, name, dst))

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	#"3"wayhandshake

	inicio = 1
	fin = 0
	seq_e = 0
	ack_e = 0
	tam_e = 3 + len(name)
	data_e = 'dow' + name

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
				else:
					s.close()
					sys.exit(1)
		except socket.timeout:
			time_outs_consecutivos += 1
			if time_outs_consecutivos == 100:
				s.close()
				sys.exit(1)

	f = open(dst, "w")
	inicio = 0
	fin = 0
	seq_e = seq_e#1
	ack_e = 0#0
	tam_e = 0
	data_e = ''
	segmentos_recibidos = 1
	seq_esperado = seq_r+1
	while True:
		try:
			mandar_mensaje(s,server_address,inicio,fin,seq_e,ack_e,tam_e,data_e)

			inicio_r, fin_r, seq_r, ack_r, tam_r, data_r,validacion = recibir_mensaje(s)
			time_outs_consecutivos = 0
			if validacion:
				ack_e = seq_r

				if fin_r == 1:# falta avisar ack del fin?
					f.write(data_r)
					break

				if seq_esperado == seq_r:
					seq_e += 1
					segmentos_recibidos += 1
					f.write(data_r)
					seq_esperado = seq_r+1
					if(seq_esperado==99999):
						seq_esperado = 0
		except socket.timeout:
			time_outs_consecutivos += 1
			#f.seek((segmentos_recibidos - 1)*tam_r)
			if time_outs_consecutivos == 100:
				f.close()
				s.close()
				sys.exit(1)

	f.close()

    #end
	inicio_e = 0
	fin_e = 1
	seq_e = seq_e
	ack_e = ack_e
	tam_e = 0
	data_e = ''
	esperado = seq_e

	while True:
		try:
			mandar_mensaje(s,server_address,inicio_e,fin_e,seq_e,ack_e,tam_e,data_e)
			inicio_r, fin_r, seq_r, ack_r, tam_r, data_r, validacion = recibir_mensaje(s)
			if validacion:
				if fin_r == 2:
					break
		except socket.timeout:
			time_outs_consecutivos += 1
			if time_outs_consecutivos == 50:
				break
	s.close()
