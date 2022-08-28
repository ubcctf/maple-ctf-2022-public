module cpu(clk,rst,
        instr_in,PC,
        mem_write_addr,mem_in,mem_write,
        mem_read_addr,mem_out);

    input clk, rst;
    input [11:0] instr_in;
    input [7:0] mem_out;
    output logic [7:0] PC;
    output wire [7:0] mem_write_addr,mem_read_addr,mem_in;
    output logic mem_write;

    wire [7:0] data_stack_top,data_stack_next;

    logic data_stack_write_en,ret_stack_write_en;
    logic [2:0] data_stack_op,ret_stack_op;
    logic [2:0] ALU_op;

    wire [3:0] opcode;
    wire [7:0] operand,jmp_addr,push_data,return_addr,ret_push_data;
    logic ret,stack_data,data_select,zero,set_zero;
    logic [7:0] next_pc;

    typedef enum {RESET_PC,JMP_PC,NORMAL_PC,HALT} PC_SEL_T;
    PC_SEL_T pc_sel;

    enum {FETCH,EXECUTE} state;

    data_path dt(clk,rst,
                data_select,
                return_addr,
                ALU_op,is_zero,
                data_stack_write_en,ret_stack_write_en,
                data_stack_op,ret_stack_op,
                push_data,ret_push_data,
                data_stack_top,data_stack_next);

    assign opcode = instr_in[11:8];
    assign operand = instr_in[7:0];
    assign jmp_addr = ret == 0 ? operand : return_addr;
    assign mem_write_addr = data_stack_next;
    assign mem_read_addr = data_stack_top;
    assign push_data = stack_data == 1 ? operand : mem_out;
    
    assign mem_in = data_stack_top;
    assign ret_push_data = PC + 1;
    
    always_comb begin
        data_select = 1'b0;
        data_stack_write_en = 1'b0;
        ret_stack_write_en = 1'b0;
        data_stack_op = 3'b0;
        ret_stack_op = 3'b0;
        pc_sel = NORMAL_PC;
        ret = 1'b0;
        stack_data = 1'b1;
        mem_write = 1'b0;
        set_zero = 1'b0;
        if (state == EXECUTE) begin
        casez(opcode)
            4'b0???: begin
                    if (opcode != 7) begin
                        data_select = 1'b1;
                        ALU_op = opcode[2:0];
                        data_stack_write_en = 1'b1;
                        data_stack_op = 3'd3;
                        set_zero = 1'b1;
                    end else begin
                        data_stack_write_en = 1'b1;
                        data_stack_op = 3'd4;
                        end
                    end
            4'd8: begin
                    pc_sel = JMP_PC;
                    ret = 1'b0;
                    end
            4'd9: begin
                    pc_sel = JMP_PC;
                    ret_stack_write_en = 1'b1;
                    ret_stack_op = 3'd0;
                    ret = 1'b0;
                    end
            4'd10: begin
                    pc_sel = JMP_PC;
                    ret_stack_write_en = 1'b1;
                    ret_stack_op = 3'd4;
                    ret = 1'b1;
                    end
            4'd11: begin
                    ret = 1'b0;
                    if(zero)
                        pc_sel = JMP_PC;
                    else
                        pc_sel = NORMAL_PC;
                    end
            4'd12: begin
                    data_select = 1'b0;
                    data_stack_write_en = 1'b1;
                    data_stack_op = 3'b0;
                    end
            4'd13: begin
                    data_stack_op = 3'd1;
                    data_select = 1'b0;
                    stack_data = 1'b0;
                    data_stack_write_en = 1'b1;
                    end
            4'd14: begin
                    mem_write = 1'b1;
                    data_stack_op = 3'd2;
                    data_stack_write_en = 1'b1;
            end
            4'd15: pc_sel = HALT;
        endcase
        end
    end

    
    always_comb begin
        case(pc_sel)
            RESET_PC: next_pc = 8'b0;
            JMP_PC: next_pc = jmp_addr;
            NORMAL_PC: next_pc = PC + 1;
            HALT: next_pc = PC;
            default: next_pc = 8'bz;
        endcase
    end

    always_ff @(posedge clk) begin
        if (rst) begin
            PC <= 8'b0;
        end
        else begin
            if (state == EXECUTE)
                PC <= next_pc;
            if (set_zero == 1)
                zero = is_zero;
        end
    end

    always_ff @(posedge clk) begin
        if (rst)
            state <= FETCH;
        else begin
            case(state)
                FETCH: state <= EXECUTE;
                EXECUTE: state <= FETCH;
            endcase
        end
    end


endmodule
