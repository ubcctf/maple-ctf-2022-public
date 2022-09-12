from scapy.all import *
from scapy.layers.usb import *
from Crypto.Cipher import AES, ARC4

#from challdriver
rc4key = bytes([0x4f, 0x5e, 0xc2, 0x35, 0x55, 0xa6, 0x7b, 0xe2, 0x53, 0x15, 0x17, 0x43, 0x8f, 0x96, 0xc4, 0x6f, 0x7f, 0x65, 0x2a, 0x74, 0x29, 0xc4, 0xb3, 0xb6, 0x08, 0x71, 0x52, 0xd9, 0x15, 0x7d, 0xd0, 0x98, 0x0a, 0x32, 0xa9, 0xee, 0xdf, 0xa3, 0x54, 0xe2, 0x67, 0x14, 0xf5, 0x78, 0x9b, 0x1c, 0xe3, 0x8d])
encstr = bytes([0xf9, 0x7a, 0x85, 0x17, 0x1c, 0xc1, 0x5a, 0xd7, 0x1f, 0xfa, 0xa5, 0x8b, 0xf0, 0xfe, 0xbe, 0x69, 0x06, 0xe8, 0x8e, 0x6e, 0x44, 0x66, 0xa6, 0x6b, 0xf1, 0x3e, 0x2e, 0xf2, 0xca, 0xe7, 0xa4, 0x95, 0x7c, 0x82, 0xa5, 0x15, 0x5b, 0x00, 0xda, 0x87, 0xa8, 0xdd, 0x15, 0x3e, 0x9e, 0x8a, 0x4d, 0x46])

#obtain strs for use as initial value in CTR mode (strs is mainly used for LoadLibrary/GetProcAddress though)
c = ARC4.new(rc4key)
strs = c.decrypt(encstr)
print(strs)



pcap = rdpcap('log.pcap')

#get all packets that has opcode 0x0727 signifying server-side handshake start (ignoring HID data which is 1 control transfer stage + 8 bytes setup data)
s2c = [p[USBpcap] for p in pcap if bytes(p[USBpcap].payload)[9:].startswith(b'\x27\x07')]

#since responses are all encrypted the only thing we can work with is the device id
id = s2c[0].device

#fetch all responses (in the form of interrupts) from the device with the id we obtained in the handshake starts
c2s = [p[USBpcap] for p in pcap if p[USBpcap].device == id and p[USBpcap].transfer == 0x01 and len(p[USBpcap].payload) == 64]    #we know from rawhid_recv in challdriver that valid packet sizes are 64 bytes long

assert len(s2c) - 1 == len(c2s)    #should be one request one response
#note: s2c will have 1 more packet since client emulation stops responding when it finishes injecting the commands
#but this is unnecessary information for solving the chall - normal real life captures will likely have unbalanced request/responses due to pcap cutting off mid way anyway


#obtain injected commands
cmds = []

for req, res in zip(s2c, c2s):
    secret = bytes(req.payload)[11:15]    #ignore HID setup data (9 bytes) and opcode (2 bytes), and also ignore all the remaining bytes since they are junk
    decoded = bytes([secret[i % len(secret)] ^ v for i, v in enumerate(bytes(res.payload))])  #decode by xoring secret given in handshake just like in challdriver
    if decoded.startswith(b'\xf0\x0f'):    #only backdoor operations interest us - this is obvious once one has reversed challdriver enough that they realize 0x0ff0 (little endian) calls CreateProcessA instead of SendInput
        aes = AES.new(decoded[:32], AES.MODE_CTR, initial_value=strs[32:], nonce=b"")    #CTR mode as shown in challdriver; strs is used as "iv" and first half of the packet is used as key
        cmds += [aes.decrypt(decoded[32:])]


#extract flag from cmds (running the cmds directly in windows will also yield you a flag in the "conf" file)
for cmd in cmds:
    print(chr(cmd[23]), end="")