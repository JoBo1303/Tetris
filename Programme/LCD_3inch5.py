from machine import Pin,SPI,PWM,mem32,freq
import framebuf
from time import sleep_ms, sleep_us, ticks_diff, ticks_us
from micropython import const,heap_lock
import ustruct,gc
from random import randint
from usys import exit

LCD_DC   = const(8)
LCD_CS   = const(9)
LCD_SCK  = const(10)
LCD_MOSI = const(11)
LCD_MISO = const(12)
LCD_BL   = const(13)
LCD_RST  = const(15)
TP_CS    = const(16)
TP_IRQ   = const(17)
_CASET = const(0x2a) # Column Address Set
_PASET = const(0x2b) # Page Address Set
_RAMWR = const(0x2c) # Memory Write
_RAMRD = const(0x2e) # Memory Read
MEMORY_BUFFER = const(200) #1024) # SPI Write Buffer
COLUMN_ADDRESS_SET = const(0x2a);PAGE_ADDRESS_SET = const(0x2b);RAM_WRITE = const(0x2c);RAM_READ = const(0x2e)

class LCD_3inch5(framebuf.FrameBuffer):
    def __init__(self, mem = 200):
        self.RED   =   0x07E0
        self.GREEN =   0x001f
        self.BLUE  =   0xf800
        self.WHITE =   0xffff
        self.BLACK =   0x0000
        self.YELLOW =  0xE0FF
        self.ORANGE =  0x20FD
        self.GRAY =  0x7BEF
        self.MAGENTA = 0x1FF8
        self.CYAN = 0xFF07
        
        self.width = 480
        self.height = 160
        self._scroll = 0
        
        self.cs = Pin(LCD_CS,Pin.OUT)
        self.rst = Pin(LCD_RST,Pin.OUT)
        self.dc = Pin(LCD_DC,Pin.OUT)        
        self.tp_cs =Pin(TP_CS,Pin.OUT)
        self.irq = Pin(TP_IRQ,Pin.IN)
        self.temp = bytearray(1)
        self.temp1 = bytearray(1)
        h2=1                   #154 set to framebuffer height
        self.cs(1)
        self.dc(1)
        self.rst(1)
        self.tp_cs(1)
        self.spi = SPI(1,22_500_000,sck=Pin(LCD_SCK),mosi=Pin(LCD_MOSI),miso=Pin(LCD_MISO))
        #print(self.spi) # 62,500,000
        gc.collect()     
        self.buffer = bytearray(h2 * self.width * 2)
        super().__init__(self.buffer, self.width, h2, framebuf.RGB565)
        self.init_display()
        self.color_map = bytearray(b'\x00\x00\xFF\xFF')
        self.mem_buffer = bytearray(mem*2)# MEMORY_BUFFER * 2)
        self.mv_buffer = bytearray(mem*2)#MEMORY_BUFFER * 2)
        self.temp_color = bytearray(2)
        
    def _write_cmd(self, cmd):
        write_cmd_asm(cmd)
        self.cs(1)

    def _write_data(self, buf):
        write_data_asm(buf)
        self.cs(1)

    def write_cmd(self, cmd):
        self.temp[0] = cmd
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(self.temp)
        self.cs(1)

    def write_data(self, buf):
        self.temp[0] = buf
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.temp)
        self.cs(1)


    def init_display(self):
        """Initialize dispaly"""  
        self.rst(1)
        sleep_ms(5)
        self.rst(0)
        sleep_ms(10)
        self.rst(1)
        sleep_ms(5)
        self.write_cmd(0x21)
        self.write_cmd(0xC2)
        self.write_data(0x33)
        self.write_cmd(0XC5)
        self.write_data(0x00)
        self.write_data(0x1e)
        self.write_data(0x80)
        self.write_cmd(0xB1)
        self.write_data(0xB0)
        self.write_cmd(0x36)
        self.write_data(0x28)
        self.write_cmd(0XE0)
        self.write_data(0x00)
        self.write_data(0x13)
        self.write_data(0x18)
        self.write_data(0x04)
        self.write_data(0x0F)
        self.write_data(0x06)
        self.write_data(0x3a)
        self.write_data(0x56)
        self.write_data(0x4d)
        self.write_data(0x03)
        self.write_data(0x0a)
        self.write_data(0x06)
        self.write_data(0x30)
        self.write_data(0x3e)
        self.write_data(0x0f)
        self.write_cmd(0XE1)
        self.write_data(0x00)
        self.write_data(0x13)
        self.write_data(0x18)
        self.write_data(0x01)
        self.write_data(0x11)
        self.write_data(0x06)
        self.write_data(0x38)
        self.write_data(0x34)
        self.write_data(0x4d)
        self.write_data(0x06)
        self.write_data(0x0d)
        self.write_data(0x0b)
        self.write_data(0x31)
        self.write_data(0x37)
        self.write_data(0x0f)
        self.write_cmd(0X3A)
        self.write_data(0x55)
        self.write_cmd(0x11)
        sleep_ms(120)
        self.write_cmd(0x29)
        
        self.write_cmd(0xB6)
        self.write_data(0x00)
        self.write_data(0x62)
        
        self.write_cmd(0x36)
        self.write_data(0x28) #28
    def show_up(self):
        self.write_cmd(0x2A)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x01)
        self.write_data(0xdf)
        
        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x9f)
        
        self.write_cmd(0x2C)
        
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)
    def show_down(self):
        self.write_cmd(0x2A)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x01)
        self.write_data(0xdf) # 479 width
        
        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(0xA0) # 160 start height
        self.write_data(0x01)
        self.write_data(0x3f) # 319 end height
        
        self.write_cmd(0x2C)
        
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)
    def bl_ctrl(self,duty):
        pwm = PWM(Pin(LCD_BL))
        pwm.freq(1000)
        if(duty>=100):
            pwm.duty_u16(65535)
        else:
            pwm.duty_u16(655*duty)
    def draw_point(self,x,y,color,size=1):
        self.write_cmd(0x2A)

        
        self.write_data((x-2)>>8)
        self.write_data((x-2)&0xff)
        self.write_data(x>>8)
        self.write_data(x&0xff)
        
        self.write_cmd(0x2B)
        self.write_data((y-2)>>8)
        self.write_data((y-2)&0xff)
        self.write_data(y>>8)
        self.write_data(y&0xff)
        
        self.write_cmd(0x2C)
        
        self.cs(1)
        self.dc(1)
        self.cs(0)
        for i in range(0,size): # 9
            self.temp[0] =  color&0xff
            self.spi.write(self.temp)
            self.temp[0] =  color>>8
            self.spi.write(self.temp)
        self.cs(1)

    def draw_line(self, x0, y0, x1, y1, color, width=1):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        for i in range(width):
            x = x0
            y = y0 + i
            while True:
                self.draw_point(x, y, color)
                if x == x1 and y == y1+i:
                    break
                e2 = 2 * err
                if e2 > -dy:
                    err -= dy
                    x += sx
                if e2 < dx:
                    err += dx
                    y += sy


    def touch_get(self,both=False):
        if self.irq() == 0:
            self.spi = SPI(1,5_000_000,sck=Pin(LCD_SCK),mosi=Pin(LCD_MOSI),miso=Pin(LCD_MISO))            
            self.tp_cs(0)
            X_Point = 0
            Y_Point = 0
            for i in range(0,3):
                self.temp1[0]=0xd0
                self.spi.write(self.temp1)
                self.Read_data = self.temp_color
                self.spi.readinto(self.Read_data)
                sleep_us(10)
                X_Point=X_Point+(((self.Read_data[0]<<8)+self.Read_data[1])>>3)
                self.temp1[0]=0x90
                self.spi.write(self.temp1)
                self.Read_data = self.temp_color
                self.spi.readinto(self.Read_data)
                Y_Point=Y_Point+(((self.Read_data[0]<<8)+self.Read_data[1])>>3)
            X_Point=X_Point//3
            Y_Point=Y_Point//3
            self.tp_cs(1) 
            self.spi = SPI(1,60_000_000,sck=Pin(LCD_SCK),mosi=Pin(LCD_MOSI),miso=Pin(LCD_MISO))
            if both:
                return [X_Point,Y_Point]
            return X_Point
        
    def show_xy(self,x1,y1,x2,y2,buffer):
        self.write_cmd(0x2A)
        self.write_data(x1 >>8 )
        self.write_data(x1 & 0x00ff)
        self.write_data(x2 >>8 )
        self.write_data(x2 & 0x00ff)   # 479 width        
        self.write_cmd(0x2B)
        self.write_data(y1 >> 8)
        self.write_data(y1 & 0x00ff) # 160 start height
        self.write_data(y2 >> 8)
        self.write_data(y2 & 0x00ff) # 319 end height
        self.write_cmd(0x2C) 
        self.cs(1)
        self.dc(1)
        self.cs(0)
        #gticks=ticks_us()
        self.spi.write(buffer)
        #delta = ticks_diff(ticks_us(), gticks) #35056 240x240,  6100 100x100  or .305us per byte   
        #print(delta)
        self.cs(1)
        return
        
    def WriteDevice(self, command, data=None):
        self.temp[0] = command
        self.dc(0)
        self.cs(0)
        self.spi.write(self.temp) #(bytearray([command]))
        self.cs(1)
        if data is not None:
            self.WriteDataToDevice(data)
            
    @micropython.native        
    def WriteDataToDevice(self, data):
        self.dc(1);self.cs(0);self.spi.write(data);self.cs(1)


    def WriteBlock(self, x0, y0, x1, y1, data=None):
        self.WriteDevice(COLUMN_ADDRESS_SET,None)
        self.write_data(x0 >> 8 )
        self.write_data(x0 & 0x00ff)
        self.write_data(x1 >> 8 )
        self.write_data(x1 & 0x00ff)   # 479 width
        self.WriteDevice(PAGE_ADDRESS_SET,None)
        self.write_data(y0 >> 8)
        self.write_data(y0 & 0x00ff) # 160 start height
        self.write_data(y1 >> 8)
        self.write_data(y1 & 0x00ff) # 319 end height
        self.WriteDevice(RAM_WRITE, data)

    def Vline(self,x,y,h,color):
        self.FillRectangle(x, y, 1, h, color)
        
    def Fill(self,color):
        self.FillRectangle(0, 0, 479, 319, color)

    @micropython.native
    def FillRectangle(self, x, y, w, h, color=None): #:, buffer=None):        
        x = min(self.width - 1, max(0, x));y = min(320 - 1, max(0, y))
        w = min(self.width - x, max(1, w));h = min(320 - y, max(1, h))        
        if color:
            self.temp_color[0] = color & 0x00ff
            self.temp_color[1] = color >> 8 
        else:
            self.temp_color[0] = 0
            self.temp_color[1] = 0
        fill_b_array(self.mem_buffer,MEMORY_BUFFER,self.temp_color[0],self.temp_color[1])
            #for i in range(MEMORY_BUFFER):
            #    self.mem_buffer[2*i]=self.temp_color[0]; self.mem_buffer[2*i+1]=self.temp_color[1]
        
        chunks = w * h // MEMORY_BUFFER
        rest = w * h % MEMORY_BUFFER
    
        self.WriteBlock(x, y, x + w - 1, y + h - 1, None)
        if chunks:
            for count in range(chunks):
                self.WriteDataToDevice(self.mem_buffer)
        if rest != 0:
            self.mv_buffer = self.mem_buffer
            self.WriteDataToDevice(self.mv_buffer)
                    
    def scroll(self, dy, r=None):        
        self._scroll = (self._scroll + dy) % self.width
        if r:
            self._scroll = 0 
        self.write_cmd(0x37)
        self.write_data(self._scroll>>8)
        self.write_data(self._scroll)
        

@micropython.asm_thumb
def fill_b_array(r0,r1,r2,r3): # r0=address, r1= # of words, r2,r3=data
    label(LOOP)
    strb(r2, [r0, 0]) # 
    strb(r3, [r0, 1]) #
    add(r0, 2)  # add 2 to address (next word)
    sub(r1, 1)  # dec number of words
    bgt(LOOP)   # branch if not done
    
# SPI1_BASE = 0x40040000
# SSPCR1 = 0x004 # offset , bit 1 to enable
# SSPDR  = 0x008 # Tx FIFO
# SSPSR  = 0x00c # status register, bit 1=0 is FIFO full


@micropython.asm_thumb
def peek_asm(r0):
    ldr(r0,[r0,0])
    

@micropython.asm_thumb
def write_cmd_asm(r0):
    align(4)
    mov(r1,pc)
    b(LOAD_REGS)
    data(2,0x0000,0x4004,0x4000,0x4001,0,0xd000)
    align(4)
    label(LOAD_REGS)
    ldr(r7,[r1,8])    # r7 = SIO_START  = 0xD0000000
    ldr(r2,[r1,4])    # r2 = GPIO_START = 0x40014000
    ldr(r1,[r1,0])    # r1 = SPI1_BASE  = 0x40040000  
    bl(CS_HIGH)
    bl(DC_LOW)
    bl(CS_LOW)  
    str(r0,[r1,0x8])  # write data to FIFO
    mov(r3,0b10)       
    str(r3,[r1,0x4])  # enable
    label(SPI_WAIT)
    ldr(r3,[r1,0xc])  # get FIFO status
    mov(r4,0b10)      # is it full?
    and_(r3,r4)
    cmp(r3,r4)
    bne(SPI_WAIT)
    #bl(CS_HIGH)
    b(EXIT)
    
    # --------SUBS-----------
    label(CS_HIGH)
    mov(r4,1)
    lsl(r4,r4,9)       # pin 9
    str(r4,[r7,0x14])  # GPIO_OUT_SET Register
    bx(lr)
    
    label(CS_LOW)
    #mov(r4,5)
    #str(r4,[r2,0x4c])  # CS = GPIO 9 = 0x4c    
    mov(r3,1)          
    lsl(r3,r3,31)      
    sub(r3,1)          # all pins!
    mov(r4,1)
    lsl(r4,r4,9)       # pin 9
    str(r4,[r7,0x18])  # GPIO_OE_CLR Register
    #str(r3,[r7,0x20])  # GPIO_OE Register (enable)
    bx(lr)

    label(DC_HIGH)
    mov(r4,1)
    lsl(r4,r4,8)       # pin 8
    str(r4,[r7,0x14])  # GPIO_OUT_SET Register
    bx(lr)    

    label(DC_LOW)
    mov(r4,1)
    lsl(r4,r4,8)       # pin 8
    str(r4,[r7,0x18])  # GPIO_OE_CLR Register
    bx(lr)
    
    label(DELAY_PINS)
    mov(r3,255)
    lsl(r3,r3,9)
    label(DELAY_LOOP)
    sub(r3,1)
    bne(DELAY_LOOP)
    
    label(EXIT)
    

@micropython.asm_thumb
def write_data_asm(r0):
    align(4)
    mov(r1,pc)
    b(LOAD_REGS)
    data(2,0x0000,0x4004,0x4000,0x4001,0,0xd000)
    align(4)
    label(LOAD_REGS)
    ldr(r7,[r1,8])    # r7 = SIO_START  = 0xD0000000
    ldr(r2,[r1,4])    # r2 = GPIO_START = 0x40014000
    ldr(r1,[r1,0])    # r1 = SPI1_BASE  = 0x40040000  
    bl(CS_HIGH)
    bl(DC_HIGH)
    bl(CS_LOW)  
    str(r0,[r1,0x8])  # write data to FIFO
    mov(r3,0b10)       
    str(r3,[r1,0x4])  # enable
    label(SPI_WAIT)
    ldr(r3,[r1,0xc])  # get FIFO status
    mov(r4,0b10)      # is it full?
    and_(r3,r4)
    cmp(r3,r4)
    bne(SPI_WAIT)
    
    #bl(DELAY_PINS)
    #bl(CS_HIGH)
    #bl(DELAY_PINS)
    b(EXIT)
    
    # --------SUBS-----------
    label(CS_HIGH)
    mov(r4,1)
    lsl(r4,r4,9)       # pin 9
    str(r4,[r7,0x14])  # GPIO_OUT_SET Register
    bx(lr)
    
    label(CS_LOW)
    #mov(r4,5)
    #str(r4,[r2,0x4c])  # CS = GPIO 9 = 0x4c    
    mov(r3,1)          
    lsl(r3,r3,31)      
    sub(r3,1)          # all pins!
    mov(r4,1)
    lsl(r4,r4,9)       # pin 9
    str(r4,[r7,0x18])  # GPIO_OE_CLR Register
    #str(r3,[r7,0x20])  # GPIO_OE Register (enable)
    bx(lr)

    label(DC_HIGH)
    mov(r4,1)
    lsl(r4,r4,8)       # pin 8
    str(r4,[r7,0x14])  # GPIO_OUT_SET Register
    bx(lr)    

    label(DC_LOW)
    mov(r4,1)
    lsl(r4,r4,8)       # pin 8
    str(r4,[r7,0x18])  # GPIO_OE_CLR Register
    bx(lr)
    
    label(DELAY_PINS)
    mov(r3,255)
    lsl(r3,r3,9)
    label(DELAY_LOOP)
    sub(r3,1)
    bne(DELAY_LOOP)
    
    label(EXIT)

#print(hex(write_asm(1)))
#exit()

                
if __name__=='__main__':
    freq(230_000_000)
    LCD = LCD_3inch5()
    print(LCD.spi)
    machine.mem32[0x40008048] = 1<<11 # enable peri_ctrl clock
    LCD.bl_ctrl(100)
    #LCD.fill(LCD.RED)
    buf=bytearray(480*80*2)
    screen=framebuf.FrameBuffer(buf, 480, 80, framebuf.RGB565)
    screen.fill(randint(0,0xffff))
    gticks=ticks_us()
    LCD.show_xy(0,0,479,79,screen)
    LCD.show_xy(0,80,479,159,screen)
    LCD.show_xy(0,160,479,239,screen)
    LCD.show_xy(0,240,479,319,screen)
    print(1_000_000//ticks_diff(ticks_us(),gticks))
    ymax=159
    max_x = 479
    i=ymax*10000 //max_x
    #LCD.FillRectangle(0,0,480,320,LCD.BLACK)
    step = 20
    colors=[LCD.RED,LCD.YELLOW,LCD.ORANGE,LCD.GREEN,LCD.BLUE]
    print('mem free:',gc.mem_free())
 
    while(0):
        gticks=ticks_us()
        for k in range(0,step):
            x=k
            while x<max_x:
            #for x in range(k,max_x,step):
                j=(x*i)//10000
                LCD.line(x,0,max_x,j,LCD.WHITE)
                LCD.line(max_x,j,max_x-x,ymax,LCD.WHITE)
                LCD.line(max_x-x,ymax,0,ymax-j,LCD.WHITE)
                LCD.line(0,ymax-j,x,0,LCD.WHITE)
                x+=step
            LCD.show_up()
            LCD.show_down()
            LCD.fill(LCD.BLACK)
        #print(gc.mem_free())
        delta = ticks_diff(ticks_us(), gticks)
        #print(delta/1000000)
    while(1):
        gticks=ticks_us()
        for i in range(50): #50
            LCD.FillRectangle(randint(0,470),randint(0,310),20,10,colors[randint(0,4)])
            #LCD.FillRectangle(randint(0,470),randint(0,310),20,10,randint(0,65535))
        #print(ticks_diff(ticks_us(), gticks))
        for i in range(1):
            LCD.scroll(1)
            #sleep_ms(10)


