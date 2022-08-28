import sys

ops = {
    "ADD":"0",
    "SUBTRACT":"1",
    "XOR":"2",
    "AND":"3",
    "OR":"4",
    "LS":"5",
    "RS":"6",
    "POP":"7",
    "JMP":"8",
    "CALL":"9",
    "RET":"A",
    "JZ":"B",
    "PUSH":"C",
    "LOAD":"D",
    "STORE":"E",
    "HALT":"F",
}

with open(sys.argv[1], "r") as f:
    g = open(sys.argv[2], "w")
    for line in f:
        s = line.strip().split(" ")
        op = ops.get(s[0].upper().strip())
        if len(s) >= 2:
            if s[1][0] not in "1234567890":
                operand = "00"
            else:
                operand = hex(int(s[1].strip()))[2:]
                operand = operand.rjust(2, '0')
        else:
            operand = "00"
        g.write(op+operand+" ")
