import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles
import os

fpga_config = (
    (0,0,6,0,3,5,1,2),
    (5,3,0,0,3,3,4,2),
    (0,0,5,5,6,6,1,2),
    (5,3,3,5,6,0,4,2),
    (0,0,7,1,2,4,1,2),
    (5,3,1,1,2,2,4,2),
    (0,0,4,4,7,7,1,2),
    (5,3,2,4,7,1,4,2),
)

fpga_in1 = (
    (0,0,1,0,0,2,0,0),
    (0,0,0,0,0,0,0,0),
    (0,0,0,0,0,0,0,0),
    (0,0,4,0,0,3,0,0),
    (0,0,5,0,0,8,0,0),
    (0,0,0,0,0,0,0,0),
    (9,0,0,0,0,0,0,0),
    (0,0,6,0,0,7,0,0),
)

fpga_in2 = (
    (0,0,0,0,0,0,0,0),
    (0,0,0,4,1,0,0,0),
    (0,0,0,3,2,0,0,0),
    (0,0,0,0,0,0,0,0),
    (0,0,0,0,0,0,0,0),
    (0,0,0,8,7,0,0,0),
    (0,0,0,5,6,9,0,0),
    (0,0,0,0,0,0,0,0),
)

fpga_out = (
    (0,0,4,0,0,1,0,0),
    (0,0,0,0,0,0,0,0),
    (0,0,0,0,0,0,0,0),
    (0,0,3,0,0,2,0,0),
    (0,0,8,0,0,7,0,0),
    (0,0,0,0,0,0,0,0),
    (0,0,0,0,0,9,0,0),
    (0,0,5,0,0,6,0,0),
)


class Cells:
    dut, height, width = None, None, None
    def __init__(self, dut, height, width):
        self.dut, self.height, self.width = dut, height, width
    def path(self, y, x, comp):
        try:
            return getattr(self.dut.dut.g.g_y[y].g_x[x].t, comp)
        except AttributeError:
            try:
                return self.dut.dut._id(f'\\g.g_y[{y}].g_x[{x}].t.{comp}', extended=False)
            except AttributeError:
                class Missing:
                    value = '?'
                return Missing()
    def in_se(self, y, x):
        return self.path(y, x, 'in_se')
    def in_sc(self, y, x):
        return self.path(y, x, 'in_sc')
    def in_v(self, y, x):
        return self.path(y, x, 'in_v')
    def in_h(self, y, x):
        return self.path(y, x, 'in_h')
    def in_d(self, y, x):
        return self.path(y, x, 'in_d')
    def in_t(self, y, x):
        return self.path(y, x, 'in_t')
    def in_r(self, y, x):
        return self.path(y, x, 'in_r')
    def in_b(self, y, x):
        return self.path(y, x, 'in_b')
    def in_l(self, y, x):
        return self.path(y, x, 'in_l')
    def w_dv(self, y, x):
        return self.path(y, x, 'w_dv')
    def w_hr(self, y, x):
        return self.path(y, x, 'w_hr')
    def w_vb(self, y, x):
        return self.path(y, x, 'w_vb')
    def w_dh(self, y, x):
        return self.path(y, x, 'w_dh')
    def w_na(self, y, x):
        return self.path(y, x, 'w_na')
    def w_ov(self, y, x):
        return self.path(y, x, 'w_ov')
    def w_gn(self, y, x):
        return self.path(y, x, 'w_gn')
    def w_gh(self, y, x):
        return self.path(y, x, 'w_gh')
    def w_oh(self, y, x):
        return self.path(y, x, 'w_oh')
    def out_sc(self, y, x):
        return self.path(y, x, 'out_sc')
    def out_t(self, y, x):
        return self.path(y, x, 'out_t')
    def out_r(self, y, x):
        return self.path(y, x, 'out_r')
    def out_b(self, y, x):
        return self.path(y, x, 'out_b')
    def out_l(self, y, x):
        return self.path(y, x, 'out_l')
    def w_v(self, y, x):
        return self.path(y, x, 'w_v')
    def w_h(self, y, x):
        return self.path(y, x, 'w_h')
    def w_d(self, y, x):
        return self.path(y, x, 'w_d')
    def config(self, y, x):
        return str(self.w_v(y, x).value) + str(self.w_h(y, x).value) + str(self.w_d(y, x).value)
    def data(self, y, x):
        return str(self.out_sc(y, x).value)
    def state(self, y, x):
        return self.config(y, x) + self.data(y, x)
    def fullstate(self):
        return ', '.join(' '.join(self.state(y, x) for x in range(self.width)) for y in range(self.height))

async def ticktock(dut):
    dut.clk.value = 1
    await Timer(10, units='ns')
    dut.clk.value = 0
    await Timer(10, units='ns')

async def delay():
    await Timer(1, units='ns')

@cocotb.test()
async def test_fpga(dut):
    dut._log.info("start")
    gatelevel = os.environ.get('GATES') == 'yes'
    height, width = 8, 8
    cells = Cells(dut, height, width)

    dut._log.info("testing reset logic")
    fs = cells.fullstate()
    assert fs == ('xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx, xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx, '
                  'xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx, xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx, '
                  'xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx, xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx, '
                  'xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx, xxxx xxxx xxxx xxxx xxxx xxxx xxxx xxxx')
    dut.rst_n.value = 0
    for i in range(height * width + 1):
        await ticktock(dut)
    dut.rst_n.value = 1
    await ticktock(dut)
    fs = cells.fullstate()
    assert fs == ('0000 0000 0000 0000 0000 0000 0000 0000, 0000 0000 0000 0000 0000 0000 0000 0000, '
                  '0000 0000 0000 0000 0000 0000 0000 0000, 0000 0000 0000 0000 0000 0000 0000 0000, '
                  '0000 0000 0000 0000 0000 0000 0000 0000, 0000 0000 0000 0000 0000 0000 0000 0000, '
                  '0000 0000 0000 0000 0000 0000 0000 0000, 0000 0000 0000 0000 0000 0000 0000 0000')

    dut._log.info("testing configuration upload")
    dut.in_lb.value = 1
    dut.in_lbc.value = 0
    for k in range(4):
        dut.in_se.value = 1
        dut.in_cfg.value = 0
        for l in reversed(fpga_config):
            for v in reversed(l):
                dut.in_sc.value = (v>>k) & 1
                await ticktock(dut)
        dut.in_se.value = 0
        dut.in_cfg.value = 3-k
        await ticktock(dut)
    fs = cells.fullstate()
    cmps = ', '.join(' '.join(bin(fpga_config[y][x]*2)[2:].rjust(4, '0') for x in range(width)) for y in range(height))
    assert fs == cmps

    dut._log.info("testing data upload, single step & download")
    testvec = (0,0,1,1,0,0,0,0,1,0,0,1,1,0,1,1,1,1)
    dut.ui_in.value = 0
    dut.in_cfg.value = 0
    for test in range(18):
        rotated = testvec[test:] + testvec[:test]
        in1 = rotated[0::2]
        in2 = rotated[1::2]
        out = tuple((i&j)^1 for i, j in zip(in1, in2))
        data = [list(rotated[j:j+width]) for j in range(height)]  # used as noise only
        for j in range(height):
            for i in range(width):
                # override data at points that actually matter
                if fpga_in1[j][i] != 0:
                    data[j][i] = in1[fpga_in1[j][i]-1]
                if fpga_in2[j][i] != 0:
                    data[j][i] = in2[fpga_in2[j][i]-1]
        dut._log.info(f"round {test}, data upload")
        dut.in_lb.value = 1
        dut.in_lbc.value = 0
        dut.in_se.value = 1
        for l in reversed(data):
            for v in reversed(l):
                dut.in_sc.value = v
                await ticktock(dut)
        dut.in_se.value = 0
        await ticktock(dut)
        dut._log.info(f"round {test}, propagation test 1")
        for prop in range(50):
            for lbc in (1, 2, 3, 0):
                dut.in_lbc.value = lbc
                await delay()
        for j in range(height):
            for i in range(width):
                if fpga_out[j][i] != 0:
                    assert cells.out_sc(j, i).value == data[j][i]
        dut._log.info(f"round {test}, single step")
        await ticktock(dut)
        for j in range(height):
            for i in range(width):
                if fpga_out[j][i] != 0:
                    assert cells.out_sc(j, i).value == out[fpga_out[j][i]-1]
        dut._log.info(f"round {test}, propagation test 2")
        for prop in range(50):
            for lbc in (1, 2, 3, 0):
                dut.in_lbc.value = lbc
                await delay()
        for j in range(height):
            for i in range(width):
                if fpga_out[j][i] != 0:
                    assert cells.out_sc(j, i).value == out[fpga_out[j][i]-1]
        dut._log.info(f"round {test}, data download")
        dut.in_se.value = 1
        dut.in_sc.value = 0
        await ticktock(dut)
        out = [[cells.out_sc(j, i).value for i in range(width)] for j in range(height)]
        for j in reversed(range(height)):
            for i in reversed(range(width)):
                assert out[j][i] == dut.out_sc.value
                await ticktock(dut)
        dut.in_se.value = 0
        await ticktock(dut)

    dut._log.info("testing io & multi-step propagation")
    dut.ui_in.value = 0
    dut._log.info("zero input")
    for i in range(3):
        for prop in range(50):
            for lbc in (1, 2, 3, 0):
                dut.in_lbc.value = lbc
                await delay()
        await ticktock(dut)
    assert dut.uo_out.value == 0b01010101
    dut.ui_in.value = 0b01110010
    for i in range(3):
        dut._log.info(f"custom input, step {i}")
        for prop in range(50):
            for lbc in (1, 2, 3, 0):
                dut.in_lbc.value = lbc
                await delay()
        await ticktock(dut)
    assert dut.uo_out.value == 0b10011100

    dut._log.info("testing loop breaker")
    dut.in_lb.value = 1
    dut.in_lbc.value = 0
    dut._log.info("reconfiguration")
    for k in range(4):
        dut.in_se.value = 1
        dut.in_cfg.value = 0
        for j in reversed(range(height)):
            for i in reversed(range(width)):
                cfg = {(0, 0): 0, (0, 1): 5, (1, 0): 6, (1, 1): 3}[(j%2, i%2)]
                dut.in_sc.value = (cfg>>k) & 1
                await ticktock(dut)
        dut.in_se.value = 0
        dut.in_cfg.value = 3-k
        await ticktock(dut)
    dut.ui_in.value = 0
    dut._log.info("zero input, manual cycles")
    for i in range(3):
        for prop in range(50):
            for lbc in (1, 2, 3, 0):
                dut.in_lbc.value = lbc
                await delay()
        await ticktock(dut)
    assert dut.uo_out.value == 0b10101010
    dut.ui_in.value = 0b01110010
    for i in range(3):
        dut._log.info(f"custom input, manual cycles, step {i}")
        for prop in range(50):
            for lbc in (1, 2, 3, 0):
                dut.in_lbc.value = lbc
                await delay()
        await ticktock(dut)
    assert dut.uo_out.value == 0b11010010
    dut.ui_in.value = 0
    dut._log.info("zero input, automatic cycles")
    dut.in_lb.value = 0
    for i in range(3):
        await ticktock(dut)
    assert dut.uo_out.value == 0b10101010
    dut.ui_in.value = 0b01110010
    for i in range(3):
        dut._log.info(f"custom input, automatic cycles, step {i}")
        await ticktock(dut)
    assert dut.uo_out.value == 0b11010010
    dut.in_lb.value = 1

    dut._log.info("finished")

