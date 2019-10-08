from socket import socket
import struct

def download_file(server_address, name, dst):
	print('TCP: download_file({}, {}, {})'.format(server_address, name, dst))
	s = socket()
	s.connect((server_address[0], server_address[1]))

	# Mando el nombre. Asumo que el nombre mide menos de 1024
	s.send("dow".encode())
	s.send(struct.pack('!i', len(name.encode())))
	s.send(name.encode())
	print(name)

	f = open(dst, "wb")

	end = False;
	while not end:
		try:
	  		# Recibir datos del cliente.
			largo = s.recv(4)
			largo = struct.unpack('!i', largo[:4])[0]
			print("Largo Paquete por recibir" + str(largo))
			input_data = s.recv(largo)

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
