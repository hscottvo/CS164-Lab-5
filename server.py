import socket
import sys
from _thread import *
from check import *
from time import sleep
from random import randint

host = ""
port = 8888

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("Socket created")
except socket.error as msg:
    print(f"Failed to create socket. Error code: {str(msg[0])} Message {msg[1]}")
    sys.exit()

try:
    s.bind((host, port))
except socket.error as msg:
    print(f"Bind failed. Error code: {str(msg[0])} Message {msg[1]}")
    sys.exit()

print("Socket bind complete")

packet = make_pkt(1, "init")

while True:
    # skip corrupt case for now
    ########################### WAIT FOR 0 ###########################
    d = s.recvfrom(1024)
    print("DEMO PART 3: TIMEOUT")
    sleep(3)
    data = d[0].decode("utf-8")
    addr = d[1]
    if not data:
        sys.exit()
    print(
        f"Message[{str(addr[1])} to {addr[0]}] - \n\t\t\tPacket: {data} \n\t\t\tData: {parse_packet(data)['data']}\n\t\t\tSeq: {parse_packet(data)['ack']}"
    )

    while (notcorrupt(data) and is_ack(data, 1)) or corrupt(data):
        s.sendto(packet.encode("utf-8"), addr)
        d = s.recvfrom(1024)
        data = d[0].decode("utf-8")
        addr = d[1]
        if not data:
            sys.exit()
        print(
            f"Message[{str(addr[1])} to {addr[0]}] - \n\t\t\tPacket: {data} \n\t\t\tData: {parse_packet(data)['data']}\n\t\t\tSeq: {parse_packet(data)['ack']}"
        )

    if not (notcorrupt(data) and is_ack(data, 0)):

        print("logic error somewhere")
        sys.exit()

    packet_data = parse_packet(data)["data"]
    packet = make_pkt(0, "OK..." + packet_data)
    s.sendto(packet.encode("utf-8"), addr)
    print(
        f"Message[{addr[0]} to {str(addr[1])}] - \n\t\t\tPacket: {packet} \n\t\t\tData: {parse_packet(packet)['data']}\n\t\t\tAck: {parse_packet(packet)['ack']}"
    )

    ########################### WAIT FOR 1 ###########################
    d = s.recvfrom(1024)
    data = d[0].decode("utf-8")
    addr = d[1]
    if not data:
        sys.exit()
    print(
        f"Message[{str(addr[1])} to {addr[0]}] - \n\t\t\tPacket: {data} \n\t\t\tData: {parse_packet(data)['data']}\n\t\t\tSeq: {parse_packet(data)['ack']}"
    )

    while (notcorrupt(data) and is_ack(data, 0)) or corrupt(data):
        s.sendto(packet.encode("utf-8"), addr)
        d = s.recvfrom(1024)
        data = d[0].decode("utf-8")
        addr = d[1]
        if not data:
            sys.exit()
        print(
            f"Message[{str(addr[1])} to {addr[0]}] - \n\t\t\tPacket: {data} \n\t\t\tData: {parse_packet(data)['data']}\n\t\t\tSeq: {parse_packet(data)['ack']}"
        )

    packet_data = parse_packet(data)["data"]
    packet = make_pkt(1, "OK..." + packet_data)
    s.sendto(packet.encode("utf-8"), addr)
    print(
        f"Message[{addr[0]} to {str(addr[1])}] - \n\t\t\tPacket: {packet} \n\t\t\tData: {parse_packet(packet)['data']}\n\t\t\tAck: {parse_packet(data)['ack']}"
    )

s.close()
