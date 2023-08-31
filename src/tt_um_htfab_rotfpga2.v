`default_nettype none

module tt_um_htfab_rotfpga2 (
    input  wire [7:0] ui_in,    // Dedicated inputs - connected to the input switches
    output wire [7:0] uo_out,   // Dedicated outputs - connected to the 7 segment display
    input  wire [7:0] uio_in,   // IOs: Bidirectional Input path
    output wire [7:0] uio_out,  // IOs: Bidirectional Output path
    output wire [7:0] uio_oe,   // IOs: Bidirectional Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // will go high when the design is enabled
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

    logic_grid lg (
        .clk(clk),
        .rst_n(rst_n),
        .in_se(uio_in[0]),
        .in_sc(uio_in[1]),
        .in_cfg(uio_in[3:2]),
        .in_lb(uio_in[4]),
        .in_lbc(uio_in[6:5]),
        .ins(ui_in),
        .out_sc(uio_out[7]),
        .outs(uo_out)
    );

    assign uio_out[6:0] = 7'b0000000;
    assign uio_oe[6:0] = 7'b0000000;
    assign uio_oe[7] = 1'b1;

endmodule
