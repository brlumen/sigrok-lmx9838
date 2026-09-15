# Generates a two-channel (bit0=RX, bit1=TX) UART stream, 8N1, 10 samples per bit.
import struct
SPB = 10
def uart_bits(data):
    bits = []
    for b in data:
        bits += [0] + [(b >> i) & 1 for i in range(8)] + [1, 1]
    return [x for bit in bits for x in [bit] * SPB]

def pkt(pt, op, data):
    l = len(data)
    cs = (pt + op + (l & 0xFF) + (l >> 8)) & 0xFF
    return bytes([0x02, pt, op, l & 0xFF, l >> 8, cs]) + bytes(data) + b'\x03'

tx = pkt(0x52, 0x05, []) + pkt(0x52, 0x0A, [1, 0x89, 0xFE, 0x34, 0xE4, 0x18, 0x00, 1]) \
   + pkt(0x52, 0x0F, [1, 3, 0, 0x41, 0x42, 0x43]) + pkt(0x52, 0x11, [1]) + pkt(0x52, 0x26, [])
rx = pkt(0x69, 0x25, [4] + list(b'0210')) + pkt(0x43, 0x05, [0, 0x89, 0xFE, 0x34, 0xE4, 0x18, 0x00]) \
   + pkt(0x69, 0x0B, [0, 0x89, 0xFE, 0x34, 0xE4, 0x18, 0x00, 1, 1]) \
   + pkt(0x69, 0x10, [1, 3, 0, 0x31, 0x32, 0x33]) + bytes([0x02, 0x43, 0x11, 2, 0, 0x99, 0, 1, 0x03])  # bad checksum
rxb, txb = [1] * 50 + uart_bits(rx), [1] * 50 + uart_bits(tx)
n = max(len(rxb), len(txb)) + 20 * SPB
rxb += [1] * (n - len(rxb)); txb += [1] * (n - len(txb))
open('test.bin', 'wb').write(bytes(r | (t << 1) for r, t in zip(rxb, txb)))
