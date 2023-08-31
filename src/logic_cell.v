`default_nettype none

module logic_cell(
   input clk,     // clock
   input in_se,   // scan chain enable
   input in_sc,   // scan chain input
   input in_lb,   // loop breaker
   input in_v,    // vertical flip
   input in_h,    // horizontal flip
   input in_d,    // diagonal flip
   input in_t,    // top input
   input in_r,    // right input
   input in_b,    // bottom input
   input in_l,    // left input
   input [1:0] bi_l,  // loop breaker inserts
   output [1:0] bo_b, //   bypass: bi_l <- bo_b
   output [1:0] bo_l, //   latch:  bi_l <- bo_l
   output out_sc, // scan chain output
   output out_t,  // top output
   output out_r,  // right output
   output out_b,  // bottom output
   output out_l   // left output
);

wire w_v, w_h, w_d, w_vt, w_vb, w_hr, w_hl, w_dh, w_dv, w_na;
wire w_dhl, w_nal, w_gnl, w_ghl, w_gn, w_gh, w_oh, w_ov;

sky130_fd_sc_hd__mux2_1 cw_v(.A0(w_v), .A1(out_sc), .S(in_v), .X(w_v));
sky130_fd_sc_hd__mux2_1 cw_h(.A0(w_h), .A1(out_sc), .S(in_h), .X(w_h));
sky130_fd_sc_hd__mux2_1 cw_d(.A0(w_d), .A1(out_sc), .S(in_d), .X(w_d));

sky130_fd_sc_hd__mux2_1 cw_vt(.A0(in_t), .A1(in_b), .S(w_v), .X(w_vt));
sky130_fd_sc_hd__mux2_1 cw_vb(.A0(in_b), .A1(in_t), .S(w_v), .X(w_vb));
sky130_fd_sc_hd__mux2_1 cw_hr(.A0(in_r), .A1(in_l), .S(w_h), .X(w_hr));
sky130_fd_sc_hd__mux2_1 cw_hl(.A0(in_l), .A1(in_r), .S(w_h), .X(w_hl));
sky130_fd_sc_hd__mux2_1 cw_dh(.A0(w_hl), .A1(w_vt), .S(w_d), .X(w_dh));
sky130_fd_sc_hd__mux2_1 cw_dv(.A0(w_vt), .A1(w_hl), .S(w_d), .X(w_dv));

sky130_fd_sc_hd__sdfxtp_1 cout_sc(.CLK(clk), .D(w_dv), .SCD(in_sc), .SCE(in_se), .Q(out_sc));
sky130_fd_sc_hd__nand2_1 cw_na(.A(w_hr), .B(w_vb), .Y(w_na));

sky130_fd_sc_hd__mux2_1 cw_gn(.A0(w_na), .A1(w_gnl), .S(in_lb), .X(w_gnl));
sky130_fd_sc_hd__mux2_1 cw_gh(.A0(w_dh), .A1(w_ghl), .S(in_lb), .X(w_ghl));

assign bo_b = {w_na, w_dh};
assign bo_l = {w_gnl, w_ghl};
assign {w_gn, w_gh} = bi_l;

sky130_fd_sc_hd__mux2_1 cw_oh(.A0(out_sc), .A1(w_gn), .S(w_d), .X(w_oh));
sky130_fd_sc_hd__mux2_1 cw_ov(.A0(w_gn), .A1(out_sc), .S(w_d), .X(w_ov));
sky130_fd_sc_hd__mux2_1 cout_t(.A0(w_ov), .A1(w_gh), .S(w_v), .X(out_t));
sky130_fd_sc_hd__mux2_1 cout_b(.A0(w_gh), .A1(w_ov), .S(w_v), .X(out_b));
sky130_fd_sc_hd__mux2_1 cout_r(.A0(w_gh), .A1(w_oh), .S(w_h), .X(out_r));
sky130_fd_sc_hd__mux2_1 cout_l(.A0(w_oh), .A1(w_gh), .S(w_h), .X(out_l));

endmodule

`default_nettype wire

