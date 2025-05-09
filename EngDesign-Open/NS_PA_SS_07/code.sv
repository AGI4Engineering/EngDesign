module model (
    input  wire [7:0] din,     // data input for write
    input  wire [2:0] addr,    // address for read or write
    input  wire       wr,      // write-enable
    input  wire       rd,      // read-enable
    input  wire       clk,     // clock
    input  wire       resetn,  // synchronous, active-low reset
    output reg  [7:0] dout,    // data output for read
    output reg        error    // error flag for invalid op
);

    // Internal memory and valid bit array
    reg [7:0] mem [0:7];
    reg valid [0:7];
    
    integer i; // For loop index

    // Synchronization block
    always @(posedge clk or negedge resetn) begin
        if (!resetn) begin
            // Reset all values
            for (i = 0; i < 8; i = i + 1) begin
                mem[i] <= 8'b0;
                valid[i] <= 1'b0;
            end
            dout <= 8'b0;
            error <= 1'b0;
        end else begin
            if (wr && rd) begin
                // Invalid operation: both read and write enabled
                error <= 1'b1;
                dout <= 8'b0;
            end else if (wr) begin
                // Write operation
                mem[addr] <= din;
                valid[addr] <= 1'b1;
                error <= 1'b0;
                dout <= 8'b0;
            end else if (rd) begin
                // Read operation
                if (valid[addr]) begin
                    dout <= mem[addr];
                end else begin
                    dout <= 8'b0; // Unwritten address
                end
                error <= 1'b0;
            end else begin
                // No operation
                dout <= 8'b0;
                error <= 1'b0;
            end
        end
    end

endmodule