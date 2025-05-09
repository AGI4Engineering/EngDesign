module model #(
    parameter DATA_WIDTH = 8
) (
    input  logic                  clk,      // clock signal
    input  logic                  resetn,   // synchronous, active-low reset
    input  logic [DATA_WIDTH-1:0] din,      // initial seed value written on reset
    input  logic [DATA_WIDTH-1:0] tap,      // feedback polynomial (tap positions)
    output logic [DATA_WIDTH-1:0] dout      // current LFSR output
);

    logic [DATA_WIDTH-1:0] lfsr_reg;
    logic [DATA_WIDTH-1:0] latched_tap;

    always_ff @(posedge clk) begin
        if (!resetn) begin
            lfsr_reg <= din;
            latched_tap <= tap;
            dout <= 8'b1; // Assuming dout = 1 means lfsr_reg initialized 
        end else begin
            logic feedback_bit;
            feedback_bit = ^(lfsr_reg & latched_tap); // Calculate feedback bit
            lfsr_reg <= {feedback_bit, lfsr_reg[DATA_WIDTH-1:1]}; // Shift right and insert feedback bit
            dout <= lfsr_reg; // Update dout
        end
    end

endmodule