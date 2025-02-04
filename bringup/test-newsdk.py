from ttboard import cocotb
from ttboard.cocotb.clock import Clock
from ttboard.cocotb.triggers import Timer
from ttboard.cocotb.time.system import SystemTime
from ttboard.demoboard import DemoBoard

height, width = 8, 8

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

testvec = (0,0,1,1,0,0,0,0,1,0,0,1,1,0,1,1,1,1)

def bin8(val):
    bin_suff = bin(val)[2:]
    return '0b' + '0' * (8-len(bin_suff)) + bin_suff

test_results = []

def test_eq(val1, val2):
    passed = val1 == val2
    test_results.append(passed)
    passed_str = 'PASSED' if passed else 'FAILED'
    print(f'TEST {passed_str}: {bin8(val1)} == {bin8(val2)}')

async def delay():
    await Timer(1, units='ms')
    #SystemTime.advance(1, 'ms')

async def ticktock(dut):
    dut.clk.value = 1
    await Timer(10, units='ms')
    #SystemTime.advance(10, 'ms')
    dut.clk.value = 0
    await Timer(10, units='ms')
    #SystemTime.advance(10, 'ms')

@cocotb.test()
async def test_fpga(dut):
  
    dut._log.info("testing reset propagation")

    dut.rst_n.value = 0
    dut.clk.value = 0
    for i in range(height * width + 1):
        await ticktock(dut)
    dut.rst_n.value = 1
    await ticktock(dut)
    
    dut._log.info("testing configuration upload")

    dut.in_lb.value = 1
    dut.in_lbc.value = 0
    for k in range(4):
        dut.in_se.value = 1
        dut.in_cfg.value = 0
        for l in reversed(fpga_config):
            for v in reversed(l):
                dut.in_sc.value = (v >> k) & 1
                await ticktock(dut)
        dut.in_cfg.value = 3-k
        await delay()
        dut.in_cfg.value = 0
    dut.in_se.value = 0

    dut._log.info("testing data upload, single step & download")

    dut.ui_in.value = 0
    dut.in_cfg.value = 0
    for test in range(18):
        rotated = testvec[test:] + testvec[:test]
        in1, in2 = [], []
        for i, t in enumerate(rotated):
            if i % 2:
                in2.append(t)
            else:
                in1.append(t)
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
        await delay()
        dut._log.info(f"round {test}, propagation test 1")
        for prop in range(50):
            for lbc in (1, 2, 3, 0):
                dut.in_lbc.value = lbc
                await delay()
        dut._log.info(f"round {test}, single step")
        await ticktock(dut)
        dut._log.info(f"round {test}, propagation test 2")
        for prop in range(50):
            for lbc in (1, 2, 3, 0):
                dut.in_lbc.value = lbc
                await delay()
        dut._log.info(f"round {test}, data download")
        dut.in_se.value = 1
        dut.in_sc.value = 0
        await delay()
        test_out = 0
        test_ref = 0
        for j in reversed(range(height)):
            for i in reversed(range(width)):
                if fpga_out[j][i] != 0:
                    test_out = (test_out << 1) | dut.out_sc.value
                    test_ref = (test_ref << 1) | out[fpga_out[j][i]-1]
                await ticktock(dut)
        dut.in_se.value = 0
        await delay()
        assert test_out == test_ref

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
        dut.in_cfg.value = 3-k
        await delay()
        dut.in_cfg.value = 0
    dut.in_se.value = 0
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
        print(f"custom input, manual cycles, step {i}")
        for prop in range(50):
            for lbc in (1, 2, 3, 0):
                dut.in_lbc.value = lbc
                await delay()
        await ticktock(dut)
    assert dut.uo_out.value == 0b11010010
    dut.ui_in.value = 0
    dut._log.info("zero input, automatic cycles")
    dut.in_lb.value = 0
    await delay()
    for i in range(3):
        await ticktock(dut)
    assert dut.uo_out.value == 0b10101010
    dut.ui_in.value = 0b01110010
    print("custom input, automatic cycles")
    for i in range(3):
        await ticktock(dut)
    assert dut.uo_out.value == 0b11010010
    dut.in_lb.value = 1
    await delay()

    dut._log.info("finished")
    dut._log.info(f"{sum(test_results)} out of {len(test_results)} tests passed")
    if all(test_results):
        dut._log.info("ALL TESTS PASSED")
    else:
        dut._log.info("SOME TESTS FAILED")

def main():
    from ttboard.cocotb.dut import DUTWrapper
    
    class DUT(DUTWrapper):
        def __init__(self):
            super().__init__()
            self.tt = DemoBoard.get()
            
            # inputs
            self.in_se = self.new_slice_attribute(self.tt.uio_in, 0)
            self.in_sc = self.new_slice_attribute(self.tt.uio_in, 1)
            self.in_cfg = self.new_slice_attribute(self.tt.uio_in, 3, 2)
            self.in_lb = self.new_slice_attribute(self.tt.uio_in, 4)
            self.in_lbc = self.new_slice_attribute(self.tt.uio_in, 6, 5)
            
            # outputs
            self.out_sc = self.new_slice_attribute(self.tt.uio_out, 7)

    tt = DemoBoard.get()
    tt.shuttle.tt_um_htfab_rotfpga2.enable()
    tt.clock_project_stop()
    Clock.clear_all()

    # pin directions
    tt.uio_oe_pico.value = 0x7f  # pins 0-6 driven by rp2040, pin 7 driven by user project
    
    dut = DUT()
    dut._log.info("enabled rotfpga2")
    runner = cocotb.get_runner()
    runner.test(dut)

if __name__ == '__main__':
    main()
