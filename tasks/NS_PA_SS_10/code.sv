module model (
    input  logic clk,      // clock signal
    input  logic resetn,   // synchronous, active‐low reset: clears history
    input  logic din,      // serial input bit, MSB first
    output logic dout      // high if the current value mod 5 == 0
);

  typedef enum logic [2:0] {R0, R1, R2, R3, R4} state_t;
  state_t current_state, next_state;

  always_ff @(posedge clk) begin
    if (~resetn) begin
      current_state <= R0;
    end else begin
      current_state <= next_state;
    end
  end

  always_comb begin
    case (current_state)
      R0: begin
        if (din) next_state = R1; else next_state = R0;
      end
      R1: begin
        if (din) next_state = R3; else next_state = R2;
      end
      R2: begin
        if (din) next_state = R4; else next_state = R1;
      end
      R3: begin
        if (din) next_state = R2; else next_state = R0;
      end
      R4: begin
        if (din) next_state = R1; else next_state = R3;
      end
      default: next_state = R0; //Should never happen
    endcase
  end

  always_comb begin
    dout = (current_state == R0);
  end

endmodule
