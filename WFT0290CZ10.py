from micropython import const
from time import sleep_ms
import framebuf
import ustruct

# Display resolution
EPD_WIDTH  = const(128)
EPD_HEIGHT = const(297)


# Display commands
PANEL_SETTING                  = const(0x00)
POWER_SETTING                  = const(0x01)
POWER_OFF                      = const(0x02)
POWER_ON                       = const(0x04)
BOOSTER_SOFT_START             = const(0x06)
DATA_START_TRANSMISSION_1      = const(0x10)
DISPLAY_REFRESH                = const(0x12)
DATA_START_TRANSMISSION_2      = const(0x13)

VCOM_AND_DATA_INTERVAL_SETTING = const(0x50)

TCON_RESOLUTION                = const(0x61)

VCM_DC_SETTING_REGISTER        = const(0x82)
    
BUSY = const(0)  # 0=busy, 1=idle

class EPD():   
    def __init__(self,  spi, cs, dc, rst, busy):
        self.spi  = spi
        self.cs   = cs
        self.dc   = dc
        self.rst  = rst
        self.busy = busy
        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        self.rst.init(self.rst.OUT, value=0)
        self.busy.init(self.busy.IN)
        self.init_display()
        self.buf_B = bytearray(((EPD_HEIGHT+7)//8)* EPD_WIDTH)
        self.buf_R = bytearray(((EPD_HEIGHT+7)//8)* EPD_WIDTH)
    def write_cmd(self, command, data=None):
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([command]))
        self.cs(1)
        if data is not None:
            self.write_data(data)

    def write_data(self, data):
        self.dc(1)
        self.cs(0)
        self.spi.write(data)
        self.cs(1)

    def init_display(self):
        self.reset()
        self.write_cmd(BOOSTER_SOFT_START, b'\x17\x17\x17')
        self.write_cmd(POWER_ON)
        self.write_cmd(PANEL_SETTING, b'\x83')
        self.write_cmd(TCON_RESOLUTION, ustruct.pack(">BH", EPD_WIDTH, EPD_HEIGHT))
        self.write_cmd(VCM_DC_SETTING_REGISTER, b'\x0A')
 
    def wait_until_idle(self):
        sleep_ms(10)
        while self.busy.value() == BUSY:
            sleep_ms(10)

    def reset(self):
        self.rst(0)
        sleep_ms(20)
        self.rst(1)
        sleep_ms(20)

    def show(self):

        self.write_cmd(DATA_START_TRANSMISSION_1)
        self.write_data(self.buf_B)
        self.write_cmd(DATA_START_TRANSMISSION_2)
        self.write_data(self.buf_R)
        self.write_cmd(DISPLAY_REFRESH)
        self.wait_until_idle()

    def sleep(self):
        self.write_cmd(VCOM_AND_DATA_INTERVAL_SETTING, b'\x37')
        self.write_cmd(VCM_DC_SETTING_REGISTER, b'\x00') # to solve Vcom drop
        self.write_cmd(POWER_SETTING, b'\x02\x00\x00\x00') # gate switch to external
        self.wait_until_idle()
        self.write_cmd(POWER_OFF)
    
class EPD_B(framebuf.FrameBuffer):
    def __init__(self,buffer, rot=0):
        if rot==0:
            super().__init__(buffer, EPD_WIDTH, EPD_HEIGHT, framebuf.MONO_HMSB)
        elif rot==1:
            super().__init__(buffer, EPD_HEIGHT, EPD_WIDTH, framebuf.MONO_HMSB + framebuf.MV + framebuf.MY)
        elif rot==2:
            super().__init__(buffer, EPD_WIDTH, EPD_HEIGHT, framebuf.MONO_HMSB + framebuf.MX + framebuf.MY)
        else:
            super().__init__(buffer, EPD_HEIGHT, EPD_WIDTH, framebuf.MONO_HMSB + framebuf.MV + framebuf.MX)
        
class EPD_R(framebuf.FrameBuffer):
    def __init__(self,buffer, rot=0):
        if rot==0:
            super().__init__(buffer, EPD_WIDTH, EPD_HEIGHT, framebuf.MONO_HMSB)
        elif rot==1:
            super().__init__(buffer, EPD_HEIGHT, EPD_WIDTH, framebuf.MONO_VMSB + framebuf.MV + framebuf.MY)
        elif rot==2:
            super().__init__(buffer, EPD_WIDTH, EPD_HEIGHT, framebuf.MONO_HMSB + framebuf.MX + framebuf.MY)
        else:
            super().__init__(buffer, EPD_HEIGHT, EPD_WIDTH, framebuf.MONO_VMSB + framebuf.MV + framebuf.MX)
