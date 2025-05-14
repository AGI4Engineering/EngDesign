//-------------------------------------------------------------------------
//    Color_Mapper.sv                                                    --
//    Stephen Kempf                                                      --
//    3-1-06                                                             --
//                                                                       --
//    Modified by David Kesler  07-16-2008                               --
//    Translated by Joe Meng    07-07-2013                               --
//    Modified by Zuofu Cheng   08-19-2023                               --
//                                                                       --
//    Fall 2023 Distribution                                             --
//                                                                       --
//    For use with ECE 385 USB + HDMI                                    --
//    University of Illinois ECE Department                              --
//-------------------------------------------------------------------------


module  color_mapper ( 
    input  logic [2:0] Tetro,
    input logic [1:0] direction,
    input logic [2:0] next_Tetro,
    input logic [4:0] TetroX,
    input logic [4:0] TetroY,
    
    input logic start,
    input logic in_progress,
    input logic end_game,
    input logic [199:0] map,
    input logic [9:0] DrawX, DrawY,
    output logic [3:0]  Red, Green, Blue );
    
    logic ball_on;
	 
 /* Old Ball: Generated square box by checking if the current pixel is within a square of length
    2*BallS, centered at (BallX, BallY).  Note that this requires unsigned comparisons.
	 
    if ((DrawX >= BallX - Ball_size) &&
       (DrawX <= BallX + Ball_size) &&
       (DrawY >= BallY - Ball_size) &&
       (DrawY <= BallY + Ball_size))
       )

     New Ball: Generates (pixelated) circle by using the standard circle formula.  Note that while 
     this single line is quite powerful descriptively, it causes the synthesis tool to use up three
     of the 120 available multipliers on the chip!  Since the multiplicants are required to be signed,
	  we have to first cast them from logic to int (signed by default) before they are multiplied). */
    logic [7:0] positionX, positionY,nextX,nextY;
    logic [8:0] triangleX, triangleY;
    logic [3:0] blockX,blockY;
    
    logic block_on,next_block_on,next_canvas_on, score_canvas_on,map_on;
    logic canvas_on,menu_on,game_over_on,triangle_on,start_block_on;
    logic [3:0][3:0] block,next_block;
    logic [3:0]  Red_E, Green_E, Blue_E;
    assign positionX = DrawX[9:4];
    assign positionY = DrawY[9:4];
    assign triangleX = DrawX[9:1];
    assign triangleY = DrawY[9:1];
    assign nextX = DrawX[9:4];
    assign nextY = DrawX[9:4];
    assign blockX = DrawX[3:0];
    assign blockY = DrawY[3:0];
    font_rom font_map (
        .tetro(Tetro),
        .direction(direction),
        .data(block)
    );
    GAMEOVER gameover(
        .DrawX(DrawX),        // 当前像素 X 坐标
        .DrawY(DrawY),        // 当前像素 Y 坐标
        .game_over(game_over_on),   // 游戏结束标志
        .Red(Red_E),          // 红色分量
        .Green(Green_E),        // 绿色分量
        .Blue(Blue_E)          // 蓝色分量
    );
    font_rom next_map(
        .tetro(next_Tetro),
        .direction(2'b00),
        .data(next_block)
    );
    always_comb
    begin
        block_on = 1'b0;
        map_on = 1'b0;
        canvas_on = 1'b0;
        menu_on = 1'b0;
        next_block_on = 1'b0;
        next_canvas_on = 1'b0;
        score_canvas_on = 1'b0;
        game_over_on = 1'b0;
        triangle_on = 1'b0;
        start_block_on = 1'b0;
        if (DrawX[9:4] >= 6'd28 && DrawX[9:4] < 6'd32 && DrawY[9:4] >= 6'd8 && DrawY[9:4] < 6'd12)
        begin
            nextX = DrawX[9:4] - 7'd28;
            nextY = DrawY[9:4] - 7'd8;
            if (next_block[nextY][2'd3 - nextX] == 1'b1)
            begin
                next_block_on = 1'b1;
            end
            if (block[nextY][2'd3 - nextX] == 1'b1)
            begin
                start_block_on = 1'b1;
            end
            next_canvas_on = 1'b1;

        end
        if (DrawX[9:4] >= 6'd28 && DrawX[9:4] < 6'd34 && DrawY[9:4] >= 6'd14 && DrawY[9:4] < 6'd17)
        begin
            score_canvas_on = 1'b1;
        end
        if (DrawX[9:4] >= 6'd15 && DrawX[9:4] < 6'd25 && DrawY[9:4] >= 6'd5 && DrawY[9:4] < 6'd25)
        begin
            positionX = DrawX[9:4] - 4'd15;
            positionY = DrawY[9:4] - 3'd5;
            if (positionX >= 6'd1 && positionX < 6'd9  && positionY >= 6'd8  && positionY < 6'd12)
            begin
                triangleX = DrawX[9:1] - 8'd154;
                triangleY = DrawY[9:1] - 7'd108;
                if (triangleX >= 1'd0 && triangleX < 7'd12)
                begin
                    if (triangleY >= triangleX && triangleY<= 5'd24 - triangleX)
                    begin
                        triangle_on = 1'b1;
                    end
                end
                menu_on = 1'b1;
            end
            if (map[positionX + positionY * 10] == 1'b1)
                map_on = 1'b1;
            else if (positionX + 2 >= TetroX &&  positionX < TetroX + 6'd2 && positionY >= TetroY && positionY < TetroY + 6'd4)
            begin
                if (block[positionY - TetroY][1'd1 - positionX + TetroX] == 1'b1)
                begin
                    block_on = 1'b1;
                end
            end
            if (DrawX[9:2] >= 7'd71 && DrawX[9:2] <= 7'd88 && DrawY[9:2] >= 6'd59 && DrawY[9:2] <= 6'd60)
            begin
                game_over_on = 1'b1;
            end

            canvas_on = 1'b1;
        end
        
        //else 
          //  canvas_on = 1'b0;
     end 
       
    always_comb
    begin

        if((in_progress && next_block_on) || (start && start_block_on))
        begin
            if (blockX < 4'd2 || blockY > 4'd13)
            begin
                Red = 4'hc;
                Green = 4'h6;
                Blue = 4'h0;
            end
            else if (blockY < 4'd2 || blockY > 4'd13)
            begin
                Red = 4'hf;
                Green = 4'ha;
                Blue = 4'h0;
            end
            else
            begin
                Red = 4'hF;
                Green = 4'h7;
                Blue = 4'h0;
            end
        end
        else if(canvas_on || next_canvas_on)
        begin         
            Red = 4'hf;
            Green = 4'hf;
            Blue = 4'hf;
            if(in_progress == 1'b1)
            begin
                if ((map_on)) 
                begin 
                    if (blockX < 4'd2 || blockY > 4'd13)
                    begin
                        Red = 4'hc;
                        Green = 4'h6;
                        Blue = 4'h0;
                    end
                    else if (blockY < 4'd2 || blockX > 4'd13)
                    begin
                        Red = 4'hf;
                        Green = 4'ha;
                        Blue = 4'h0;
                    end
                    else
                    begin
                        Red = 4'hF;
                        Green = 4'h7;
                        Blue = 4'h0;
                    end
                end
                else if (block_on)
                begin
                    case (Tetro[2:1])
                        2'b00: begin
                            if (blockX < 4'd2 || blockY > 4'd13) begin
                                Red = 4'h0;
                                Green = 4'h6;
                                Blue = 4'h0; // Shadow
                            end else if (blockY < 4'd2 || blockX > 4'd13) begin
                                Red = 4'h0;
                                Green = 4'hC;
                                Blue = 4'h0; // Highlight
                            end else begin
                                Red = 4'h0;
                                Green = 4'h9;
                                Blue = 4'h0; // Default
                            end
                        end
                        2'b01: begin
                            if (blockX < 4'd2 || blockY > 4'd13) begin
                                Red = 4'h0;
                                Green = 4'h0;
                                Blue = 4'h6; // Shadow
                            end else if (blockY < 4'd2 || blockX > 4'd13) begin
                                Red = 4'h0;
                                Green = 4'h0;
                                Blue = 4'hC; // Highlight
                            end else begin
                                Red = 4'h0;
                                Green = 4'h0;
                                Blue = 4'h9; // Default
                            end
                        end
                        2'b10: begin
                            if (blockX < 4'd2 || blockY > 4'd13) begin
                                Red = 4'h8;
                                Green = 4'h4;
                                Blue = 4'h0; // Shadow
                            end else if (blockY < 4'd2 || blockX > 4'd13) begin
                                Red = 4'hF;
                                Green = 4'hC;
                                Blue = 4'h0; // Highlight
                            end else begin
                                Red = 4'hC;
                                Green = 4'h8;
                                Blue = 4'h0; // Default
                            end
                        end
                        2'b11: begin
                            if (blockX < 4'd2 || blockY > 4'd13) begin
                                Red = 4'h8;
                                Green = 4'h0;
                                Blue = 4'h6; // Shadow
                            end else if (blockY < 4'd2 || blockX > 4'd13) begin
                                Red = 4'hF;
                                Green = 4'h0;
                                Blue = 4'hD; // Highlight
                            end else begin
                                Red = 4'hC;
                                Green = 4'h0;
                                Blue = 4'hA; // Default
                            end
                        end
                        default: begin
                            Red = 4'h8;
                            Green = 4'h8;
                            Blue = 4'h8; // Default gray
                        end
                    endcase
                end
            end
            else if (start == 1'b1)
            begin
                if (menu_on == 1'b1)
                begin
                // botton（）
                    if (triangle_on == 1'b1)
                    begin
                        Red   = 4'h8;
                        Green = 4'hF;
                        Blue  = 4'hF;
                    end
                    else
                    begin
                        Red   = 4'h8;
                        Green = 4'hF;
                        Blue  = 4'h8;
                    end
                end
            end
            else if (end_game == 1'b1)
            begin
                if (game_over_on == 1'b1)
                begin
                // botton（）
                    Red   = Red_E;
                    Green = Green_E;
                    Blue  = Blue_E;
                end
            end
        end
        else
        begin
            if (blockX < 4'd2 || blockY > 4'd13)
            begin
                Red = 4'h4;
                Green = 4'h4;
                Blue = 4'h4;
            end
            else if (blockY < 4'd2 || blockX > 4'd13)
            begin
                Red = 4'hC;
                Green = 4'hC;
                Blue = 4'hC;
            end
            else
            begin
                Red = 4'h8;
                Green = 4'h8;
                Blue = 4'h8;
            end
        end
    end
endmodule
