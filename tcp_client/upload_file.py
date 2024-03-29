from socket import socket
import struct
import sys


def upload_file(server_address, src, name):
	print('TCP: upload_file({}, {}, {})'.format(server_address, src, name))
	try:
		f = open(src, "rb")
	except:
		sys.exit()

	s = socket()
	s.connect((server_address[0], server_address[1]))

	# Mando el nombre. Asumo que el nombre mide menos de 1024
	s.send("upl".encode())
	s.send(struct.pack('!i', len(name.encode())))
	s.send(name.encode())

	content = f.read(1024)

	while content:
		# Enviar contenido.
		s.send(struct.pack('!i', len(content)))
		s.send(content)
		content = f.read(1024)


	# Se utiliza el caracter de código 1 para indicar
	# al cliente que ya se ha enviado todo el contenido.
	try:
		s.send(struct.pack('!i', 1))
		s.send(chr(1))
	except TypeError:
		# Compatibilidad con Python 3.
		s.send(bytes(chr(1), "utf-8"))

	# Cerrar conexión y archivo.
	s.close()
	f.close()
