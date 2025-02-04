from ttboard.demoboard import DemoBoard, Pins
from time import sleep_ms
import random

tt = DemoBoard()

tt.clock_project_stop()
tt.shuttle.tt_um_htfab_rotfpga2.enable()
tt.reset_project(True)
tt.project_clk(0)

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

for i in range(7):
    tt.bidirs[i].mode = Pins.OUT
tt.bidirs[7].mode = Pins.IN

def multibit(bits):
    def call(value=None):
        if value is None:
            value = 0
            for bit in reversed(bits):
                value <<= 1
                value |= bit()
            return value
        else:
            for bit in bits:
                bit(value & 1)
                value >>= 1
    return call

def bin8(val):
    bin_suff = bin(val)[2:]
    return '0b' + '0' * (8-len(bin_suff)) + bin_suff

test_results = []

def test_eq(val1, val2):
    passed = val1 == val2
    test_results.append(passed)
    passed_str = 'PASSED' if passed else 'FAILED'
    print(f'TEST {passed_str}: {bin8(val1)} == {bin8(val2)}')

in_se = tt.bidirs[0]
in_sc = tt.bidirs[1]
in_cfg = multibit((tt.bidirs[2], tt.bidirs[3]))
in_lb = tt.bidirs[4]
in_lbc = multibit((tt.bidirs[5], tt.bidirs[6]))
out_sc = tt.bidirs[7]

ui_in = multibit(tt.inputs)
uo_out = multibit(tt.outputs)

def ticktock():
    tt.clock_project_once(10)

def delay():
    sleep_ms(1)

height, width = 8, 8

tt.reset_project(True)
for i in range(height * width + 1):
    ticktock()
tt.reset_project(False)
ticktock()

print("testing configuration upload")

in_lb(1)
in_lbc(0)
for k in range(4):
    in_se(1)
    in_cfg(0)
    for l in reversed(fpga_config):
        for v in reversed(l):
            in_sc( (v >> k) & 1 )
            ticktock()
    in_cfg(3-k)
    delay()
    in_cfg(0)
in_se(0)

print("testing data upload, single step & download")

ui_in(0)
in_cfg(0)
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
    print(f"round {test}, data upload")
    in_lb(1)
    in_lbc(0)
    in_se(1)
    for l in reversed(data):
        for v in reversed(l):
            in_sc(v)
            ticktock()
    in_se(0)
    delay()
    print(f"round {test}, propagation test 1")
    for prop in range(50):
        for lbc in (1, 2, 3, 0):
            in_lbc(lbc)
            delay()
    print(f"round {test}, single step")
    ticktock()
    print(f"round {test}, propagation test 2")
    for prop in range(50):
        for lbc in (1, 2, 3, 0):
            in_lbc(lbc)
            delay()
    print(f"round {test}, data download")
    in_se(1)
    in_sc(0)
    delay()
    test_out = 0
    test_ref = 0
    for j in reversed(range(height)):
        for i in reversed(range(width)):
            if fpga_out[j][i] != 0:
                test_out = (test_out << 1) | out_sc()
                test_ref = (test_ref << 1) | out[fpga_out[j][i]-1]
            ticktock()
    in_se(0)
    delay()
    test_eq(test_out, test_ref)

print("testing io & multi-step propagation")
ui_in(0)
print("zero input")
for i in range(3):
    for prop in range(50):
        for lbc in (1, 2, 3, 0):
            in_lbc(lbc)
            delay()
    ticktock()
test_eq(uo_out(), 0b01010101)
ui_in(0b01110010)
for i in range(3):
    print(f"custom input, step {i}")
    for prop in range(50):
        for lbc in (1, 2, 3, 0):
            in_lbc(lbc)
            delay()
    ticktock()
test_eq(uo_out(), 0b10011100)

print("testing loop breaker")
in_lb(1)
in_lbc(0)
print("reconfiguration")
for k in range(4):
    in_se(1)
    in_cfg(0)
    for j in reversed(range(height)):
        for i in reversed(range(width)):
            cfg = {(0, 0): 0, (0, 1): 5, (1, 0): 6, (1, 1): 3}[(j%2, i%2)]
            in_sc( (cfg>>k) & 1 )
            ticktock()
    in_cfg(3-k)
    delay()
    in_cfg(0)
in_se(0)
ui_in(0)
print("zero input, manual cycles")
for i in range(3):
    for prop in range(50):
        for lbc in (1, 2, 3, 0):
            in_lbc(lbc)
            delay()
    ticktock()
test_eq(uo_out(), 0b10101010)
ui_in(0b01110010)
for i in range(3):
    print(f"custom input, manual cycles, step {i}")
    for prop in range(50):
        for lbc in (1, 2, 3, 0):
            in_lbc(lbc)
            delay()
    ticktock()
test_eq(uo_out(), 0b11010010)
ui_in(0)
print("zero input, automatic cycles")
in_lb(0)
delay()
for i in range(3):
    ticktock()
test_eq(uo_out(), 0b10101010)
ui_in(0b01110010)
print("custom input, automatic cycles")
for i in range(3):
    ticktock()
test_eq(uo_out(), 0b11010010)
in_lb(1)
delay()

print("finished")
print(f"{sum(test_results)} out of {len(test_results)} tests passed")
if all(test_results):
    print("ALL TESTS PASSED")
else:
    print("SOME TESTS FAILED")
