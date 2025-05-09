// tb.sv
module tb;
  // Parameter
  localparam DATA_WIDTH = 16;

  // Signals
  logic                     clk, resetn;
  logic [DATA_WIDTH-1:0]    din;
  logic [4:0]               wad1, rad1, rad2;
  logic                     wen1, ren1, ren2;
  logic [DATA_WIDTH-1:0]    dout1, dout2;
  logic                     collision;

  // Instantiate the DUT
  model #(.DATA_WIDTH(DATA_WIDTH)) dut (
    .din(din),
    .wad1(wad1),
    .rad1(rad1),
    .rad2(rad2),
    .wen1(wen1),
    .ren1(ren1),
    .ren2(ren2),
    .clk(clk),
    .resetn(resetn),
    .dout1(dout1),
    .dout2(dout2),
    .collision(collision)
  );

  // Clock generation: 10 ns period
  initial clk = 0;
  always #5 clk = ~clk;

  initial begin
    // Reset sequence
    resetn = 0;
    wen1   = 0; ren1 = 0; ren2 = 0;
    din    = '0; wad1 = '0; rad1 = '0; rad2 = '0;
    #10;
    @(posedge clk);
    resetn = 1;
    @(posedge clk);

    // Test 0: Write then Read
    din   = 16'hA5A5;
    wad1  = 5'd7;
    wen1  = 1;
    ren1  = 0; ren2 = 0;
    @(posedge clk);

    // Now read back
    wen1  = 0;
    ren1  = 1; rad1 = 5'd7;
    @(posedge clk);
    if (dout1 === 16'hA5A5)
      $display("[PASS] Test 0");
    else
      $display("[FAIL] Test 0");

    // Test 1: Read from unwritten address should return zero
    ren1 = 1; rad1 = 5'd3;
    ren2 = 0;
    @(posedge clk);
    if (dout1 === {DATA_WIDTH{1'b0}})
      $display("[PASS] Test 1");
    else
      $display("[FAIL] Test 1");

    // Test 2: Collision detection on write/read to same address
    wen1   = 1; 
    din    = 16'hFFFF; 
    wad1   = 5'd4;
    ren1   = 1; rad1 = 5'd4;
    ren2   = 0;
    @(posedge clk);
    if (collision)
      $display("[PASS] Test 2");
    else
      $display("[FAIL] Test 2");

    $finish;
  end
endmodule
