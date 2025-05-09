`timescale 1ns/1ps

module tb;
  // Parameters
  localparam WIDTH = 8;

  // Signals
  logic         clk;
  logic         resetn;
  logic  [7:0]  din;
  logic  [2:0]  addr;
  logic         wr;
  logic         rd;
  logic  [7:0]  dout;
  logic         error;

  // Instantiate DUT
  model dut (
    .din    (din),
    .addr   (addr),
    .wr     (wr),
    .rd     (rd),
    .clk    (clk),
    .resetn (resetn),
    .dout   (dout),
    .error  (error)
  );

  // Clock generation: 10 ns period
  initial clk = 0;
  always #5 clk = ~clk;

  initial begin
    $display(">> TESTBENCH START <<");

    // Initialize & reset
    resetn = 0;
    wr     = 0;
    rd     = 0;
    din    = 8'd0;
    addr   = 3'd0;
    #12;
    @(posedge clk); #1;
    resetn = 1;
    @(posedge clk); #1;

    // Test 0: After reset, dout=0 and error=0
    if (dout === 8'd0 && error === 1'b0)
      $display("[PASS] Test 0");
    else
      $display("[FAIL] Test 0: dout=%0d, error=%b", dout, error);

    // Test 1: Write then Read
    // Write 0xA5 at address 3
    din  = 8'hA5;
    addr = 3'd3;
    wr   = 1;
    rd   = 0;
    @(posedge clk); #1;    // perform write
    // Now read back
    wr   = 0;
    rd   = 1;
    @(posedge clk); #1;    // perform read
    if (dout === 8'hA5 && error === 1'b0)
      $display("[PASS] Test 1");
    else
      $display("[FAIL] Test 1: dout=%0h, error=%b", dout, error);

    // Test 2: Simultaneous rd and wr asserts error
    din  = 8'hFF;
    addr = 3'd1;
    wr   = 1;
    rd   = 1;
    @(posedge clk); #1;
    if (error === 1'b1 && dout === 8'd0)
      $display("[PASS] Test 2");
    else
      $display("[FAIL] Test 2: dout=%0d, error=%b", dout, error);

    $finish;
  end
endmodule
