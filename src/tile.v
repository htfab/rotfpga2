`default_nettype none

module tile (
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

// configuration latches to store the current state of vertical, horizontal and diagonal flips
// w_v, w_h, w_d are the currently latched values
// in_v, in_h, in_d specify whether to update the latches
// out_sc is the potential new value, coming from the tile's flip-flop

sky130_fd_sc_hd__mux2_1 cw_v(.A0(w_v), .A1(out_sc), .S(in_v), .X(w_v));
sky130_fd_sc_hd__mux2_1 cw_h(.A0(w_h), .A1(out_sc), .S(in_h), .X(w_h));
sky130_fd_sc_hd__mux2_1 cw_d(.A0(w_d), .A1(out_sc), .S(in_d), .X(w_d));

// convert inputs of the rotated/reflected tile to inputs of the original upright tile
// top, right, bottom, left inputs of the rotated/reflected tile are in_t, in_r, in_b, in_l

// vertical flip
sky130_fd_sc_hd__mux2_1 cw_vt(.A0(in_t), .A1(in_b), .S(w_v), .X(w_vt));
sky130_fd_sc_hd__mux2_1 cw_vb(.A0(in_b), .A1(in_t), .S(w_v), .X(w_vb));
// horizontal flip
sky130_fd_sc_hd__mux2_1 cw_hr(.A0(in_r), .A1(in_l), .S(w_h), .X(w_hr));
sky130_fd_sc_hd__mux2_1 cw_hl(.A0(in_l), .A1(in_r), .S(w_h), .X(w_hl));
// diagonal flip
sky130_fd_sc_hd__mux2_1 cw_dh(.A0(w_hl), .A1(w_vt), .S(w_d), .X(w_dh));
sky130_fd_sc_hd__mux2_1 cw_dv(.A0(w_vt), .A1(w_hl), .S(w_d), .X(w_dv));

// top input of the upright tile is w_dv
// left input of the upright tile is w_dh
// right and bottom inputs of the upright tile are w_hr and w_vb in some order
//
//         A     V
//   +-----|-----|-----+
//   |  /==:=====/     |
//   |  |  |           |
// >====:==:=====+=======>
//   |  |  |     |     |
//   |  D  ~&    |     |
// <====/  |\====:=======<
//   |     |     |     |
//   |     |     |     |
//   +-----|-----|-----+
//         A     V
//
// top output of the upright tile is w_na
// left output of the upright tile is out_sc
// right and bottom outputs of the upright tile are both w_dh

// flip-flop with scan chain override
sky130_fd_sc_hd__sdfxtp_1 cout_sc(.CLK(clk), .D(w_dv), .SCD(in_sc), .SCE(in_se), .Q(out_sc));
// nand gate
sky130_fd_sc_hd__nand2_1 cw_na(.A(w_hr), .B(w_vb), .Y(w_na));

// implement the loop breaker functionality
// w_gnl and w_ghl are the latched versions of w_na and w_dh respectively
// they are only updated when in_lb is low

sky130_fd_sc_hd__mux2_1 cw_gn(.A0(w_na), .A1(w_gnl), .S(in_lb), .X(w_gnl));
sky130_fd_sc_hd__mux2_1 cw_gh(.A0(w_dh), .A1(w_ghl), .S(in_lb), .X(w_ghl));

// to save on chip space, we don't use the loop breaker in every tile
// but we have to make this selection in the parent module
// so we pass back both the latched and unlatched values to the parent module
// we get back either the latched or the unlatched values
// if we get back the unlatched ones, the latches will be optimized out during synthesis

assign bo_b = {w_na, w_dh};
assign bo_l = {w_gnl, w_ghl};
assign {w_gn, w_gh} = bi_l;

// finally we convert the outputs of the upright tile to those of the rotated/reflected one
// top output of the upright tile (with possible latching) is w_gn
// left output of the upright tile is out_sc
// right and bottom outputs of the upright tile (with possible latching) is w_gh

// diagonal flip
sky130_fd_sc_hd__mux2_1 cw_oh(.A0(out_sc), .A1(w_gn), .S(w_d), .X(w_oh));
sky130_fd_sc_hd__mux2_1 cw_ov(.A0(w_gn), .A1(out_sc), .S(w_d), .X(w_ov));
// vertical flip
sky130_fd_sc_hd__mux2_1 cout_t(.A0(w_ov), .A1(w_gh), .S(w_v), .X(out_t));
sky130_fd_sc_hd__mux2_1 cout_b(.A0(w_gh), .A1(w_ov), .S(w_v), .X(out_b));
// horizontal flip
sky130_fd_sc_hd__mux2_1 cout_r(.A0(w_gh), .A1(w_oh), .S(w_h), .X(out_r));
sky130_fd_sc_hd__mux2_1 cout_l(.A0(w_oh), .A1(w_gh), .S(w_h), .X(out_l));

// top, right, bottom left outputs of the rotated/reflected tile are out_t, out_r, out_b, out_l

endmodule

`default_nettype wire

