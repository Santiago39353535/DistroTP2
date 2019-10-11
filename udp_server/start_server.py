import socket

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
	return (seq,ack,tam,data,addr)

def upload(s,src):
	f = open(src, "w")
	while True:
		seq_r, ack_r, tam_r, data_r,addr = recibir_mensaje(s)
		#no soporta perdida de paquete
		seq_e = 0
		ack_e = seq_r
		tam_e = 0
		data_e = ''
		mandar_mensaje(s,addr,seq_e,ack_e,tam_e,data_e)
		seq_e += 1
		if data_r == 'fin':
			break
		#perdida de paquete rompe, poner en header num de seq
		f.write(data_r)
	print("Termino de recibir el archivo")
	f.close()



def start_server(server_address, storage_dir):
	# TODO: Implementar UDP server
	print('UDP: start_server({}, {})'.format(server_address, storage_dir))

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(server_address)

	"""
	#Three-way-Handshake

	try:
		seq_r, ack_r, tam_r, data_r, addr = recibir_mensaje(s)
		seq_e = 0
		tam_e = 0
		tam_e = 0
		data_e = ''
		if data_r == "inicio":
			ack_e = seq_r
			mandar_mensaje(s,addr,seq_e,ack_e,tam_e,data_e)
			esperado = seq_e
			seq_r, ack_r, tam_r, data_r, addr = recibir_mensaje(s)
			if( ack_r != esperado):
				raise Exeption("Problema ACK sincronizaciion")
			seq_e += 1
	except socket.timeout:
		print("Timeout sincronizacion")
		sys.exit(1)
	"""

	#Recivo comando
	seq_r, ack_r, tam_r, codigo, addr = recibir_mensaje(s)

	seq_e = 0
	ack_e = seq_r
	tam_e = 0
	data_e = ''
	mandar_mensaje(s,addr,seq_e,ack_e,tam_e,data_e)
	seq_e += 1

	#Recivo nombre de archivo
	seq_r, ack_r, tam_r, nombre, addr = recibir_mensaje(s)
	print(nombre)
	seq_e = 0
	ack_e = seq_r
	tam_e = 0
	data_e = ''
	mandar_mensaje(s,addr,seq_e,ack_e,tam_e,data_e)
	seq_e += 1


	if codigo == "upl":
		upload(s,storage_dir+'/'+nombre)


	s.close()
