module model #(parameter
  DATA_WIDTH = 16
) (
  input [DATA_WIDTH-1:0] gray,
  output logic [DATA_WIDTH-1:0] bin
);

    int i;
    logic [DATA_WIDTH-1:0] temp;

    always @(*) begin
        for(i=0; i<DATA_WIDTH; i++) begin
            temp[i] = ^(gray >> i);
        end
    end

    assign bin = temp;

endmodule