module dot_product #(parameter WIDTH = 8) (
    input logic [WIDTH-1:0] din,   // 8-bit unsigned input words
    input logic clk,              // clock signal
    input logic resetn,           // synchronous, active-low reset
    output logic [17:0] dout,     // 18-bit unsigned output
    output logic run              // output valid signal
);

    // Internal registers
    logic [WIDTH-1:0] a [0:2]; // registers for a1, a2, a3
    logic [WIDTH-1:0] b [0:2]; // registers for b1, b2, b3
    logic [2:0] count;          // 3-bit counter to track input sequence

    // Synchronous logic
    always_ff @(posedge clk or negedge resetn) begin
        if (!resetn) begin
            // Reset logic
            count <= 3'b0;
            a[0] <= '0;
            a[1] <= '0;
            a[2] <= '0;
            b[0] <= '0;
            b[1] <= '0;
            b[2] <= '0;
            dout <= 18'b0;
            run <= 1'b1; // Assert run because 0·0=0
        end else begin
            // Normal operation
            run <= 1'b0;
            case (count)
                3'd0: a[0] <= din; // Capture a1
                3'd1: a[1] <= din; // Capture a2
                3'd2: a[2] <= din; // Capture a3
                3'd3: b[0] <= din; // Capture b1
                3'd4: b[1] <= din; // Capture b2
                3'd5: begin
                    b[2] <= din; // Capture b3
                    // Compute dot product and assert run
                    dout <= a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
                    run <= 1'b1;
                end
            endcase
            count <= (count == 3'd5) ? 3'd0 : count + 3'd1; // Increment or reset counter
        end
    end

endmodule