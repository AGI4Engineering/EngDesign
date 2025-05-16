module fifo2 #(
    parameter DATA_WIDTH = 16
) (
    input  logic [DATA_WIDTH-1:0] din,   // write data
    input  logic [4:0]            wad1,  // write address
    input  logic [4:0]            rad1,  // read address 1
    input  logic [4:0]            rad2,  // read address 2
    input  logic                  wen1,  // write-enable
    input  logic                  ren1,  // read-enable 1
    input  logic                  ren2,  // read-enable 2
    input  logic                  clk,   // clock
    input  logic                  resetn,// sync active-low reset
    output logic [DATA_WIDTH-1:0] dout1, // read data 1
    output logic [DATA_WIDTH-1:0] dout2, // read data 2
    output logic                  collision // collision flag
);

    // Register bank
    logic [DATA_WIDTH-1:0] regfile [0:31];

    // Reset or write logic
    always_ff @(posedge clk) begin
        if (!resetn) begin
            for (int i = 0; i < 32; i++) begin
                regfile[i] <= '0;
            end
            dout1 <= '0;
            dout2 <= '0;
            collision <= 1'b0;
        end else begin
            if (wen1) begin
                regfile[wad1] <= din;
            end

            if (wen1 && ((wad1 == rad1 && ren1) || (wad1 == rad2 && ren2))) begin
                collision <= 1'b1;
            end else if (ren1 && ren2 && rad1 == rad2) begin
                collision <= 1'b1;
            end else begin
                collision <= 1'b0;
            end
        end
    end

    // Read logic
    always_comb begin
        if (ren1) begin
            dout1 = regfile[rad1];
        end else begin
            dout1 = '0;
        end
        
        if (ren2) begin
            dout2 = regfile[rad2];
        end else begin
            dout2 = '0;
        end
    end

endmodule