`timescale 1ns/1ps

module tb;
  localparam WIDTH = 8;

  // signals
  logic                 clk;
  logic                 resetn;
  logic  [7:0]          din;
  logic [17:0]          dout;
  logic                 run;

  // DUT instantiation
  model dut (
    .clk    (clk),
    .resetn (resetn),
    .din    (din),
    .dout   (dout),
    .run    (run)
  );

  // 10 ns clock
  initial clk = 0;
  always #5 clk = ~clk;

  // scratchpad for feeding data
  reg [7:0] test_data [0:5];
  integer i;

  initial begin
    $display(">> TESTBENCH START <<");

    // Global reset
    resetn = 0;
    din    = 8'd0;
    @(posedge clk); #1;
    resetn = 1;

    // --- Test 0: zero-vector → dot = 0 ---
    for (i = 0; i < 6; i = i + 1) begin
      din = 8'd0;
      @(posedge clk); #1;
    end
    if (run !== 1'b1 || dout !== 18'd0)
      $display("[FAIL] Test 0: run=%b dout=%0d, expected run=1 dout=0", run, dout);
    else
      $display("[PASS] Test 0");

    // --- Test 1: [1,2,3]·[4,5,6] = 32 ---
    test_data[0] = 8'd1;
    test_data[1] = 8'd2;
    test_data[2] = 8'd3;
    test_data[3] = 8'd4;
    test_data[4] = 8'd5;
    test_data[5] = 8'd6;
    for (i = 0; i < 6; i = i + 1) begin
      din = test_data[i];
      @(posedge clk); #1;
    end
    if (run !== 1'b1 || dout !== 18'd32)
      $display("[FAIL] Test 1: run=%b dout=%0d, expected run=1 dout=32", run, dout);
    else
      $display("[PASS] Test 1");

    // --- Test 2: [7,8,9]·[1,2,3] = 50 ---
    test_data[0] = 8'd7;
    test_data[1] = 8'd8;
    test_data[2] = 8'd9;
    test_data[3] = 8'd1;
    test_data[4] = 8'd2;
    test_data[5] = 8'd3;
    for (i = 0; i < 6; i = i + 1) begin
      din = test_data[i];
      @(posedge clk); #1;
    end
    if (run !== 1'b1 || dout !== 18'd50)
      $display("[FAIL] Test 2: run=%b dout=%0d, expected run=1 dout=50", run, dout);
    else
      $display("[PASS] Test 2");

    $finish;
  end
endmodule
