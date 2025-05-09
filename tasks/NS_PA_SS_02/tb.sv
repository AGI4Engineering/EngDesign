`timescale 1ns/1ps

module tb;
  localparam DATA_WIDTH = 4;
  reg  clk;
  reg  resetn;
  wire [DATA_WIDTH-1:0] out;

  // DUT
  model #(.DATA_WIDTH(DATA_WIDTH)) dut (
    .clk    (clk),
    .resetn (resetn),
    .out    (out)
  );

  // 10 ns clock
  initial begin
    clk = 0;
    forever #5 clk = ~clk;
  end

  initial begin
    $display(">> TESTBENCH START <<");

    // Test 0: after reset
    resetn = 0;
    @(posedge clk); #1;
    if (out !== {DATA_WIDTH{1'b0}})
      $display("[FAIL] Test 0: out=%b expected=%b", out, {DATA_WIDTH{1'b0}});
    else
      $display("[PASS] Test 0");

    // Test 1: gray(1)
    resetn = 1;
    @(posedge clk); #1;
    if (out !== {{(DATA_WIDTH-1){1'b0}},1'b1})
      $display("[FAIL] Test 1: out=%b expected=%b", out, {{(DATA_WIDTH-1){1'b0}},1'b1});
    else
      $display("[PASS] Test 1");

    // Test 2: gray(2)
    @(posedge clk); #1;
    if (out !== {{(DATA_WIDTH-2){1'b0}},2'b11})
      $display("[FAIL] Test 2: out=%b expected=%b", out, {{(DATA_WIDTH-2){1'b0}},2'b11});
    else
      $display("[PASS] Test 2");

    $finish;
  end
endmodule
