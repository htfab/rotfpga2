`default_nettype none
`timescale 1ns/1ps

/*
this testbench just instantiates the module and makes some convenient wires
that can be driven / tested by the cocotb test.py
*/

// testbench is controlled by test.py
module tb ();

    // this part dumps the trace to a vcd file that can be viewed with GTKWave
    initial begin
        $dumpfile ("tb.vcd");
        $dumpvars (0, tb);
        #1;
    end

    // wire up the inputs and outputs
    reg  clk;
    reg  rst_n;
    reg  ena;
    reg  in_se;
    reg  in_sc;
    reg  [1:0] in_cfg;
    reg  in_lb;
    reg  [1:0] in_lbc;
    reg  [7:0] ui_in;

    wire [7:0] uio_in;
    assign uio_in[0] = in_se;
    assign uio_in[1] = in_sc;
    assign uio_in[3:2] = in_cfg;
    assign uio_in[4] = in_lb;
    assign uio_in[6:5] = in_lbc;

    wire [7:0] uo_out;
    wire [7:0] uio_out;
    wire [7:0] uio_oe;
    wire out_sc = uio_out[7];

    tt_um_htfab_rotfpga2 dut (
    // include power ports for the Gate Level test
    `ifdef GL_TEST
        .VPWR( 1'b1),
        .VGND( 1'b0),
    `endif
        .ui_in      (ui_in),
        .uo_out     (uo_out),
        .uio_in     (uio_in),
        .uio_out    (uio_out),
        .uio_oe     (uio_oe),
        .ena        (ena),
        .clk        (clk),
        .rst_n      (rst_n)
        );

endmodule

