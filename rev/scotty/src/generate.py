#!/usr/bin/env python3

flag = "maple{7h4nk_y0u_4l0nz0_church.DwRVwXLKnlMQFnw5}"

def gen_int(n):
    def go(n):
        if n == 0:
            return "z"
        elif n & 1:
            return f"p1s ({go(n >> 1)})"
        else:
            return f"s ({go(n >> 1)})"
    return f"I $ \z s p1s -> {go(n)}"

def gen_flag(f):
    if f == "":
        return "n"
    else:
        return f"c ({gen_int(ord(f[0]))}) ({gen_flag(f[1:])})"

print(f"flag = L $ \\n c -> {gen_flag(flag)}")
