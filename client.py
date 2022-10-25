import socket
import sys
from check import *
from time import sleep
import threading
from random import randint

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print("Failed to create socket")

host = "localhost"
port = 9822


def send_with_timeout_corruption(sock, packet, timeout):
    t = threading.current_thread()
    while getattr(t, "run", True):
        if randint(0, 10) < 8:
            print(f"Corrupting packet {packet}...")
            temp = packet + "l"
            sock.sendto(temp.encode("utf-8"), (host, port))
        else:
            sock.sendto(packet.encode("utf-8"), (host, port))
        sleep(timeout)
        if getattr(t, "run", True):
            print(f'Timeout reached for packet "{packet}". resending...')


def send_with_timeout(sock, packet, timeout):
    t = threading.current_thread()
    while getattr(t, "run", True):
        sock.sendto(packet.encode("utf-8"), (host, port))
        sleep(timeout)
        if getattr(t, "run", True):
            print(f'Timeout reached for packet "{packet}". resending...')


def start_thread(target, args):
    return threading.Thread(target=target, args=args)


while True:
    ########################### WAIT FOR CALL 0 FROM ABOVE ###########################
    # rdt_send(data)
    # this is basically the rdt_rcv loop
    data = input("Enter message to send. Press enter to exit: ")
    if not data:
        s.sendto(b"", (host, port))
        break
    packet = make_pkt(0, data)
    print(
        f"Message[Client] - \n\t\t\tPacket: {packet}\n\t\t\tData: {parse_packet(packet)['data']}\n\t\t\tAck: {parse_packet(packet)['ack']}"
    )
    # udt_send(sndpkt) and start_timer
    thread = start_thread(send_with_timeout, (s, packet, 1))
    thread.start()

    ########################### WAIT FOR ACK 0 ###########################
    # rdt_rcv(rcvpkt)
    d = s.recvfrom(1024)
    reply = d[0].decode("utf-8")
    addr = d[1]
    # corrupt(rcvpkt) || isACK(rcvpkt, 1)
    while corrupt(reply) or is_ack(reply, 1):
        d = s.recvfrom(1024)
        reply = d[0].decode("utf-8")
        addr = d[1]
    print(
        f"Message[Server] - \n\t\t\tPacket: {reply}\n\t\t\tData: {parse_packet(reply)['data']}\n\t\t\tAck: {parse_packet(reply)['ack']}"
    )
    if not (notcorrupt(packet) and is_ack(packet, 0)):
        print("logic error somewhere")
        sys.exit()
    # stop_timer
    thread.run = False

    ########################### WAIT FOR CALL 1 FROM ABOVE ###########################
    # rdt_send(data)
    data = input("Enter message to send. Press enter to exit: ")
    if not data:
        s.sendto(b"", (host, port))
        break
    packet = make_pkt(1, data)
    print(
        f"Message[Client] - \n\t\t\tPacket: {packet}\n\t\t\tData: {parse_packet(packet)['data']}\n\t\t\tAck: {parse_packet(packet)['ack']}"
    )

    # udt_send(sndpkt) and start_timer
    # thread = start_thread(send_with_timeout, (s, packet, 1))
    print("DEMO PART 2: PACKET LOSS")
    thread = start_thread(send_with_timeout_corruption, (s, packet, 1))
    thread.start()

    ########################### WAIT FOR ACK 1 ###########################
    # rdt_rcv(rcvpkt)
    d = s.recvfrom(1024)
    reply = d[0].decode("utf-8")
    addr = d[1]
    # corrupt(rcvpkt) || isACK(rcvpkt, 1)
    while corrupt(reply) or is_ack(reply, 0):
        d = s.recvfrom(1024)
        reply = d[0].decode("utf-8")
        addr = d[1]
    print(
        f"Message[Server] - \n\t\t\tPacket: {reply}\n\t\t\tData: {parse_packet(reply)['data']}\n\t\t\tAck: {parse_packet(reply)['ack']}"
    )
    if not (notcorrupt(packet) and is_ack(packet, 1)):
        print("logic error somewhere")
        sys.exit()

    # stop_timer
    thread.run = False
