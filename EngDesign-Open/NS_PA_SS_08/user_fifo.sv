module target_sequence_detector #(
    parameter TARGET_WIDTH = 5
) (
    input  logic               clk,      // clock signal
    input  logic               resetn,   // synchronous, active-low reset
    input  logic [TARGET_WIDTH-1:0] init,// target sequence, loaded on reset
    input  logic               din,      // serial input bit
    output logic               seen      // pulses high for one cycle on match
);

    // Internal registers
    logic [TARGET_WIDTH-1:0] target_reg;  // Holds the target pattern
    logic [TARGET_WIDTH-1:0] shift_reg;   // Holds the current shifted bits

    // Synchronous logic
    always_ff @(posedge clk) begin
        if (!resetn) begin
            // On reset, load init into target_reg and clear shift_reg
            target_reg <= init;
            shift_reg <= '0; // Clear the shift register
            seen <= 0;
        end else begin
            // Shift in the new bit into the shift register from the left
            shift_reg <= {shift_reg[TARGET_WIDTH-2:0], din};
            
            // Compare shift_reg with target_reg
            if (shift_reg == target_reg) begin
                seen <= 1;
            end else begin
                seen <= 0;
            end
        end
    end

endmodule