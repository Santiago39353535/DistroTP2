import socket
import sys, traceback
import time
import os.path
import hashlib

CHUNK_SIZE = 1024
RECV = 1500
seq_r = 0
#header IFSSSSSAAAAATTTTCCCCC

def mandar_mensaje(s,addr,inicio,fin,seq,ack,tam,data):
	m = hashlib.md5()
	m.update((str(inicio)+str(fin)+str(seq).zfill(5)+str(ack).zfill(5)+str(tam).zfill(4)+data).encode())
	msg = str(inicio)+str(fin)+str(seq).zfill(5)+str(ack).zfill(5)+str(tam).zfill(4)+m.hexdigest()+data
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
	return (inicio,fin,seq,ack,tam,data,addr,validacion)

def upload(s,src,seq_r):
	f = open(src, "w")

	segmentos_recibidos = 1
	time_outs_consecutivos = 0
	tam_r = 0
	seq_e = 1
	inicio_e = 0
	fin_e = 0
	seq_esperado = seq_r
	while True:
		try:
			inicio_r, fin_r, seq_r, ack_r, tam_r, data_r,addr, validacion = recibir_mensaje(s)
			time_outs_consecutivos = 0
			if validacion:
				ack_e = seq_r
				tam_e = 0
				data_e = ''
				mandar_mensaje(s,addr,inicio_e,fin_e,seq_e,ack_e,tam_e,data_e)
				seq_e += 1
				if fin_r == 1:# falta avisar ack del fin
					break
				if seq_esperado == seq_r:
					segmentos_recibidos += 1
					f.write(data_r)
					seq_esperado = seq_r+1
					if(seq_esperado == 99999):
						seq_esperado = 0
		except socket.timeout:
			time_outs_consecutivos += 1
			f.seek((segmentos_recibidos - 1)*tam_r)
			if time_outs_consecutivos == 100:
				f.close()
				raise Exception("Se perdio coneccion con el cliente")

	f.close()
	tam_r = 0
	inicio_e = 0
	fin_e = 1
	seq_esperado = seq_r
	mandar_mensaje(s,addr,inicio_e,fin_e,seq_e,ack_e,tam_e,data_e)


def download(s,src,seq_e,addr):
		inicio = 0
		fin = 0
		ack_e = 1
		seq_e = seq_e +1
		esperado = seq_e

		time_outs_consecutivos = 0
		s.settimeout(0.1)
		#Empiezo a mandar archivo
		if os.path.exists(src):
			f = open(src, "r")
			data_e = f.read(CHUNK_SIZE)
			while data_e:
				try:
					tam_e = len(data_e)
					mandar_mensaje(s,addr,inicio,fin,seq_e,ack_e,tam_e,data_e)

					inicio_r, fin_r,seq_r, ack_r, tam_r, data_r,addr, validacion= recibir_mensaje(s)
					time_outs_consecutivos = 0
					if validacion:
						if( ack_r == esperado):
							seq_e += 1
							if seq_e == 99999:
								seq_e = 0
							esperado = seq_e
							data_e = f.read(CHUNK_SIZE)
				except socket.timeout:
					time_outs_consecutivos += 1
					if time_outs_consecutivos == 100:
						f.close()
						raise Exception("Se perdio coneccion con el cliente")

			f.close()


def inicio_coneccion(s):
	try:
		inicio_r, fin_r, seq_r, ack_r, tam_r, data_r, addr, validacion = recibir_mensaje(s)
		time_outs_consecutivos = 0
		if validacion:
			codigo = data_r[0:3]
			nombre = data_r[3:tam_r]
			if inicio_r == 1:
				inicio_e = 1
				fin_e = 0
				seq_e = 0
				ack_e = seq_r
				tam_e = 0
				data_e = ''
				s.settimeout(0.1)
				while True:
					try:
						mandar_mensaje(s,addr,inicio_e,fin_e,seq_e,ack_e,tam_e,data_e)
						inicio_r, fin_r, seq_r, ack_r, tam_r, data_r, addr,validacion = recibir_mensaje(s)
						time_outs_consecutivos = 0
						if validacion:
							esperado = 	seq_e
							if inicio_r == 0:
								break
					except socket.timeout:
						time_outs_consecutivos += 1
						if time_outs_consecutivos == 100:
							raise Exception("Sindrome de Syn atack")

				else:
					raise Exception("Conexion corrupta")
			return (codigo, nombre, seq_r, seq_e, addr)
	except socket.timeout:
		raise Exception("Problema de sincronizacion con el cliente")


def start_server(server_address, storage_dir):
	# TODO: Implementar UDP server
	print('UDP: start_server({}, {})'.format(server_address, storage_dir))
	time_outs_consecutivos = 0
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(server_address)

	#three way handshake
	while True:
		try:
			time_outs_consecutivos = 0
			s.settimeout(100000)
			#three way handshake
			codigo, nombre, seq_r, seq_e, addr = inicio_coneccion(s)
			try:
				s.settimeout(0.1)
				if codigo == "upl":
					upload(s,storage_dir+'/'+nombre,seq_r)
					fin_e = 1
					mandar_mensaje(s,addr,inicio_e,fin_e,seq_e,ack_e,tam_e,data_e)
				if codigo == "dow":
					download(s,storage_dir+'/'+nombre,seq_e,addr)
					time.sleep(0.2)
					while True:
						try:
							inicio_e = 0
							fin_e = 1
							seq_e += 1
							ack_e = seq_r
							tam_e = 0
							data_e = ''
							mandar_mensaje(s,addr,inicio_e,fin_e,seq_e,ack_e,tam_e,data_e)
							inicio_r, fin_r, seq_r, ack_r, tam_r, data_r, addr,validacion = recibir_mensaje(s)
							if validacion:
								if (fin_r == 1):
									break
						except socket.timeout:
							time_outs_consecutivos += 1
							if time_outs_consecutivos == 15:
								break
					fin_e = 2
					mandar_mensaje(s,addr,inicio_e,fin_e,seq_e,ack_e,tam_e,data_e)
			except Exception as e:
				 pass
		except Exception as e:
			 pass
	s.close()
