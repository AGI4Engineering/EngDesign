module model (
  input clk,
  input resetn,
  input din,
  output logic dout
);

    parameter MODR=0, MOD0=1, MOD1=2, MOD2=3, MOD3=4, MOD4=5, MOD5=6;
    logic [2:0] state;

    always @(posedge clk) begin
        if (!resetn) begin
            state <= MODR;
        end else begin
            case (state)
                MODR: state <= (din ? MOD1 : MOD0);
                MOD0: state <= (din ? MOD1 : MOD0);
                MOD1: state <= (din ? MOD3 : MOD2);
                MOD2: state <= (din ? MOD0 : MOD4);
                MOD3: state <= (din ? MOD2 : MOD1);
                MOD4: state <= (din ? MOD4 : MOD3);
            endcase
        end
    end

    assign dout = (state == MOD0);

endmodule