module model #(
    parameter WIDTH = 8  // Default width is 8 bits
) (
    input  logic [WIDTH-1:0] gray,  // N-bit Gray code input
    output logic [WIDTH-1:0] bin    // N-bit binary index output
);

    // MSB of binary is same as MSB of Gray
    assign bin[WIDTH-1] = gray[WIDTH-1];

    // XOR cascade for remaining bits
    // For each bit i from WIDTH-2 down to 0: bin[i] = bin[i+1] ^ gray[i]
    genvar i;
    generate
        for (i = WIDTH-2; i >= 0; i--) begin : gray_to_bin_loop
            assign bin[i] = bin[i+1] ^ gray[i];
        end
    endgenerate

endmodule