module hex_driver (
    input   logic           clk,
    input   logic           reset,

    input   logic   [3:0]   in[4],

    output  logic   [7:0]   hex_seg,
    output  logic   [3:0]   hex_grid
);
    
    module nibble_to_hex(
        input   logic   [3:0]   nibble,
        output  logic   [7:0]   hex
    );
        always_comb begin
        case(nibble)
            4'b0000 : hex = 8'b00111111; // '0'
            4'b0001 : hex = 8'b00000110; // '1'
            4'b0010 : hex = 8'b01011011; // '2'
            4'b0011 : hex = 8'b01001111; // '3'
            4'b0100 : hex = 8'b01100110; // '4'
            4'b0101 : hex = 8'b01101101; // '5'
            4'b0110 : hex = 8'b01111101; // '6'
            4'b0111 : hex = 8'b00000111; // '7'
            4'b1000 : hex = 8'b01111111; // '8'
            4'b1001 : hex = 8'b01101111; // '9'
            4'b1010 : hex = 8'b01110111; // 'A'
            4'b1011 : hex = 8'b01111100; // 'b'
            4'b1100 : hex = 8'b00111001; // 'C'
            4'b1101 : hex = 8'b01011110; // 'd'
            4'b1110 : hex = 8'b01111001; // 'E'
            4'b1111 : hex = 8'b01110001; // 'F'
        endcase
        end
    endmodule

    logic [7:0] hex [4];

    genvar i;
    generate
        for(i = 0; i < 4; i++) begin
            nibble_to_hex nibble_to_hex_(
                .nibble(in[i]),
                .hex(hex[i])
            );
        end
    endgenerate

    logic [16:0] counter;

    always_ff @( posedge clk ) begin
        if (reset) begin
            counter <= '0;
        end else begin
            counter <= counter + 1;
        end
    end

    always_comb begin
        if (reset) begin
            hex_grid = '1;
            hex_seg = '1;
        end else begin
            case (counter [16:15])
            2'b00: begin
                hex_seg = ~hex[0];
                hex_grid = 4'b1110;
            end
            2'b01: begin
                hex_seg = ~hex[1];
                hex_grid = 4'b1101;
            end
            2'b10: begin
                hex_seg = ~hex[2];
                hex_grid = 4'b1011;
            end
            2'b11: begin
                hex_seg = ~hex[3];
                hex_grid = 4'b0111;
            end
            endcase
        end
    end

endmodule