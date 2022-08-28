#once
#bits 16
#subruledef cond
{
    le  =>  0x1
    l   =>  0x2
    e   =>  0x3
    ne  =>  0x4
    ge  =>  0x5
    g   =>  0x6
}

#ruledef
{
    halt                                    =>  0x00        @ 0x00
    nop                                     =>  0x10        @ 0x00
    mov r{rA: u4}, r{rB: u4}                =>  0x20        @ rA @ rB
    mov{X: cond} r{rA: u4}, r{rB: u4}       =>  0x2 @ X     @ rA @ rB
    irmov {V: i64}, r{rB: u4}               =>  0x30        @ 0xF @ rB      @ V
    rmmov r{rA: u4}, {D: i64}(r{rB: u4})    =>  0x40        @ rA @ rB       @ D
    mrmov {D: i64}(r{rB: u4}), r{rA: u4}    =>  0x50        @ rA @ rB       @ D
    add r{rA: u4}, r{rB: u4}                =>  0x60        @ rA @ rB
    sub r{rA: u4}, r{rB: u4}                =>  0x61        @ rA @ rB
    and r{rA: u4}, r{rB: u4}                =>  0x62        @ rA @ rB
    xor r{rA: u4}, r{rB: u4}                =>  0x63        @ rA @ rB
    mul r{rA: u4}, r{rB: u4}                =>  0x64        @ rA @ rB
    div r{rA: u4}, r{rB: u4}                =>  0x65        @ rA @ rB
    mod r{rA: u4}, r{rB: u4}                =>  0x66        @ rA @ rB
    ;shl r{rA: u4}, r{rB: u4}                =>  0x67        @ rA @ rB
    ;shr r{rA: u4}, r{rB: u4}                =>  0x68        @ rA @ rB
    jmp {D: i64}                            =>  0x70        @ 0xFF          @ D
    j{X: cond} {D: i64}                     =>  0x7 @ X     @ 0xFF          @ D
    call {D: i64}                           =>  0x80        @ 0xF4          @ D
    ret                                     =>  0x90        @ 0xF4
    push r{rA: u4}                          =>  0xA0        @ rA @ 0x4
    pop r{rA: u4}                           =>  0xB0        @ rA @ 0x4

    ; "Hidden" instructions
    call {D: i64}, r{rB: u4}                =>  0x80        @ 0xF @ rB          @ D
    ret r{rB: u4}                           =>  0x90        @ 0xF @ rB
    push r{rA: u4}, r{rB: u4}               =>  0xA0        @ rA @ rB
    pop r{rA: u4}, r{rB: u4}                =>  0xB0        @ rA @ rB

    ; Macros
    initstack                               =>  0x30        @ 0xF4          @ 0x0000_0000_00ff_fffc
    initstack 5                             =>  0x30        @ 0xF5          @ 0x0000_0000_00ef_fffc
    initstack 6                             =>  0x30        @ 0xF6          @ 0x0000_0000_00df_fffc
    initstack 7                             =>  0x30        @ 0xF7          @ 0x0000_0000_00cf_fffc
}

;; Prelude
initstack
