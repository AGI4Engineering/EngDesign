module model #(parameter
  DATA_WIDTH = 4
) (
  input clk,
  input resetn,
  output logic [DATA_WIDTH-1:0] out
);

    logic [DATA_WIDTH-1:0] q, temp;

    always @ (posedge clk) begin
        if (!resetn) begin
            temp <= 0;
            q <= 1;
        end else begin
            q <= q + 1;

            for (int i = 0; i < DATA_WIDTH-1; i=i+1) begin
                temp[i] <= q[i+1] ^ q[i];
            end

            temp[DATA_WIDTH-1] <= q[DATA_WIDTH-1];
        end
    end

    assign out = temp;

endmodule