import pygame
from pygame.locals import *
import random

# Khởi tạo Pygame
pygame.init()

# Hàm vẽ văn bản lên màn hình
def draw_text(text, font, color, x, y):
    screen_text = font.render(text, True, color)  # Tạo bề mặt văn bản
    screen.blit(screen_text, [x, y])  # Vẽ văn bản lên màn hình

# Khởi tạo đồng hồ và thiết lập tốc độ khung hình
clock = pygame.time.Clock()
fps = 60

# Kích thước màn hình
screen_width = 864
screen_height = 936

# Tạo cửa sổ trò chơi
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')  # Tiêu đề cửa sổ

# Định nghĩa font chữ
font = pygame.font.SysFont('Bauhaus 93', 60)

# Định nghĩa màu sắc
white = (255, 255, 255)

# Định nghĩa các biến trò chơi
ground_scroll = 0  # Biến cuộn nền
scroll_speed = 4  # Tốc độ cuộn
flying = False  # Trạng thái bay
game_over = False  # Trạng thái kết thúc trò chơi
pipe_gap = 150  # Khoảng cách giữa các ống
pipe_frequency = 1500  # Tần suất tạo ống (milliseconds)
last_pipe = pygame.time.get_ticks() - pipe_frequency  # Thời gian ống cuối cùng được tạo
score = 0  # Điểm số
pass_pipe = False  # Biến kiểm tra ống đã qua

# Tải hình ảnh
bg = pygame.image.load('img/bg.png')  # Hình nền
ground_img = pygame.image.load('img/ground.png')  # Hình ảnh mặt đất
button_img = pygame.image.load('img/restart.png')  # Hình nút khởi động lại

# Hàm reset trò chơi
def reset_game():
    pipe_group.empty()  # Xóa tất cả các ống
    flappy.rect.x = 100  # Đặt vị trí chim
    flappy.rect.y = int(screen_height / 2)
    score = 0  # Đặt điểm về 0
    return score  # Trả về điểm số

# Định nghĩa lớp Bird (chim)
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)  # Khởi tạo lớp cha
        self.images = []  # Danh sách lưu trữ hình ảnh
        self.index = 0  # Chỉ số hình ảnh hiện tại
        self.counter = 0  # Bộ đếm khung hình

        # Tải hình ảnh chim
        for num in range(1, 4):
            img = pygame.image.load(f"img/bird{num}.png")
            self.images.append(img)

        self.image = self.images[self.index]  # Hình ảnh hiện tại
        self.rect = self.image.get_rect()  # Khung hình của chim
        self.rect.center = [x, y]  # Đặt vị trí chim
        self.vel = 0  # Tốc độ rơi
        self.clicked = False  # Trạng thái nhấp chuột

    def update(self):
        if flying:  # Nếu đang bay
            self.vel += 0.5  # Áp dụng trọng lực
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:  # Giới hạn vị trí chim
                self.rect.y += int(self.vel)

        if not game_over:  # Nếu chưa kết thúc trò chơi
            # Kiểm tra nhấp chuột để nhảy
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                self.vel = -10  # Tạo lực nhảy
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            # Xử lý hoạt hình
            flap_cooldown = 5  # Thời gian giữa các lần flap
            self.counter += 1
            
            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
                self.image = self.images[self.index]  # Cập nhật hình ảnh

            # Xoay chim
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)  # Xoay chim xuống khi game over

# Định nghĩa lớp Pipe (ống)
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)  # Khởi tạo lớp cha
        self.image = pygame.image.load("img/pipe.png")  # Tải hình ảnh ống
        self.rect = self.image.get_rect()  # Khung hình của ống
        
        # Đặt vị trí ống
        if position == 1:  # Nếu là ống trên
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        elif position == -1:  # Nếu là ống dưới
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed  # Di chuyển ống sang trái
        if self.rect.right < 0:  # Nếu ống ra ngoài màn hình
            self.kill()  # Xóa ống

# Định nghĩa lớp Button (nút)
class Button():
    def __init__(self, x, y, image):
        self.image = image  # Hình ảnh nút
        self.rect = self.image.get_rect()  # Khung hình của nút
        self.rect.topleft = (x, y)  # Đặt vị trí nút

    def draw(self, score):
        action = False

        # Lấy vị trí chuột
        pos = pygame.mouse.get_pos()

        # Kiểm tra nếu chuột đang di chuyển qua nút và nhấn
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True  # Nếu nhấn nút
		
        # Vẽ nút lên màn hình
        screen.blit(self.image, (self.rect.x, self.rect.y))
        
        # Vẽ số điểm lên nút
        draw_text('Your score: ' + str(score), font_pixel, (0, 0, 0), button.rect.x + 20, button.rect.y + button.rect.height + 10)

        return action  # Trả về hành động (nếu nút được nhấn)

font_large = pygame.font.Font('PressStart2P-Regular.ttf', 150)  # Đặt kích thước là 80


# Định nghĩa font chữ pixel
font_pixel = pygame.font.Font('PressStart2P-Regular.ttf')

# Tạo các nhóm sprite
pipe_group = pygame.sprite.Group()
bird_group = pygame.sprite.Group()

# Tạo đối tượng chim
flappy = Bird(100, int(screen_height / 2))
bird_group.add(flappy)

# Tạo nút khởi động lại
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)

# Vòng lặp chính của trò chơi
run = True
while run:
    clock.tick(fps)  # Giới hạn FPS

    # Vẽ nền
    screen.blit(bg, (0, 0))

    pipe_group.draw(screen)  # Vẽ các ống
    bird_group.draw(screen)  # Vẽ chim
    bird_group.update()  # Cập nhật trạng thái chim

    # Vẽ và cuộn nền
    screen.blit(ground_img, (ground_scroll, 768))

    # Hiển thị điểm số ở góc trên bên trái khi trò chơi đang diễn ra
    if flying and not game_over:  # Chỉ hiển thị khi đang bay và chưa kết thúc
        draw_text('Score: ' + str(score), font_pixel, (0, 0, 0), 20, 100)

    # Kiểm tra điểm số
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left and \
           bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right and \
           not pass_pipe:
            pass_pipe = True
        if pass_pipe:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1  # Tăng điểm số
                pass_pipe = False

    # Kiểm tra va chạm
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True  # Nếu va chạm hoặc chim rơi ra ngoài

    # Nếu chim chạm đất
    if flappy.rect.bottom >= 768:
        game_over = True
        flying = False  # Dừng bay

    if flying and not game_over:  # Nếu đang bay và chưa kết thúc trò chơi
        # Tạo ống mới
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)  # Thêm ống dưới
            pipe_group.add(top_pipe)  # Thêm ống trên
            last_pipe = time_now  # Cập nhật thời gian tạo ống

        pipe_group.update()  # Cập nhật trạng thái các ống

        ground_scroll -= scroll_speed  # Cuộn mặt đất
        if abs(ground_scroll) > 35:  # Nếu mặt đất đã cuộn quá xa
            ground_scroll = 0  # Đặt lại vị trí

    # Kiểm tra kết thúc trò chơi và reset
    if game_over:
        if button.draw(score):  # Nếu nút được nhấn
            game_over = False  # Reset trạng thái game over
            score = reset_game()  # Reset trò chơi

    # Xử lý sự kiện
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Nếu người dùng đóng cửa sổ
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and not flying and not game_over:  # Nếu nhấn chuột và trò chơi chưa bắt đầu
            flying = True  # Bắt đầu trò chơi

    pygame.display.update()  # Cập nhật màn hình

pygame.quit()  # Thoát Pygame