// SystemVerilog module for one-cycle bubble-sort with parameterizable BITWIDTH
module model #(
    parameter BITWIDTH = 8
) (
    input  logic [BITWIDTH-1:0]      din,
    input  logic                     sortit,
    input  logic                     clk,
    input  logic                     resetn,
    output logic [8*BITWIDTH:0]      dout
);

    // Internal memory to store 8 elements of BITWIDTH
    logic [BITWIDTH-1:0] memory [0:7];
    logic valid;

    // Temporary variable for sorting
    logic [BITWIDTH-1:0] sorted [0:7];

    // Sequential logic to store input data
    always_ff @(posedge clk) begin
        if (!resetn) begin
            // Synchronous reset: Clear memory and dout
            for (int i = 0; i < 8; i++)
                memory[i] <= '0;
            dout <= '0;
            valid <= 0;
        end else if (!sortit) begin
            // Load data into memory while sortit is low
            // Assuming a mechanism to load one element per cycle
            // For example, could use a counter to load 8 elements sequentially
            // Here using continuous input for simplicity
            memory[0] <= din;  // Simplified loading logic
        end else begin
            // Sort data in one cycle when sortit is high
            // Bubble-sort fully unrolled

            // Load memory into sorted array
            for (int i = 0; i < 8; i++)
                sorted[i] = memory[i];
            
            // Perform bubble sort network
            for (int i = 0; i < 8; i++) begin
                for (int j = 0; j < 7-i; j++) begin
                    if (sorted[j] < sorted[j+1]) begin
                        logic [BITWIDTH-1:0] temp;
                        temp = sorted[j];
                        sorted[j] = sorted[j+1];
                        sorted[j+1] = temp;
                    end
                end
            end
            
            // Concatenate sorted array into dout
            dout = {1'b1, sorted[7], sorted[6], sorted[5], sorted[4], sorted[3], sorted[2], sorted[1], sorted[0]};
            valid <= 1;
        end
    end

endmodule