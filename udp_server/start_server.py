import socket
import sys, traceback
import time
import os.path

CHUNK_SIZE = 1024
RECV = 1500
seq_r = 0
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
	return (inicio,fin,seq,ack,tam,data,addr)

def upload(s,src,seq_r):
	print("Se empieza a recivir el archivo")
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
			inicio_r, fin_r, seq_r, ack_r, tam_r, data_r,addr = recibir_mensaje(s)
			time_outs_consecutivos = 0
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

	print("Termino de recibir el archivo")
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
			print("Se empieza a mandar el archivo")
			while data_e:
				try:
					tam_e = len(data_e)
					mandar_mensaje(s,addr,inicio,fin,seq_e,ack_e,tam_e,data_e)

					inicio_r, fin_r,seq_r, ack_r, tam_r, data_r,addr= recibir_mensaje(s)
					time_outs_consecutivos = 0
					if( ack_r == esperado):
						seq_e += 1
						if seq_e == 99999:
							seq_e = 0
						esperado = seq_e
						data_e = f.read(CHUNK_SIZE)

				except socket.timeout:
					time_outs_consecutivos += 1
					if time_outs_consecutivos == 100:
						print("Se perdio coneccion con el cliente")
						f.close()
						raise Exception("Se perdio coneccion con el cliente")

			print("Informando Fin de Archivo")
			f.close()


def inicio_coneccion(s):
	try:
		inicio_r, fin_r, seq_r, ack_r, tam_r, data_r, addr= recibir_mensaje(s)
		time_outs_consecutivos = 0
		print("se recibio mensaje")
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
					inicio_r, fin_r, seq_r, ack_r, tam_r, data_r, addr = recibir_mensaje(s)
					time_outs_consecutivos = 0
					esperado = 	seq_e
					if inicio_r == 0:
						break# go to print nombre
				except socket.timeout:
					time_outs_consecutivos += 1
					if time_outs_consecutivos == 100:
						print("Sindrome de Syn atack")
						raise Exception("Sindrome de Syn atack")

			else:
				print("Conexion corrupta")
				raise Exception("Conexion corrupta")
		return (codigo, nombre, seq_r, seq_e, addr)
	except socket.timeout:
		print("Problema de sincronizacion con el cliente")
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
				print(nombre)
				s.settimeout(0.1)
				if codigo == "upl":
					upload(s,storage_dir+'/'+nombre,seq_r)
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
						inicio_r, fin_r, seq_r, ack_r, tam_r, data_r, addr = recibir_mensaje(s)
						if (fin_r == 1):
							break
					except socket.timeout:
						time_outs_consecutivos += 1
						if time_outs_consecutivos == 15:
							break
				print("Esperando nuevo cliente")
			except Exception as e:
				 pass
		except Exception as e:
			 pass
	s.close()
