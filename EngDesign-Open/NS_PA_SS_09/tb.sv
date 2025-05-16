// tb_gray2bin.sv: Testbench for Gray-to-binary converter
`timescale 1ns/1ps
module tb;
  // Parameters
  localparam WIDTH = 8;

  // Signals
  logic [WIDTH-1:0] gray;
  logic [WIDTH-1:0] bin;

  // Instantiate DUT
  model #(.WIDTH(WIDTH)) dut (
    .gray(gray),
    .bin(bin)
  );

  initial begin
    // Allow combinational outputs to settle
    #1;

    // Test 0: gray = 0 -> bin = 0
    gray = 'h00; #1;
    if (bin === 'h00)
      $display("[PASS] Test 0");
    else
      $display("[FAIL] Test 0: gray=0x%0h, expected bin=0x00, got=0x%0h", gray, bin);

    // Test 1: gray = 8'b00000011 (3) -> bin = 8'b00000010 (2)
    gray = 8'h03; #1;
    if (bin === 8'h02)
      $display("[PASS] Test 1");
    else
      $display("[FAIL] Test 1: gray=0x%0h, expected bin=0x02, got=0x%0h", gray, bin);

    // Test 2: gray = 8'b00000110 (6) -> bin = 8'b00000100 (4)
    gray = 8'h06; #1;
    if (bin === 8'h04)
      $display("[PASS] Test 2");
    else
      $display("[FAIL] Test 2: gray=0x%0h, expected bin=0x04, got=0x%0h", gray, bin);

    $finish;
  end
endmodule
