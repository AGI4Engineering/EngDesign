module model #(parameter 
    DATA_WIDTH = 16
) (
    input [DATA_WIDTH-1:0] din,
    input [4:0] wad1,
    input [4:0] rad1, rad2,
    input wen1, ren1, ren2,
    input clk,
    input resetn,
    output logic [DATA_WIDTH-1:0] dout1, dout2,
    output logic collision
);

    reg [DATA_WIDTH-1:0] mem [31:0];

    always_ff @(posedge clk) begin
        if (!resetn) begin
            // If reset mode, all entries are set to zero
            mem = '{default:'0};
            dout1 <= '0;
            dout2 <= '0;
            collision <= '0;
        end else begin
            if (!wen1 & !ren1 & !ren2) begin  // NOP
                dout1 <= '0;
                dout2 <= '0;
                collision <= '0;
            end else if (!wen1 & !ren1 & ren2) begin  // Read 2
                dout1 <= '0;
                dout2 <= mem[rad2];
                collision <= '0;
            end else if (!wen1 & ren1 & !ren2) begin  // Read 1
                dout1 <= mem[rad1];
                dout2 <= '0;
                collision <= '0;
            end else if (!wen1 & ren1 & ren2) begin  // Read 1 & Read 2
                if (rad1 == rad2) begin
                    dout1 <= '0;
                    dout2 <= '0;
                    collision <= '1;
                end else begin
                    dout1 <= mem[rad1];
                    dout2 <= mem[rad2];
                    collision <= '0;
                end
            end else if (wen1 & !ren1 & !ren2) begin  // Write, no reads
                mem[wad1] <= din;
                dout1 <= '0;
                dout2 <= '0;
                collision <= '0;
            end else begin  // Allowed, but need to check for address collision
                if (wad1 == rad1 && ren1) begin
                    dout1 <= '0;
                    dout2 <= '0;
                    collision <= '1;
                end else if (wad1 == rad2 && ren2) begin
                    dout1 <= '0;
                    dout2 <= '0;
                    collision <= '1;
                end else if (rad1 == rad2 && ren1 && ren2) begin
                    mem[wad1] <= din;
                    dout1 <= '0;
                    dout2 <= '0;
                    collision <= '1;
                end else begin
                    mem[wad1] <= din;
                    if (!ren1 & ren2) begin
                        dout1 <= '0;
                        dout2 <= mem[rad2];
                    end else if (ren1 & !ren2) begin
                        dout1 <= mem[rad1];
                        dout2 <= '0;
                    end else begin
                        dout1 <= mem[rad1];
                        dout2 <= mem[rad2];
                    end
                    collision <= '0;
                end
            end
        end
    end

endmodule