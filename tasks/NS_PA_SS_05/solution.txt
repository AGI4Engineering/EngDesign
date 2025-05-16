module model #(parameter 
    BITWIDTH = 3
) (
    input [BITWIDTH-1:0] din,
    input sortit,
    input clk,
    input resetn,
    output logic [8*BITWIDTH:0] dout
);
    
    localparam NINPUTS = 8;

    logic [BITWIDTH-1:0] mem [NINPUTS-1:0];
    logic [BITWIDTH-1:0] tmp;
    logic [$clog2(NINPUTS)-1:0] addr;
    logic [NINPUTS*BITWIDTH:0] dout_preff;

    always_ff @(posedge clk) begin
        if (!resetn) begin
            addr <= '0;
            dout <= '0;
            mem <= '{default:'0};
        end else if (!sortit) begin 
            addr <= addr + 1;
            dout <= dout_preff;
            mem[addr] <= din;
        end else begin
            addr <= addr;
            dout <= dout_preff;
            mem[addr] <= mem[addr];
        end
    end

    always_comb begin
        if (sortit) begin
            // Bubble sort algorithm
            integer i, j;
            for (i = NINPUTS - 1; i > -1; i--) begin
                for (j = 0; j < i; j++) begin
                    if (mem[j] < mem[j + 1]) begin
                        tmp = mem[j];
                        mem[j] = mem[j + 1];
                        mem[j + 1] = tmp;
                    end 
                end
            end
        end
    end

    always_comb begin
        if (sortit) begin
            integer k;
            for (k = 0; k < NINPUTS; k++) begin
                dout_preff[BITWIDTH*k+:BITWIDTH] = mem[k];
            end
        end else begin
            dout_preff = '0;
        end
    end

endmodule