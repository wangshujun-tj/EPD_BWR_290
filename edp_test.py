import time
from machine import Pin,SPI
from WFT0290CZ10 import EPD,EPD_B,EPD_R


spi = SPI(2, baudrate=20000000, polarity=0, phase=0, sck=Pin(26), mosi=Pin(27), miso=Pin(34))
print("init")
epd = EPD(spi, cs = Pin(25), dc= Pin(33), rst= Pin(32), busy= Pin(35))
epd_b = EPD_R(epd.buf_B,rot=3)
epd_r = EPD_R(epd.buf_R,rot=3)
#rot参数改变显示的方向

epd_b.font_load("GB2312-24.fon")
epd_r.font_load("GB2312-24.fon")
epd_b.font_set(0x23,0,1,0)
epd_r.font_set(0x23,0,1,0)
#两个fb空间分别加载字库和字体设置
#红色是反向显示的，如果红黑同时显示，红覆盖掉黑
for i in range(8):
    print(i)
    epd_b.fill(1)
    epd_r.fill(0)
    epd_b.text("中文和数字混合显示-%2.2d"%(i),0,0,0)
    epd_r.text("%2.2d"%(i),0,40,1)
    epd_r.show_bmp("pic/bw%3.3d.bmp"%(i),0,200,28)
    epd.show()
    time.sleep(5)    

