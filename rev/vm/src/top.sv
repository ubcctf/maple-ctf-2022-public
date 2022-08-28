module top();
    reg clk,rst;
    wire [11:0] instr_in;
    wire [7:0] PC,mem_write_addr,mem_out,mem_read_addr,mem_in;
    wire mem_write;
    string flag;
    integer i;

    initial forever begin
        clk = 0; #5;
        clk = 1; #5;
    end
    
    initial begin
        #1;
        flag = "maple{testflag}";
        for (i=0; i< flag.len(); i++)
            data.ram[i+140] = flag[i];
        rst = 1;
        #10;
        rst = 0;
        #500000;
        if (data.ram[135] == 2)
            $display("You should be winner!");
        else
            $display("Try again.");

    end

    cpu DUT(clk,rst,
        instr_in,PC,
        mem_write_addr,mem_out,mem_write,
        mem_read_addr,mem_in);
    
    RAM #(8,8,"data.txt") data(clk,mem_read_addr,mem_write_addr,mem_write,mem_out,mem_in);
    RAM #(12,8,"prog.txt") instructions(clk,PC,8'b0,1'b0,12'b0,instr_in);
endmodule

module RAM(clk,read_addr,write_addr,write,din,dout);
  parameter data_width = 32; 
  parameter addr_width = 4;
  parameter filename = "data.txt";

  input clk;
  input [addr_width-1:0] read_addr, write_addr;
  input write;
  input [data_width-1:0] din;
  output logic [data_width-1:0] dout;

  reg [data_width-1:0] ram [2**addr_width-1:0];

  initial $readmemh(filename, ram);

  always @ (posedge clk) begin
    if (write)
      ram[write_addr] <= din;
    dout <= ram[read_addr];
  end 
endmodule