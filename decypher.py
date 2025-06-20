
import dvdpy.lfsr
import dvdpy.ecma_267

def decode(values, cypher):

    decoded = []
    for b in range(2048):
        decoded.append(values[12 + b] ^ cypher[b])
    decoded = values[:12] + bytes(decoded)

    data_edc = dvdpy.ecma_267.calc_edc(decoded)
    disc_edc = int.from_bytes(values[-4:], 'big')
    if data_edc != disc_edc:
        raise ValueError("Bad EDC")

    return decoded + values[-4:]

f = open("test.bin", "rb")

# first sector
sector0 = f.read(2064)

cypher = None
for seed in range(0, 0x7FFF): 
    cypher = dvdpy.lfsr.generate_cypher(seed, 2048)

    try:
        decode(sector0, cypher)
        print("Seed is %x" % seed)
        break
    except ValueError:
        continue

f.seek(0)
for i in range(16):
    data = decode(f.read(2064), cypher)
    for j in range(20):
        print(" %02x" % data[j], end='')
    print()

f.close()


