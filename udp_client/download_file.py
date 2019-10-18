import socket
CHUNK_SIZE = 1024
RECV = 1500

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
	return (inicio,fin,seq,ack,tam,data)


def download_file(server_address, name, dst):
    # TODO: Implementar UDP download_file client
    print('UDP: download_file({}, {}, {})'.format(server_address, name, dst))

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #"3"wayhandshake

    inicio = 1
    fin = 0
    seq_e = 0
    ack_e = 0
    tam_e = 3 + len(name)
    data_e = 'dow' + name

    s.settimeout(0.1)
    time_outs_consecutivos = 0

    while True:
        try:
            mandar_mensaje(s,server_address,inicio,fin,seq_e,ack_e,tam_e,data_e)
            esperado = seq_e

            inicio_r, fin_r, seq_r, ack_r, tam_r, data_r = recibir_mensaje(s)
            if inicio == 1 and  ack_r == esperado:
                ack_e = seq_r
                seq_e += 1
                break
            else:
                print("falla en protocolo entre conexiones")
                sys.exit(1)
        except socket.timeout:
            time_outs_consecutivos += 1
            if time_outs_consecutivos == 1000:
                print("Problema de sincronizacion con el servidor")
                sys.exit(1)

    print("Se empieza a recivir el archivo")
    f = open(dst, "w")
    inicio = 0
    fin = 0
    seq_e = seq_e#1
    ack_e = 0#0
    tam_e = 0
    data_e = ''
    segmentos_recibidos = 1

    while True:
        try:
            mandar_mensaje(s,server_address,inicio,fin,seq_e,ack_e,tam_e,data_e)
            seq_esperado = seq_e

            inicio_r, fin_r, seq_r, ack_r, tam_r, data_r = recibir_mensaje(s)

            time_outs_consecutivos = 0
            ack_e = seq_r

            if fin_r == 1:# falta avisar ack del fin?
                f.write(data_r)
                break

            if seq_esperado == seq_r:
                seq_e += 1
                segmentos_recibidos += 1
                f.write(data_r)
                seq_esperado = seq_r+1

        except socket.timeout:
            time_outs_consecutivos += 1
            #f.seek((segmentos_recibidos - 1)*tam_r)
            if time_outs_consecutivos == 1000:
                print("Se perdio coneccion con el cliente")
                sys.exit(1)

    print("Termino de recibir el archivo")
    f.close()

    #end
    inicio_e = 0
    fin_e = 1
    seq_e = seq_e
    ack_e = ack_e
    tam_e = 0
    data_e = ''
    esperado = seq_e

    while True:
        try:
            mandar_mensaje(s,server_address,inicio_e,fin_e,seq_e,ack_e,tam_e,data_e)
            inicio_r, fin_r, seq_r, ack_r, tam_r, data_r = recibir_mensaje(s)
            if fin_r == 1:
                break
        except socket.timeout:
            time_outs_consecutivos += 1
            if time_outs_consecutivos == 1000:
                break
    s.close()
