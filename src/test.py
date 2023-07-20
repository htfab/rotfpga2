import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles


segments = [ 63, 6, 91, 79, 102, 109, 124, 7, 127, 103 ]

@cocotb.test()
async def test_7seg(dut):
    dut._log.info("start")
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    dut._log.info("reset")
    dut.rst_n.value = 0
    dut.compare.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("check all segments with default MAX_COUNT")
    for i in range(10):
        dut._log.info("check segment {}".format(i))
        await ClockCycles(dut.clk, 1000)
        #assert int(dut.segments.value) == segments[i]

        # all bidirectionals are set to output
        assert dut.uio_oe == 0xFF

    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("check all segments with MAX_COUNT set to 100")
    dut.compare.value = 100
    for i in range(10):
        dut._log.info("check segment {}".format(i))
        await ClockCycles(dut.clk, 100)
#        assert int(dut.segments.value) == segments[i]

