def ip_checksum(data):  # Form the standard IP-suite checksum
    pos = len(data)
    if pos & 1:  # If odd...
        pos -= 1
        sum = ord(data[pos])  # Prime the sum with the odd end byte
    else:
        sum = 0
    # Main code: loop to calculate the checksum
    while pos > 0:
        pos -= 2
        sum += (ord(data[pos + 1]) << 8) + ord(data[pos])
    sum = (sum >> 16) + (sum & 0xFFFF)
    sum += sum >> 16
    result = (~sum) & 0xFFFF  # Keep lower 16 bits
    result = result >> 8 | ((result & 0xFF) << 8)  # Swap bytes
    return chr(result // 256) + chr(result % 256)


def pack_checksum(packet: str):
    no_sum = packet[: packet.rfind(",") + 1]
    return ip_checksum(no_sum)


def make_pkt(seq: int, data: str):
    main = f"{str(seq)},{data},"
    checksum = ip_checksum(main)
    return f"{main}{checksum}"


def parse_packet(packet: str):
    fields = packet.split(",")
    return dict(zip(["ack", "data", "checksum"], fields))


def is_ack(packet: str, value: int):
    ack_num = parse_packet(packet)["ack"]
    return True if str(value) == ack_num else False


def corrupt(packet: str):
    # try except for trying to parse packet
    try:
        checksum = parse_packet(packet)["checksum"]
    except:
        return True
    return False if checksum == pack_checksum(packet) else True


def notcorrupt(packet: str):
    return not corrupt(packet)


if __name__ == "__main__":
    # x = "0,hello world,"
    # packet = (x + ip_checksum(x)).strip("\r")
    # print(parse_packet(packet))
    # print(ip_checksum(x))
    # print(corrupt(packet))
    print(make_pkt(0, "hello world"))
