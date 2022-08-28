module tb;
   reg       clk, nrst;
   reg       in, mode;
   wire      out;

   cipher DUT(.*);

   initial forever begin
      clk = 'b0;
      #5;
      clk = 'b1;
      #5;
   end

   task loadkey(input [66:0] key);
      mode = 1'b1;
      for (int i = 66; i >= 0; i--) begin
         in = key[i];
         #10;
      end
      mode = 1'b0;
      in = 1'bx;
   endtask // loadkey

   task encrypt(input string pt);
      reg [7:0] p;
      reg [7:0] c;
      for (int i = 0; i < pt.len(); i++) begin
         p = pt[i];
         for (int j = 7; j >= 0; j--)  begin
            in = p[j];
            #0 c[j] = out;
            #10;
         end
         $write("%02x", c);
      end
      $display();
   endtask // encrypt

   initial begin
      $dumpvars;
      mode = 1'b0;
      in = 1'b0;
      nrst = 1'b0;
      #10;
      nrst = 1'b1;

      loadkey(67'h383e04e16005dfa29);
      encrypt("flag: maple{c0rr3l4710n_4nd_c4u54710n.HAiBDKZP3Jggoqyb}");

      $finish;
   end
endmodule // tb
