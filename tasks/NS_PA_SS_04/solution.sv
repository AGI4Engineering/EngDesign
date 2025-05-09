module model (
    input clk,
    input resetn,
    input [7:0] din,
    input [7:0] tap,
    output [7:0] dout
);

    logic [7:0] tap_ff, lfsr;
    logic tap_out;

    always_ff @(posedge clk) begin
        if (!resetn) begin
            lfsr <= din;  // din gets written to lfsr when in reset mode
            tap_ff <= tap;
        end
        else begin  // shift-register operation + feedback logic
            lfsr <= {lfsr[6:0], tap_out};
            tap_ff <= tap;
        end
    end

    assign tap_out = ^ (lfsr & tap_ff);  // feedback logic
    assign dout = lfsr;

endmodule