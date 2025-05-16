// tb.sv: Testbench for one-cycle bubble-sort model
`timescale 1ns/1ps
module tb;
  localparam BITWIDTH = 8;
  localparam WIDTH    = BITWIDTH*8 + 1;

  // Signals
  logic                    clk;
  logic                    resetn;
  logic                    sortit;
  logic [BITWIDTH-1:0]     din;
  logic [WIDTH-1:0]        dout;

  // Instantiate DUT
  model #(.BITWIDTH(BITWIDTH)) dut (
    .din    (din),
    .sortit (sortit),
    .clk    (clk),
    .resetn (resetn),
    .dout   (dout)
  );

  // Clock generation: 10 ns period
  initial clk = 0;
  always #5 clk = ~clk;

  // Test vectors
  reg [BITWIDTH-1:0] data_mem [0:7];
  logic [BITWIDTH-1:0] sorted [0:7];
  logic [WIDTH-1:0]    prev;
  integer i, j;
  logic ok;

  initial begin
    // Reset
    resetn = 0;
    sortit = 0;
    din    = '0;
    #12;
    @(posedge clk);
    resetn = 1;
    @(posedge clk);

    // Test 0: dout should be zero when sortit=0
    if (dout === {WIDTH{1'b0}})
      $display("[PASS] Test 0");
    else
      $display("[FAIL] Test 0");

    // Prepare 8 unsorted inputs
    data_mem[0] = 8'h10;
    data_mem[1] = 8'hFF;
    data_mem[2] = 8'h00;
    data_mem[3] = 8'h7F;
    data_mem[4] = 8'h80;
    data_mem[5] = 8'h01;
    data_mem[6] = 8'hFE;
    data_mem[7] = 8'h7E;
    sortit = 0;

    // Load inputs while sortit=0
    for (i = 0; i < 8; i = i + 1) begin
      din = data_mem[i];
      @(posedge clk);
    end

    // Test 1: assert sortit and perform sort
    sortit = 1;
    @(posedge clk);
    // Check valid flag (MSB of dout)
    if (dout[WIDTH-1] !== 1) begin
      $display("[FAIL] Test 1");
    end else begin
      // Extract sorted words
      for (j = 0; j < 8; j = j + 1) begin
        sorted[j] = dout[BITWIDTH*(8-j) - 1 -: BITWIDTH];
      end
      // Verify ascending order (smallest→largest)
      ok = 1;
      for (j = 0; j < 7; j = j + 1)
        if (sorted[j] > sorted[j+1])
          ok = 0;
      if (ok)
        $display("[PASS] Test 1");
      else
        $display("[FAIL] Test 1");
    end

    // Test 2: output stability when sortit remains asserted
    prev = dout;
    @(posedge clk);
    if (dout === prev)
      $display("[PASS] Test 2");
    else
      $display("[FAIL] Test 2");

    $finish;
  end
endmodule
