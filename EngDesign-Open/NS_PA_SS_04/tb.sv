`timescale 1ns/1ps

module tb;
  // fixed width
  localparam WIDTH = 8;

  // signals
  logic                  clk;
  logic                  resetn;
  logic [WIDTH-1:0]      din;
  logic [WIDTH-1:0]      tap;
  logic [WIDTH-1:0]      dout;

  // instantiate DUT (no parameter)
  model dut (
    .clk    (clk),
    .resetn (resetn),
    .din    (din),
    .tap    (tap),
    .dout   (dout)
  );

  // 10 ns clock
  initial clk = 0;
  always #5 clk = ~clk;

  initial begin
    $display(">> TESTBENCH START <<");

    // — Test 0: initial load —
    din    = 8'h01;               // seed
    tap    = 8'b1011_0101;        // polynomial
    resetn = 0;
    @(posedge clk);               // at this edge lfsr <= din
    #1 resetn = 1;                // release reset
    if (dout !== din)
      $display("[FAIL] Initial load, dout=%0h expected=%0h", dout, din);
    else
      $display("[PASS] Initial load");

    // — Test 1: collect 10 nonzero outputs —
    for (int i = 0; i < 10; i++) begin
      @(posedge clk);
      if (dout == 0)
        $display("[FAIL] LFSR output zero at cycle %0t", $time);
      else
        $display("[INFO] dout=%0h at cycle %0t", dout, $time);
    end

    // — Test 2: changing taps mid-stream should not zero it —
    tap = 8'b1111_1111;
    @(posedge clk);
    if (dout == 0)
      $display("[FAIL] Unexpected zero after tap change");
    else
      $display("[PASS] Tap change did not zero out");

    // — Test 3: reload new seed on reset —
    din    = 8'hAA;
    tap    = 8'b1100_0011;
    resetn = 0;
    @(posedge clk);               // load new seed
    #1 resetn = 1;
    @(posedge clk);
    if (dout !== din)
      $display("[FAIL] Reload after second reset, dout=%0h expected=%0h", dout, din);
    else
      $display("[PASS] Reload after second reset");

    $finish;
  end
endmodule
