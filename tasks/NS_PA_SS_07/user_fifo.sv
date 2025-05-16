module register_file (
    input  wire [7:0] din,     // data input for write
    input  wire [2:0] addr,    // address for read or write
    input  wire       wr,      // write-enable
    input  wire       rd,      // read-enable
    input  wire       clk,     // clock
    input  wire       resetn,  // synchronous, active-low reset
    output reg  [7:0] dout,    // data output for read
    output reg        error    // error flag for invalid op
);

    // Internal memory storage and valid tracking
    reg [7:0] mem [0:7];       // memory array of flip-flops
    reg valid [0:7];           // valid bit array to track written entries

    integer i;

    // Synchronous reset or operation
    always @(posedge clk) begin
        if (!resetn) begin
            // Active-low reset: clear valid bits, dout and error
            for (i = 0; i < 8; i = i + 1) begin
                valid[i] <= 1'b0;
            end
            dout <= 8'b0;
            error <= 1'b0;
        end
        else begin
            if (wr && rd) begin
                // Invalid operation: both read and write
                dout <= 8'b0;
                error <= 1'b1;
            end
            else if (wr) begin
                // Write operation
                mem[addr] <= din;
                valid[addr] <= 1'b1;
                dout <= 8'b0;
                error <= 1'b0;
            end
            else if (rd) begin
                // Read operation
                if (valid[addr]) begin
                    dout <= mem[addr];
                    error <= 1'b0;
                end else begin
                    dout <= 8'b0;
                    error <= 1'b0;
                end
            end
            else begin
                // No operation
                dout <= 8'b0;
                error <= 1'b0;
            end
        end
    end
endmodule