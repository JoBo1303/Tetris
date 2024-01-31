from machine import Pin, SPI
import framebuf
from time import sleep_ms
from random import randint
from LCD_3inch5 import LCD_3inch5

LCD = LCD_3inch5()
LCD.Fill(LCD.WHITE)
# Tetris block colors
COLORS = [LCD.RED, LCD.YELLOW, LCD.ORANGE, LCD.GREEN, LCD.BLUE,LCD.CYAN, LCD.MAGENTA]
C = [LCD.WHITE,LCD.BLACK]
nums =[0,1,1,1,1,1,1,  # 0 # One row per digit 
       0,1,1,0,0,0,0,  # 1
       1,1,0,1,1,0,1,  # 2
       1,1,1,1,0,0,1,  # 3
       1,1,1,0,0,1,0,  # 4
       1,0,1,1,0,1,1,  # 5
       1,0,1,1,1,1,1,  # 6
       0,1,1,0,0,0,1,  # 7
       1,1,1,1,1,1,1,  # 8
       1,1,1,0,0,1,1,  # 9
       1,1,1,1,1,0,1,  # a = 10 - HEX characters
       0,0,1,1,1,1,1,  # b = 11
       0,0,0,1,1,0,1,  # c = 12
       0,1,1,1,1,0,1,  # d = 13
       1,1,0,1,1,1,1,  # e = 14
       1,0,0,0,1,1,1,  # f = 15
       1,1,1,1,0,1,1,  # g needed for seg!
       0,0,0,0,0,0,1,  # -
       0,0,0,0,0,0,0]  # Blank

# Tetris block shapes (represented as lists of coordinates)
SHAPES = [
    [(0, 0), (1, 0), (2, 0), (3, 0)],  # I-block
    [(0, 0), (1, 0), (2, 0), (2, 1)],  # L-block
    [(0, 0), (1, 0), (2, 0), (0, 1)],  # J-block
    [(0, 0), (1, 0), (1, 1), (2, 1)],  # Z-block
    [(1, 0), (2, 0), (0, 1), (1, 1)],  # S-block
    [(0, 1), (1, 0), (1, 1), (1, 2)],  # T-block
    [(0, 0), (1, 0), (0, 1), (1, 1)]   # O-block
]

class TetrisGame:
    def __init__(self, lcd):
        self.lcd = lcd
        LCD.Fill(LCD.WHITE)
        self.board = [[0] * 20 for _ in range(10)]  # 16 rows, 10 columns
        self.current_block = self.generate_block()
        self.game_over = False
        self.score = 0
        self.speed = 500
        self.time_c = 0
        self.draw_board()
        self.show_score()
        
    def draw_board(self):
        for x in range(20):
            for y in range(10):
                self.lcd.FillRectangle(x * 20, y * 20,20,20, lcd.BLACK)
                self.lcd.FillRectangle(x * 20+1, y * 20+1,18,18, lcd.GRAY)
                
        for x in range(4):
            lcd.FillRectangle(400,x*80,80,80,lcd.BLACK)
            lcd.FillRectangle(402,x*80+2,76,76,lcd.RED)
        
        lcd.FillRectangle(437,20,6,40,lcd.BLACK)
        lcd.draw_line(442,18,430,30, lcd.BLACK, width=6)
        lcd.draw_line(442,18,452,30, lcd.BLACK, width=6)
        
        lcd.FillRectangle(437,260,6,40,lcd.BLACK)
        lcd.draw_line(442,302,430,290, lcd.BLACK, width=6)
        lcd.draw_line(442,302,452,290, lcd.BLACK, width=6)
        
        lcd.FillRectangle(437,100,6,40, lcd.BLACK)
        lcd.FillRectangle(437,100,25,6, lcd.BLACK)
        lcd.draw_line(465,102,453,92, lcd.BLACK, width=6)
        lcd.draw_line(465,102,453,112, lcd.BLACK, width=6)
        
        lcd.FillRectangle(437,180,6,40, lcd.BLACK)
        lcd.FillRectangle(415,214,25,6, lcd.BLACK)
        lcd.draw_line(415,216,425,206, lcd.BLACK, width=6)
        lcd.draw_line(415,216,425,226, lcd.BLACK, width=6)
        
    def draw_over(self):
        lcd.FillRectangle(100,50,200,220, lcd.BLACK)
        lcd.FillRectangle(102,52,196,216, lcd.WHITE)
        #G
        lcd.FillRectangle(110,215,5,40, lcd.BLACK)
        lcd.FillRectangle(110,250,80,5, lcd.BLACK)
        lcd.FillRectangle(185,215,5,40, lcd.BLACK)
        lcd.FillRectangle(150,215,40,5, lcd.BLACK)
        lcd.FillRectangle(150,215,5,20, lcd.BLACK)
        #A
        lcd.FillRectangle(150,173,5,24, lcd.BLACK)
        lcd.draw_line(110,185,190,165, lcd.BLACK, width=5)
        lcd.draw_line(110,185,190,205, lcd.BLACK, width=5)
        #M
        lcd.FillRectangle(110,115,80,5, lcd.BLACK)
        lcd.FillRectangle(110,150,80,5, lcd.BLACK)
        lcd.draw_line(113,118,150,135, lcd.BLACK, width=5)
        lcd.draw_line(113,152,150,135, lcd.BLACK, width=5)
        #E
        lcd.FillRectangle(110,100,80,5, lcd.BLACK)
        lcd.FillRectangle(110,65,5,40, lcd.BLACK)
        lcd.FillRectangle(153,75,5,30, lcd.BLACK)
        lcd.FillRectangle(185,65,5,40, lcd.BLACK)
        #O
        lcd.FillRectangle(210,215,80,40, lcd.BLACK)
        lcd.FillRectangle(215,220,70,30, lcd.WHITE)
        #V
        lcd.draw_line(290,185,210,165, lcd.BLACK, width=5)
        lcd.draw_line(290,185,210,205, lcd.BLACK, width=5)
        #E
        lcd.FillRectangle(210,150,80,5, lcd.BLACK)
        lcd.FillRectangle(210,115,5,40, lcd.BLACK)
        lcd.FillRectangle(253,125,5,30, lcd.BLACK)
        lcd.FillRectangle(285,115,5,40, lcd.BLACK)
        #R
        lcd.FillRectangle(210,65,5,40, lcd.BLACK)
        lcd.FillRectangle(210,65,40,5, lcd.BLACK)
        lcd.FillRectangle(210,100,80,5, lcd.BLACK)
        lcd.FillRectangle(250,65,5,40, lcd.BLACK)
        lcd.draw_line(250,100,290,65, lcd.BLACK, width=5)
        
    def seg(self,xx,yy,n,f): #,bg,fg):
        global C
        # (x, y, number, size-factor, background, foreground)
        
        #c = [bg,fg]
        p = n * 7        
        LCD.FillRectangle(xx+0*f,yy+1*f,1*f,3*f,C[nums[p+6]])
        LCD.FillRectangle(xx+1*f,yy+4*f,3*f,1*f,C[nums[p+5]])
        LCD.FillRectangle(xx+5*f,yy+4*f,3*f,1*f,C[nums[p+4]])
        LCD.FillRectangle(xx+8*f,yy+1*f,1*f,3*f,C[nums[p+3]])
        LCD.FillRectangle(xx+5*f,yy+0*f,3*f,1*f,C[nums[p+2]])
        LCD.FillRectangle(xx+1*f,yy+0*f,3*f,1*f,C[nums[p+1]])
        LCD.FillRectangle(xx+4*f,yy+1*f,1*f,3*f,C[nums[p]])
        
    def show_score(self):
        num = self.score
        self.speed = 500 - ((self.score // 100)*100//2)
        #num = 123
        places = 0
        if num==0:
            self.seg(20,210,0,5) #,LCD.BLACK,LCD.WHITE)
        if num > 999:
            num = 999
        while num>0:
            digit = num % 10
            ypos = 210 + places
            #draw_object2(score_list[digit],False)
            self.seg(20,ypos,digit,5) #,LCD.BLACK,LCD.WHITE)
            num //= 10
            places += 30
        
    def generate_block(self):
        shape = SHAPES[randint(0, len(SHAPES) - 1)]
        color = COLORS[randint(0, len(COLORS) - 1)]
        return {'shape': shape, 'color': color, 'position': [0, 4]}

    def draw_block(self, block):
        for x, y in block['shape']:
            px, py = block['position']
            self.lcd.FillRectangle((px + x) * 20, (py + y) * 20,20,20, block['color'])

    def erase_block(self, block):
        for x, y in block['shape']:
            px, py = block['position']
            self.lcd.FillRectangle((px + x) * 20, (py + y) * 20,20,20, LCD.BLACK)
            self.lcd.FillRectangle((px + x) * 20+1, (py + y) * 20+1,18,18, LCD.GRAY)

    def move_block(self, dx, dy):
        px, py = self.current_block['position']
        new_position = [px + dx, py + dy]

        if self.is_valid_position(new_position, self.current_block['shape']):
            self.erase_block(self.current_block)
            self.current_block['position'] = new_position
            self.draw_block(self.current_block)
        else:
            if dx != 0:  # Check for game over when moving vertically
                self.check_game_over()
                self.place_block()

    def rotate_block(self):
        rotated_shape = [(y, -x) for x, y in self.current_block['shape']]
        px, py = self.current_block['position']
        new_position = [px, py]

        if self.is_valid_position(new_position, rotated_shape):
            self.erase_block(self.current_block)
            self.current_block['shape'] = rotated_shape
            self.draw_block(self.current_block)
            
    def rotate_block_r(self):
        rotated_shape = [(-y, x) for x, y in self.current_block['shape']]
        px, py = self.current_block['position']
        new_position = [px, py]

        if self.is_valid_position(new_position, rotated_shape):
            self.erase_block(self.current_block)
            self.current_block['shape'] = rotated_shape
            self.draw_block(self.current_block)

    def is_valid_position(self, position, shape):
        for x, y in shape:
            px, py = position
            if not (0 <= px + x < 20 and 0 <= py + y < 10 and self.board[py + y][px + x] == 0):
                return False
        return True

    def check_game_over(self):
        px, py = self.current_block['position']
        shape = self.current_block['shape']

        for x, y in shape:
            if px + x < 0:
                print("ENDE")
                self.game_over = True
                
    def place_block(self):
        px, py = self.current_block['position']
        shape = self.current_block['shape']
        color = self.current_block['color']

        for x, y in shape:
            self.board[py + y][px + x] = color
        
        self.score += 1
        self.show_score()
        self.clear_lines()
        #print(self.board[0][19])
        self.current_block = self.next_block
        self.draw_next_block()
        self.draw_block(self.current_block)
        if not self.is_valid_position(self.current_block['position'], self.current_block['shape']):
            # If the new block can't be placed, game over
            self.game_over = True
            
    def clear_lines(self):
        full_line = False
        for x in range(20):
            full_line = all(row[x] != 0 for row in self.board)
            if full_line:
                self.score += 10
                self.show_score()
                for n in range(x):
                    for row in self.board:
                        row[x-n]=row[x-1-n]
                for e in range(x+1):
                    for y in range(10):
                        self.lcd.FillRectangle(e * 20, y * 20,20,20, lcd.BLACK)
                        self.lcd.FillRectangle(e * 20+1, y * 20+1,18,18, lcd.GRAY)
                for x_fill in range(x+1):
                    for y_fill in range(10):
                        if self.board[y_fill][x_fill] != 0:
                            self.lcd.FillRectangle(x_fill * 20, y_fill * 20,20,20, self.board[y_fill][x_fill])
                            
    def draw_next_block(self):
        self.next_block = self.generate_block()
        next_block_shape = self.next_block['shape']
        next_block_color = self.next_block['color']
        next_block_position = [10, 0]  # Adjust the position as needed
        self.lcd.FillRectangle(190,210,100,100,lcd.WHITE)
        
        for x, y in next_block_shape:
            nx, ny = next_block_position
            self.lcd.FillRectangle((nx+x) * 20, (ny+y + 12) * 20, 20, 20, next_block_color)


    def update(self):
        if not self.game_over:
            if self.time_c >= self.speed:
                self.time_c = 0
                self.move_block(1, 0)

# Initialize LCD
lcd = LCD_3inch5()
lcd.bl_ctrl(100)

# Initialize Tetris game
tetris_game = TetrisGame(lcd)

# Draw the initial next block
tetris_game.draw_next_block()

# Game loop
while True:
    if tetris_game.game_over:
        # Game over, wait for input to restart
        lcd.FillRectangle(400, 0, 80, 320, LCD.WHITE)
        tetris_game.draw_over()
        
        while True:
            get = lcd.touch_get(True)
            if get is not None:
                break

    # Initialize Tetris game if it's a new game or a restart
        tetris_game = TetrisGame(lcd)
        tetris_game.draw_next_block()

    get = lcd.touch_get(True)
    if get is not None:
        X_Point = int((get[1] - 430) * 480 / 3270)
        Y_Point = 320 - int((get[0] - 430) * 320 / 3270)
        if X_Point > 400:
            print(Y_Point)
            if Y_Point < 90:
                tetris_game.move_block(0, -1)
            elif Y_Point < 160 and Y_Point > 100:
                tetris_game.rotate_block()
            elif Y_Point < 240:
                tetris_game.rotate_block_r()
            elif Y_Point >= 240:
                tetris_game.move_block(0, 1)

    tetris_game.update()
    sleep_ms(100)
    tetris_game.time_c += 100

    #sleep_ms(tetris_game.speed)  # Adjust the speed of the game
