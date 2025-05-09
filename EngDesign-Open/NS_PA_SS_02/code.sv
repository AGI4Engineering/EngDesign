module model #(
    parameter DATA_WIDTH = 4
) (
    input logic clk,
    input logic resetn,
    output logic [DATA_WIDTH-1:0] out
);

    logic [DATA_WIDTH-1:0] binary_counter;

    // Sequential logic for Gray code generation
    always_ff @(posedge clk) begin
        if (!resetn) begin
            // Synchronous reset
            binary_counter <= 0;
        end else begin
            // Increment the binary counter and generate Gray code
            binary_counter <= binary_counter + 1;
        end
    end

    // Convert binary counter to Gray code
    assign out = binary_counter ^ (binary_counter >> 1);

endmodule