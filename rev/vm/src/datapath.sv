module data_path(clk,rst,
                data_select,
                return_top,
                ALU_op,z,
                data_stack_write_en,ret_stack_write_en,
                data_stack_op,ret_stack_op,
                push_data,ret_push_data,
                data_stack_top,data_stack_next);
    input clk,rst,data_select,data_stack_write_en,ret_stack_write_en;
    input [7:0] push_data,ret_push_data;
    input [2:0] data_stack_op,ret_stack_op;
    output logic [7:0] return_top,data_stack_top,data_stack_next;
    input [2:0] ALU_op;
    output wire z;
    
    wire [7:0] data_in, ALU_out,data_top, data_next, return_next;

    assign data_in = data_select == 0 ? push_data : ALU_out;
    assign data_stack_top = data_top;
    assign data_stack_next = data_next;

    stack #(10) data_stack(.clk(clk),.rst(rst),
                        .data_in(data_in),
                        .stack_top(data_top),.stack_next(data_next),
                        .op(data_stack_op),.en(data_stack_write_en));

    stack #(10) return_stack(.clk(clk),.rst(rst),
                            .data_in(ret_push_data),
                            .stack_top(return_top),.stack_next(return_next),
                            .op(ret_stack_op),.en(ret_stack_write_en));

    ALU ALU(data_top,data_next,ALU_op,ALU_out,z);




endmodule

module stack(clk,rst,data_in,stack_top,stack_next,op,en);
    input clk,rst,en;
    
    input [7:0] data_in;
    output [7:0] stack_top,stack_next;
    input [2:0] op;

    parameter address_width = 16;
    logic [7:0] ram [2**address_width-1:0];
    logic [address_width-1:0] address;


    always_ff @(posedge clk) begin
        if (rst == 1) begin
            address <= 0;
        end else if (en ==1) begin
            case (op)
                3'd0: begin
                        ram[address+1] <= data_in;
                        address <= address + 1;
                end
                3'd1: ram[address]<=data_in;
                3'd2: address <= address - 2;
                3'd3: begin 
                        address <= address - 1; 
                        ram[address-1] <= data_in;
                end
                3'd4: address <= address - 1;
            endcase
        end
    end

    assign {stack_top,stack_next} = {ram[address],ram[address-1]};

endmodule

module ALU(a,b,op,out,z);
    input [7:0] a,b;
    output logic [7:0] out;
    input [2:0] op;
    output z;

    assign z = out == 0 ? 1'b1 : 1'b0;

    always_comb begin
        case (op)
            3'd0: out = a + b;
            3'd1: out = a - b;
            3'd2: out = a ^ b;
            3'd3: out = a & b;
            3'd4: out = a | b;
            3'd5: out = a << b;
            3'd6: out = a >> b;
            default: out = 8'bz;
        endcase
    end
endmodule

