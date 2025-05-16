module gray_counter #(
  parameter integer N = 4 // Width of the Gray‐code output
)(
  input wire clk, // Rising‐edge clock
  input wire resetn, // Active‐low synchronous reset
  output reg [N-1:0] dout // Current Gray‐code output
);

reg [N-1:0] binary_counter; // A regular binary counter

// Convert binary to Gray code
function [N-1:0] binary_to_gray;
  input [N-1:0] binary_value;
  begin
    binary_to_gray = binary_value ^ (binary_value >> 1);
  end
endfunction

always @(posedge clk) begin
  if (!resetn) begin
    binary_counter <= 0;
    dout <= 0;
  end else begin
    binary_counter <= binary_counter + 1;
    dout <= binary_to_gray(binary_counter);
  end
end

endmodule