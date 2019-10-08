import socket

def start_server(server_address, storage_dir):
	# TODO: Implementar UDP server
	print('UDP: start_server({}, {})'.format(server_address, storage_dir))
  
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(server_address)
	
