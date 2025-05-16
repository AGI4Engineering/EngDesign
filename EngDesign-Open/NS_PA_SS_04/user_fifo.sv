module fibonacci_lfsr #(
    parameter int DATA_WIDTH = 8
) (
    input  logic                   clk,      // clock signal
    input  logic                   resetn,   // synchronous, active-low reset
    input  logic [DATA_WIDTH-1:0]  din,      // initial seed value written on reset
    input  logic [DATA_WIDTH-1:0]  tap,      // feedback polynomial (tap positions)
    output logic [DATA_WIDTH-1:0]  dout      // current LFSR output
);

    logic [DATA_WIDTH-1:0] shift_reg;
    logic [DATA_WIDTH-1:0] tap_reg;

    always_ff @(posedge clk) begin
        if (!resetn) begin
            // Load the shift register with din on reset, set dout to 1
            shift_reg <= din;
            dout <= 'b1;
            // Register the tap pattern for use until the next reset
            tap_reg <= tap;
        end else begin
            // Compute the feedback as XOR of tapped positions
            logic feedback;
            feedback = ^(shift_reg & tap_reg); // XOR of selected bits
            // Shift right and insert feedback into MSB position
            shift_reg <= {feedback, shift_reg[DATA_WIDTH-1:1]};
            // Update the output
            dout <= shift_reg;
        end
    end

endmodule