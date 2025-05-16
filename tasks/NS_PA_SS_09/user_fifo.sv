module gray_to_binary #(
    parameter WIDTH = 8  // Parameter to set the width of the Gray code input and binary output
) (
    input  logic [WIDTH-1:0] gray,  // N-bit Gray code input
    output logic [WIDTH-1:0] bin    // N-bit binary index output
);

    // Combinational logic to convert Gray code to binary
    always_comb begin
        integer i;  // Loop variable
        bin[WIDTH-1] = gray[WIDTH-1];  // MSB remains the same
        
        // Loop to calculate binary indexed value from Gray code
        for (i = WIDTH-2; i >= 0; i = i - 1) begin
            bin[i] = bin[i+1] ^ gray[i];  // XOR cascade for conversion
        end
    end

endmodule