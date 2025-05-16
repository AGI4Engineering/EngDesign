`timescale 1ns/1ps

module tb;
  // Signals
  logic clk;
  logic resetn;
  logic din;
  logic dout;

  // Instantiate DUT
  model dut (
    .clk    (clk),
    .resetn (resetn),
    .din    (din),
    .dout   (dout)
  );

  // Clock generation: 10 ns period
  initial clk = 0;
  always #5 clk = ~clk;

  initial begin
    $display(">> TESTBENCH START <<");

    //
    // Test 0: 5 (binary 101) → divisible by 5 → dout==1
    //
    resetn = 0;
    din    = 1'b0;
    @(posedge clk); #1;   // load reset
    resetn = 1;
    @(posedge clk); #1;   // state now MODR

    // Feed bits: 1,0,1
    din = 1'b1; @(posedge clk); #1;
    din = 1'b0; @(posedge clk); #1;
    din = 1'b1; @(posedge clk); #1;

    if (dout === 1'b1)
      $display("[PASS] Test 0");
    else
      $display("[FAIL] Test 0: dout=%b, expected 1", dout);

    //
    // Test 1: 6 (binary 110) → not divisible → dout==0
    //
    resetn = 0;
    @(posedge clk); #1;
    resetn = 1;
    @(posedge clk); #1;

    din = 1'b1; @(posedge clk); #1;
    din = 1'b1; @(posedge clk); #1;
    din = 1'b0; @(posedge clk); #1;

    if (dout === 1'b0)
      $display("[PASS] Test 1");
    else
      $display("[FAIL] Test 1: dout=%b, expected 0", dout);

    //
    // Test 2: 10 (binary 1010) → divisible → dout==1
    //
    resetn = 0;
    @(posedge clk); #1;
    resetn = 1;
    @(posedge clk); #1;

    din = 1'b1; @(posedge clk); #1;
    din = 1'b0; @(posedge clk); #1;
    din = 1'b1; @(posedge clk); #1;
    din = 1'b0; @(posedge clk); #1;

    if (dout === 1'b1)
      $display("[PASS] Test 2");
    else
      $display("[FAIL] Test 2: dout=%b, expected 1", dout);

    $finish;
  end
endmodule
