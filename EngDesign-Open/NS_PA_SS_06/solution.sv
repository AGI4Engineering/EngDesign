module model (
    input [7:0] din,
    input clk,
    input resetn,
    output reg [17:0] dout,
    output reg run
);

    // Let's keep track of the required number of bits after each mult and add operation
    // Assuming vector A = [a1, a2, a3], and vector B = [b1, b2, b3]
    // a1 * b1 = 16-b
    // a2 * b2 = 16-b
    // a3 * b3 = 16-b
    // a1b1 + a2b2 + a3b3 = 18-b

    reg [2:0] cnt;
    reg [7:0] mem [5:0];
    reg [15:0] a1b1, a2b2, a3b3;

    // A 3-bit counter is used to track the number of inputs
    always_ff @(posedge clk) begin
        if (!resetn || cnt == 5) begin
            cnt <= 0;
        end else begin 
            cnt <= cnt + 1;
        end
    end

    // Internal memory
    always_ff @(posedge clk) begin
        if (!resetn) begin
            mem[0] <= 0;
            mem[1] <= 0;
            mem[2] <= 0;
            mem[3] <= 0;
            mem[4] <= 0;
            mem[5] <= 0;
        end else begin
            mem[cnt] <= din;
        end
    end

    // Combinational logic
    assign run = (cnt == 0);
    assign a1b1 = (run) ? mem[0] * mem[3] : a1b1;
    assign a2b2 = (run) ? mem[1] * mem[4] : a2b2;
    assign a3b3 = (run) ? mem[2] * mem[5] : a3b3;
    assign dout = a1b1 + a2b2 + a3b3;

endmodule