module divisible_by_5 (
    input  logic clk,       // clock signal
    input  logic resetn,    // synchronous, active‐low reset: clears history
    input  logic din,       // serial input bit, MSB first
    output logic dout       // high if the current value mod 5 == 0
);

    // State encoded for remainders 0 to 4
    typedef enum logic [2:0] {
        REMAINDER_0 = 3'd0,
        REMAINDER_1 = 3'd1,
        REMAINDER_2 = 3'd2,
        REMAINDER_3 = 3'd3,
        REMAINDER_4 = 3'd4
    } remainder_t;

    remainder_t state, next_state;

    // Combinational logic to determine next state
    always_comb begin
        case (state)
            REMAINDER_0: next_state = din ? REMAINDER_1 : REMAINDER_0;
            REMAINDER_1: next_state = din ? REMAINDER_3 : REMAINDER_2;
            REMAINDER_2: next_state = din ? REMAINDER_0 : REMAINDER_4;
            REMAINDER_3: next_state = din ? REMAINDER_2 : REMAINDER_1;
            REMAINDER_4: next_state = din ? REMAINDER_4 : REMAINDER_3;
            default:     next_state = REMAINDER_0; // Fault recovery
        endcase
    end

    // Synchronous state update logic
    always_ff @(posedge clk) begin
        if (!resetn) begin
            state <= REMAINDER_0; // Reset state
            dout <= 1'b0;         // Reset output
        end else begin
            state <= next_state;  // Update state
            dout <= (next_state == REMAINDER_0) ? 1'b1 : 1'b0; // Set output
        end
    end

endmodule
