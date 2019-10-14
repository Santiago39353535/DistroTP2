import socket
import sys, traceback

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
	return (inicio,fin,seq,ack,tam,data,addr)

def upload(s,src):
	print("Se empieza a recivir el archivo")
	f = open(src, "w")

	segmentos_recibidos = 1
	time_outs_consecutivos = 0
	tam_r = 0
	seq_e = 1
	inicio_e = 0
	fin_e = 0
	while True:
		try:
			inicio_r, fin_r, seq_r, ack_r, tam_r, data_r,addr = recibir_mensaje(s)
			time_outs_consecutivos = 0
			segmentos_recibidos += 1
			ack_e = seq_r
			tam_e = 0
			data_e = ''
			mandar_mensaje(s,addr,inicio_e,fin_e,seq_e,ack_e,tam_e,data_e)
			seq_e += 1
			if fin_r == 1:
				break
			f.write(data_r)
		except socket.timeout:
			time_outs_consecutivos += 1
			f.seek((segmentos_recibidos - 1)*tam_r)
			if time_outs_consecutivos == 100:
				print("Se perdio coneccion con el cliente")
				sys.exit(1)

	print("Termino de recibir el archivo")
	f.close()



def start_server(server_address, storage_dir):
	# TODO: Implementar UDP server
	print('UDP: start_server({}, {})'.format(server_address, storage_dir))
	time_outs_consecutivos = 0
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(server_address)

	#three way handshake
	try:
		inicio_r, fin_r, seq_r, ack_r, tam_r, data_r, addr = recibir_mensaje(s)
		print("se recibio mensaje")
		s.settimeout(1)
		codigo = data_r[0:3]
		nombre = data_r[3:tam_r]
		if inicio_r == 1:
			inicio_e = 1
			fin_e = 0
			seq_e = 0
			ack_e = seq_r
			tam_e = 0
			data_e = ''
			mandar_mensaje(s,addr,inicio_e,fin_e,seq_e,ack_e,tam_e,data_e)
		inicio_r, fin_r, seq_r, ack_r, tam_r, data_r, addr = recibir_mensaje(s)
		esperado = 	seq_e
		if ack_r != esperado:
			print("Problema de sincronizacion con el cliente")
			sys.exit(1)
	except socket.timeout:
		print("Problema de sincronizacion con el cliente")
		sys.exit(1)

	print(nombre)
	#Recivo nombre de archivo
	s.settimeout(0.1)
	if codigo == "upl":
		upload(s,storage_dir+'/'+nombre)


	s.close()
