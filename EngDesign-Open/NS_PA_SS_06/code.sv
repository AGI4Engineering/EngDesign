module model (
    input  logic [7:0] din,     // serial input words: a1, a2, a3, b1, b2, b3
    input  logic       clk,     // clock signal
    input  logic       resetn,  // synchronous, active-low reset
    output logic [17:0] dout,   // dot product result
    output logic       run      // asserted for one cycle when dout is valid
);

  // Internal registers
  logic [7:0] vector_a [0:2];  // To hold a1, a2, a3
  logic [7:0] vector_b [0:2];  // To hold b1, b2, b3
  logic [2:0] count;           // Input counter

  // The sequential logic block
  always_ff @(posedge clk or negedge resetn) begin
    if (!resetn) begin
      // Reset all registers
      vector_a[0] <= 8'd0;
      vector_a[1] <= 8'd0;
      vector_a[2] <= 8'd0;
      vector_b[0] <= 8'd0;
      vector_b[1] <= 8'd0;
      vector_b[2] <= 8'd0;
      dout <= 18'd0; // Clear output
      run <= 1'b1;   // Assert run to indicate that dout (which is 0) is valid
      count <= 3'd0; // Reset count
    end else begin
      // Default run to zero
      run <= 1'b0;

      // Capture serial inputs
      case (count)
        3'd0: vector_a[0] <= din;
        3'd1: vector_a[1] <= din;
        3'd2: vector_a[2] <= din;
        3'd3: vector_b[0] <= din;
        3'd4: vector_b[1] <= din;
        3'd5: begin
          vector_b[2] <= din; // Complete the collection
          dout <= (vector_a[0] * vector_b[0]) +
                  (vector_a[1] * vector_b[1]) +
                  (vector_a[2] * vector_b[2]); // Compute result
          run <= 1'b1; // Assert run: result is now valid
        end
      endcase

      // Increment or reset counter
      if (count < 3'd5) begin
        count <= count + 3'd1;
      end else begin
        count <= 3'd0;
      end
    end
  end
endmodule