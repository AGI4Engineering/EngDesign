module model #(
    parameter BITWIDTH = 8
) (
    input  logic [BITWIDTH-1:0]       din,     // unsigned input word
    input  logic                      sortit,  // start new sort when asserted
    input  logic                      clk,     // clock
    input  logic                      resetn,  // synchronous, active-low reset
    output logic [8*BITWIDTH:0]       dout     // concatenated sorted vector + valid bit
);

    // Internal memory to store the 8 words
    logic [BITWIDTH-1:0] mem [0:7];
    logic [BITWIDTH-1:0] sorted_mem [0:7];

    integer i, load_index;
    logic valid;

    always_ff @(posedge clk or negedge resetn) begin
        if (!resetn) begin
            // Reset logic
            dout <= 0;
            load_index <= 0;
            for (i = 0; i < 8; i++) begin
                mem[i] <= 0;
            end
            valid <= 0;
        end else if (!sortit) begin
            // Data capture logic when sortit is low
            mem[load_index] <= din;
            load_index <= (load_index + 1) % 8;
        end else begin
            // Copy mem to sorted_mem for sorting
            for (i = 0; i < 8; i++) begin
                sorted_mem[i] = mem[i];
            end

            // Perform bubble sort using a simple sorting network
            generate
                genvar j, k;
                for (j = 0; j < 7; j = j + 1) begin
                    for (k = 0; k < 7-j; k = k + 1) begin
                        always_comb begin
                            if (sorted_mem[k] < sorted_mem[k+1]) begin
                                logic [BITWIDTH-1:0] temp;
                                temp = sorted_mem[k];
                                sorted_mem[k] = sorted_mem[k+1];
                                sorted_mem[k+1] = temp;
                            end
                        end
                    end
                end
            endgenerate

            // Construct the output with a valid flag
            dout = {1'b1, sorted_mem[7], sorted_mem[6], sorted_mem[5], sorted_mem[4],
                   sorted_mem[3], sorted_mem[2], sorted_mem[1], sorted_mem[0]};
        end
    end
endmodule
