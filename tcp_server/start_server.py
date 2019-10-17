from socket import socket
import struct
import sys

import os.path

def download(storage_dir,nombre,conn):

	try:
		f = open(storage_dir + "/" + nombre.decode('utf-8'), "rb")
	except:
		return


	content = f.read(1024)

	while content:
		# Enviar contenido.
		conn.send(struct.pack('!i', len(content)))
		conn.send(content)
		content = f.read(1024)



		# Se utiliza el caracter de código 1 para indicar
		# al cliente que ya se ha enviado todo el contenido.
	try:
		conn.send(struct.pack('!i', 1))
		conn.send(chr(1))
	except TypeError:
		# Compatibilidad con Python 3.
		conn.send(bytes(chr(1), "utf-8"))

	# Cerrar conexión y archivo.
	f.close()



def upload(storage_dir,nombre,conn):
	f = open(storage_dir + "/" + nombre.decode('utf-8'), "wb")

	end = False;
	while not end:
		try:
	  		# Recibir datos del cliente.
			largo = conn.recv(4)
			largo = struct.unpack('!i', largo[:4])[0]
			input_data = conn.recv(largo)
		except error:
			break

		if input_data:
			# Compatibilidad con Python 3.
			if isinstance(input_data, bytes):
				end = input_data[0] == 1
			else:
				end = input_data == chr(1)

			if not end:
	    			# Almacenar datos.
	    			f.write(input_data)
	f.close()


def start_server(server_address, storage_dir):
	# TODO: Implementar TCP server
	print('TCP: start_server({}, {})'.format(server_address, storage_dir))


	s = socket()

	# Escuchar peticiones en el puerto 6030.
	s.bind((server_address[0], server_address[1]))
	s.listen(0)
	while True:
		conn, addr = s.accept()

		modo = conn.recv(3)

		largo = conn.recv(4)
		largo = struct.unpack('!i', largo[:4])[0]

		nombre = conn.recv(largo)

		if modo.decode('utf-8') == "upl":
			upload(storage_dir,nombre,conn)
		else:
			download(storage_dir,nombre,conn)

		conn.close()
	s.close()
	pass
