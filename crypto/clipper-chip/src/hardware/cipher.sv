module lfsr
  #(parameter SIZE = 4, parameter POLYNOMIAL = 'hc)
   (input clk, nrst, mode, seed, output out);

   reg [SIZE-1:0] stages;

   assign out = stages[0];

   always @(posedge clk)
     if (nrst) begin
        stages[SIZE-1] <= mode ? seed : stages[0];
        for (int i = SIZE-2; i >= 0; i--)
          stages[i] <= ((POLYNOMIAL[i] & ~mode) ? stages[0] : 1'b0) ^ stages[i+1];
     end
endmodule // lfsr

module cipher
  (input  clk, nrst, mode, in,
   output out);

   wire   a, b, c;
   wire   k = (a&b) | (a&c) | (b&c);

   assign out = in ^ k;

   lfsr #(17, 'h100ab)    REG0(.seed(in), .out(a), .*);
   lfsr #(19, 'h40112)    REG1(.seed(a), .out(b), .*);
   lfsr #(31, 'h40000576) REG2(.seed(b), .out(c), .*);
endmodule // cipher
