`timescale 1ns/1ps

module tb;
  // Signals
  logic        clk;
  logic        resetn;
  logic [4:0]  init;
  logic        din;
  logic        seen;

  // Instantiate DUT (no parameters)
  model dut (
    .clk    (clk),
    .resetn (resetn),
    .init   (init),
    .din    (din),
    .seen   (seen)
  );

  // 10 ns clock
  initial clk = 0;
  always #5 clk = ~clk;

  initial begin
    $display(">> TESTBENCH START <<");

    //
    // Test 0: Right after reset, seen must be 0
    //
    init   = 5'b10101;
    din    = 1'b0;
    resetn = 0;
    #12;
    @(posedge clk); #1;   // synchronous load of init
    resetn = 1;
    @(posedge clk); #1;   // sample
    if (seen === 1'b0)
      $display("[PASS] Test 0");
    else
      $display("[FAIL] Test 0: seen=%b", seen);

    //
    // Test 1: detect sequence 0,0,1,0,1
    //
    init   = 5'b00101;
    resetn = 0;
    @(posedge clk); #1;   // load new init
    resetn = 1;
    @(posedge clk); #1;   // clear cur

    // stream bits
    din = 1'b0; @(posedge clk); #1;
    din = 1'b0; @(posedge clk); #1;
    din = 1'b1; @(posedge clk); #1;
    din = 1'b0; @(posedge clk); #1;
    din = 1'b1; @(posedge clk); #1;

    if (seen === 1'b1)
      $display("[PASS] Test 1");
    else
      $display("[FAIL] Test 1: seen=%b", seen);

    //
    // Test 2: detect sequence 1,1,1,0,0
    //
    init   = 5'b11100;
    resetn = 0;
    @(posedge clk); #1;   // load new init
    resetn = 1;
    @(posedge clk); #1;   // clear cur

    // stream bits
    din = 1'b1; @(posedge clk); #1;
    din = 1'b1; @(posedge clk); #1;
    din = 1'b1; @(posedge clk); #1;
    din = 1'b0; @(posedge clk); #1;
    din = 1'b0; @(posedge clk); #1;

    if (seen === 1'b1)
      $display("[PASS] Test 2");
    else
      $display("[FAIL] Test 2: seen=%b", seen);

    $finish;
  end
endmodule
