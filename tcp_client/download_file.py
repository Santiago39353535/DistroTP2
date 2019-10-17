from socket import socket
import struct
import sys

def download_file(server_address, name, dst):
	print('TCP: download_file({}, {}, {})'.format(server_address, name, dst))
	s = socket()
	s.connect((server_address[0], server_address[1]))

	# Mando el nombre. Asumo que el nombre mide menos de 1024
	s.send("dow".encode())
	s.send(struct.pack('!i', len(name.encode())))
	s.send(name.encode())


	try:
		f = open(dst, "wb")
	except:
		sys.exit()

	end = False;
	while not end:
		try:
	  		# Recibir datos del cliente.
			largo = s.recv(4)
			largo = struct.unpack('!i', largo[:4])[0]
			input_data = s.recv(largo)

		except:
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
