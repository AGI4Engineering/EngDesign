module model #(
    parameter BITWIDTH = 8
) (
    input  logic [BITWIDTH-1:0]     din,     // unsigned input word
    input  logic                    sortit,  // start new sort when asserted
    input  logic                    clk,     // clock
    input  logic                    resetn,  // synchronous, active-low reset
    output logic [8*BITWIDTH+1-1:0] dout     // [MSB]=valid, then 8 sorted words
);

    // Internal 8-word memory and write pointer
    logic [BITWIDTH-1:0] mem [0:7];
    logic [2:0]           write_ptr;

    // Sorting network wires: st[phase][index]
    // st[0] <= mem[0..7]; after 8 even/odd phases, st[8] is sorted ascending
    wire [BITWIDTH-1:0] st [0:8][0:7];

    // Stage 0: feed from memory
    genvar i;
    generate
        for (i = 0; i < 8; i++) begin : init_stage
            assign st[0][i] = mem[i];
        end
    endgenerate

    // Odd-Even Transposition Sort Network for 8 elements
    genvar p, j;
    generate
        for (p = 0; p < 8; p++) begin : phase   // total 8 phases
            for (j = 0; j < 8; j++) begin : elem
                if ((p % 2) == 0) begin : even_phase
                    // Even phase: compare (0,1),(2,3),(4,5),(6,7)
                    if ((j % 2) == 0) begin  // min of pair j and j+1
                        assign st[p+1][j]   = (st[p][j]   < st[p][j+1]) ? st[p][j]   : st[p][j+1];
                    end else begin          // max of pair j-1 and j
                        assign st[p+1][j]   = (st[p][j-1] < st[p][j]  ) ? st[p][j]   : st[p][j-1];
                    end
                end else begin : odd_phase
                    // Odd phase: compare (1,2),(3,4),(5,6); leave 0 and 7 alone
                    if (j == 0) begin
                        assign st[p+1][j] = st[p][j];
                    end else if ((j % 2) == 1 && (j < 7)) begin  // min of pair
                        assign st[p+1][j] = (st[p][j] < st[p][j+1]) ? st[p][j] : st[p][j+1];
                    end else if ((j % 2) == 0 && (j > 0)) begin  // max of pair
                        assign st[p+1][j] = (st[p][j-1] < st[p][j]) ? st[p][j] : st[p][j-1];
                    end else begin  // j==7 end
                        assign st[p+1][j] = st[p][j];
                    end
                end
            end
        end
    endgenerate

    // Sequential logic: data capture, sort trigger, and output register
    always_ff @(posedge clk) begin
        if (~resetn) begin
            // Reset memory, pointer, and output
            write_ptr <= 3'd0;
            for (int idx = 0; idx < 8; idx++) begin
                mem[idx] <= '0;
            end
            dout <= '0;
        end else begin
            if (sortit) begin
                // Perform one-cycle sort: output valid + sorted data
                dout <= { 1'b1,
                    st[8][0], st[8][1], st[8][2], st[8][3],
                    st[8][4], st[8][5], st[8][6], st[8][7]
                };
                // Freeze mem and pointer until sortit deasserts
            end else begin
                // Capture new input word into memory
                mem[write_ptr] <= din;
                write_ptr      <= write_ptr + 3'd1;
                dout           <= '0;  // clear output when not sorting
            end
        end
    end

endmodule