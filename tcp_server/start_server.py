from socket import socket
import struct



def download(storage_dir,nombre,conn):
	print("Enviando Archivo")
	print(storage_dir + "/" + nombre.decode('utf-8'))
	f = open(storage_dir + "/" + nombre.decode('utf-8'), "rb")

	content = f.read(1024)

	while content:
		# Enviar contenido.
		print("Largo siguiente paquete:" + str(len(content)))
		conn.send(struct.pack('!i', len(content)))
		conn.send(content)
		content = f.read(1024)



		# Se utiliza el caracter de código 1 para indicar
		# al cliente que ya se ha enviado todo el contenido.
	try:
		print("Informando Fin de Archivo")
		conn.send(struct.pack('!i', 1))
		conn.send(chr(1))
	except TypeError:
		# Compatibilidad con Python 3.
		conn.send(bytes(chr(1), "utf-8"))

	# Cerrar conexión y archivo.
	f.close()



def upload(storage_dir,nombre,conn):
	print("Recibiendo Archivo")
	print("Destino" + storage_dir + "/" + nombre.decode('utf-8'))
	f = open(storage_dir + "/" + nombre.decode('utf-8'), "wb")

	end = False;
	while not end:
		try:
	  		# Recibir datos del cliente.
			largo = conn.recv(4)
			largo = struct.unpack('!i', largo[:4])[0]
			print("Largo Paquete por recibir" + str(largo))
			input_data = conn.recv(largo)
			# print("recibido" + input_data.decode('utf-8'))
		except error:
			print("Error de lectura.")
			break

		if input_data:
			# Compatibilidad con Python 3.
			if isinstance(input_data, bytes):
				# print("FinArchivo")
				end = input_data[0] == 1
			else:
				end = input_data == chr(1)

			if not end:
	    			# Almacenar datos.
	    			f.write(input_data)
	print("El archivo se ha recibido correctamente.")
	f.close()


def start_server(server_address, storage_dir):
	# TODO: Implementar TCP server
	print('TCP: start_server({}, {})'.format(server_address, storage_dir))


	s = socket()

	# Escuchar peticiones en el puerto 6030.
	s.bind((server_address[0], server_address[1]))
	s.listen(0)

	conn, addr = s.accept()

	modo = conn.recv(3)
	print("Modo: " + modo.decode('utf-8'))

	largo = conn.recv(4)
	largo = struct.unpack('!i', largo[:4])[0]
	print("Largo Nombre: " + str(largo))

	nombre = conn.recv(largo)
	print("Nombre: " + nombre.decode('utf-8'))

	if modo.decode('utf-8') == "upl":
		upload(storage_dir,nombre,conn)
	else:
		download(storage_dir,nombre,conn)
		print("El archivo ha sido enviado correctamente.")

	conn.close()
	s.close()
	pass
