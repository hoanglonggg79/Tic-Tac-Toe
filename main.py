import pygame, sys, os, random, math, json
from math import inf
from datetime import datetime

# --- CẤU HÌNH MÔI TRƯỜNG (Fix lỗi gõ tiếng Việt trên Linux/IBUS) ---
os.environ['SDL_IM_MODULE'] = 'ibus' 

# Khởi tạo Pygame
pygame.init()
pygame.mixer.init()

# --- Định nghĩa BASE_DIR để tương thích PyInstaller/Standalone ---
BASE_DIR = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
def path(*relative):
    return os.path.join(BASE_DIR, "assets", *relative)

# ==============================================================================
# 0. CLASS PARTICLE: Hiệu ứng pháo hoa
# ==============================================================================
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 6.28)
        speed = random.uniform(2, 6)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.radius = random.randint(3, 6)
        self.life = 1.0 # 100% life
        self.decay = random.uniform(0.01, 0.03)
        self.gravity = 0.1

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= self.decay
        self.radius = max(0, self.radius - 0.05)

    def draw(self, screen):
        if self.life > 0 and self.radius > 0:
            alpha = int(self.life * 255)
            s = pygame.Surface((int(self.radius*2), int(self.radius*2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (int(self.radius), int(self.radius)), int(self.radius))
            screen.blit(s, (int(self.x) - self.radius, int(self.y) - self.radius))

# ==============================================================================
# 0b. CLASS LEADERBOARD: Quản lý bảng xếp hạng (GHI ĐÈ)
# ==============================================================================
class Leaderboard:
    def __init__(self):
        self.save_dir = os.path.join(BASE_DIR, "save")
        self.save_file = os.path.join(self.save_dir, "leaderboard.json")
        self.ensure_save_dir()
        self.scores = self.load_scores()
    
    def ensure_save_dir(self):
        if not os.path.exists(self.save_dir):
            try: os.makedirs(self.save_dir)
            except Exception as e: print(f"Lỗi tạo folder save: {e}")
    
    def load_scores(self):
        if not os.path.exists(self.save_file): return []
        try:
            with open(self.save_file, 'r', encoding='utf-8') as f: return json.load(f)
        except: return []
    
    def save_scores(self):
        try:
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(self.scores, f, ensure_ascii=False, indent=2)
        except Exception as e: print(f"Lỗi lưu file: {e}")
    
    def add_or_update_score(self, player_name, score_x, score_o, mode):
        """Thêm mới hoặc cập nhật điểm nếu trùng tên"""
        # Tìm xem tên đã tồn tại chưa (không phân biệt hoa thường)
        existing_entry = next((item for item in self.scores if item["name"].lower() == player_name.lower()), None)
        
        current_total = score_x + score_o
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        if existing_entry:
            # Nếu tồn tại -> Cập nhật (Ghi đè)
            existing_entry["score_x"] = score_x
            existing_entry["score_o"] = score_o
            existing_entry["total"] = current_total
            existing_entry["mode"] = mode
            existing_entry["date"] = timestamp
            # Chuẩn hóa lại tên theo lần nhập mới nhất
            existing_entry["name"] = player_name 
        else:
            # Nếu chưa có -> Thêm mới
            entry = {
                "name": player_name,
                "score_x": score_x,
                "score_o": score_o,
                "total": current_total,
                "mode": mode,
                "date": timestamp
            }
            self.scores.append(entry)

        # Sắp xếp và lưu
        self.scores.sort(key=lambda x: x["total"], reverse=True)
        self.scores = self.scores[:10] # Giữ top 10
        self.save_scores()
    
    def get_top_scores(self, limit=10):
        return self.scores[:limit]

# ==============================================================================
# 1. CLASS CONFIG: Quản lý tài nguyên (ĐÃ FIX EMOJI LỖI)
# ==============================================================================
class Config:
    BOARD_SIZE = 9
    WIN_CONDITION = 5
    ALLOW_BLOCKED_WIN = False 
    GAP = 2
    BOTTOM_BAR = 120

    HEIGHT = 600
    CELL_SIZE = (HEIGHT - BOTTOM_BAR) // BOARD_SIZE
    WIDTH = BOARD_SIZE * CELL_SIZE
    
    FPS = 60

    # Fonts
    PIXEL_FONT_FILE = path("font", "PixelOperator.ttf")
    SYSTEM_FONT_FILE = path("font", "arial.ttf")
    
    def safe_load_font(path, size):
        try: return pygame.font.Font(path, size)
        except: return pygame.font.SysFont("arial", size)

    FONT_XO = safe_load_font(PIXEL_FONT_FILE, CELL_SIZE * 8 // 10)
    FONT_UI_SMALL = safe_load_font(SYSTEM_FONT_FILE, 16)
    FONT_UI_MED = safe_load_font(SYSTEM_FONT_FILE, 22)
    FONT_UI_MSG = safe_load_font(SYSTEM_FONT_FILE, 32)
    
    # Resources
    MUSIC_MENU_FILE = path("music", "a.mp3")
    MUSIC_GAME_FILE = path("music", "b.mp3")
    CLICK_FILE = path("music", "click.wav")
    WIN_SOUND_FILE = path("music", "win.mp3")
    LOSE_SOUND_FILE = path("music", "lose.mp3")
    
    # Colors
    BG_COLOR = (232, 217, 192)
    CELL_BG = (246, 238, 222)
    WOOD_BORDER = (170, 125, 80)
    GRID_LINE = (120, 82, 45)
    X_COLOR = (180, 30, 30)
    O_COLOR = (120, 65, 130)
    HIGHLIGHT_LINE = (230, 60, 60)
    HOVER_COLOR = (255, 236, 153)
    BTN_BG = (205, 180, 140)
    BTN_TEXT = (50, 30, 20)
    MSG_COLOR = (120, 30, 30)
    SCORE_BG = (220, 200, 170)
    TUTORIAL_BG = (255, 250, 240)
    TUTORIAL_TEXT = (40, 40, 40)

    # Localization 
    TEXTS = {
        "title": {"vi": "Tic Tac Toe - HoangLong", "en": "Tic Tac Toe - HoangLong"},
        "play_2p": {"vi": "Chơi 2 người", "en": "Play 2 Player"},
        "play_ai": {"vi": "Chơi với máy (AI)", "en": "Play with AI"},
        "leaderboard": {"vi": "Bảng Xếp Hạng", "en": "Leaderboard"},
        "tutorial": {"vi": "Hướng Dẫn", "en": "Tutorial"},
        "ai_select_title": {"vi": ">> Chọn Độ Khó AI <<", "en": ">> Select Difficulty <<"},
        "ai_easy": {"vi": "AI Dễ (Ngẫu nhiên)", "en": "Easy AI (Random)"},
        "ai_hard": {"vi": "AI Khó (Minimax 3-ply)", "en": "Hard AI (Minimax)"},
        "quit": {"vi": "Thoát", "en": "Quit"},
        "hint": {"vi": "Game Đang Trong Giai Đoạn Phát Triển", "en": "Game In Development"},
        "lang_btn": {"vi": "Ngôn ngữ:", "en": "Language:"},
        "restart": {"vi": "Chơi Lại", "en": "Restart"},
        "menu_back": {"vi": "Menu", "en": "Menu"},
        "undo": {"vi": "Đi Lại", "en": "Undo"},
        "score": {"vi": "Tỉ số", "en": "Score"},
        "music_on": {"vi": "Nhạc: Bật", "en": "Music: On"},
        "music_off": {"vi": "Nhạc: Tắt", "en": "Music: Off"},
        "turn_of": {"vi": "Lượt của:", "en": "Turn of:"},
        "win_x": {"vi": "Người chơi X thắng!", "en": "Player X wins!"},
        "win_o": {"vi": "Người chơi O thắng!", "en": "Player O wins!"},
        "draw": {"vi": "Hòa rồi!", "en": "It's a Draw!"},
        "back": {"vi": "Quay Lại", "en": "Back"},
        "leaderboard_title": {"vi": "--- BẢNG XẾP HẠNG ---", "en": "--- LEADERBOARD ---"},
        "rank": {"vi": "Hạng", "en": "Rank"},
        "name": {"vi": "Tên", "en": "Name"},
        "total": {"vi": "Tổng Ván", "en": "Total"},
        "mode": {"vi": "Chế độ", "en": "Mode"},
        "date": {"vi": "Ngày", "en": "Date"},
        "no_scores": {"vi": "Chưa có điểm nào!", "en": "No scores yet!"},
        "save_score_prompt": {"vi": "Lưu điểm ? Nhập tên:", "en": "Save score ? Enter name:"},
        "mode_2p": {"vi": "2 Người", "en": "2 Player"},
        "mode_ai_easy": {"vi": "AI Dễ", "en": "AI Easy"},
        "mode_ai_hard": {"vi": "AI Khó", "en": "AI Hard"},
       #a
        "tutorial_title": {"vi": "[ HƯỚNG DẪN CHƠI ]", "en": "[ HOW TO PLAY ]"},
        "tut_1": {"vi": ">> MỤC TIÊU:", "en": ">> OBJECTIVE:"},
        "tut_1_desc": {"vi": "Xếp 5 quân cờ liên tiếp theo hàng ngang, dọc hoặc chéo", "en": "Align 5 pieces in a row (horizontal, vertical, or diagonal)"},
        "tut_2": {"vi": ">> CÁCH CHƠI:", "en": ">> HOW TO PLAY:"},
        "tut_2_desc": {"vi": "- Click vào ô trống để đánh\n- X đi trước, O đi sau\n- Luân phiên đánh cho đến khi có người thắng", "en": "- Click empty cell to place\n- X goes first, O goes second\n- Take turns until someone wins"},
        "tut_3": {"vi": ">> TÍNH NĂNG:", "en": ">> FEATURES:"},
        "tut_3_desc": {"vi": "- Undo: Đi lại nước đã đánh\n- Score: Điểm được lưu qua các ván\n- Leaderboard: Bảng xếp hạng điểm cao", "en": "- Undo: Take back your move\n- Score: Points saved across games\n- Leaderboard: High score ranking"},
        "tut_4": {"vi": ">> CHẾ ĐỘ AI:", "en": ">> AI MODES:"},
        "tut_4_desc": {"vi": "- AI Dễ: Đánh ngẫu nhiên\n- AI Khó: Sử dụng thuật toán Minimax", "en": "- Easy AI: Random moves\n- Hard AI: Uses Minimax algorithm"},
        "tut_5": {"vi": ">> MẸO:", "en": ">> TIPS:"},
        "tut_5_desc": {"vi": "- Kiểm soát trung tâm bàn cờ\n- Tạo nhiều hàng đồng thời\n- Chặn đối thủ khi họ sắp thắng", "en": "- Control the center of the board\n- Create multiple threats at once\n- Block opponent when they're close to winning"},
    }
    
    # Sounds
    def safe_load_sound(path):
        if not os.path.exists(path): return None
        try: return pygame.mixer.Sound(path)
        except: return None
        
    CLICK_SOUND = safe_load_sound(CLICK_FILE)
    WIN_SOUND = safe_load_sound(WIN_SOUND_FILE)
    LOSE_SOUND = safe_load_sound(LOSE_SOUND_FILE)

# ==============================================================================
# 2. CLASS BOARD: Xử lý logic và vẽ bảng cờ
# ==============================================================================
class Board:
    def __init__(self, size, win_cond, allow_blocked):
        self.size = size
        self.win_cond = win_cond
        self.allow_blocked = allow_blocked
        self.reset()

    def reset(self):
        self.grid = [["" for _ in range(self.size)] for _ in range(self.size)]
        self.winning_line = None
        self.winning_cells = []
        self.place_animations = {}
    
    def cell_rect(self, r, c):
        x = c * Config.CELL_SIZE
        y = r * Config.CELL_SIZE
        return pygame.Rect(x + Config.GAP, y + Config.GAP, Config.CELL_SIZE - Config.GAP * 2, Config.CELL_SIZE - Config.GAP * 2)

    def pixel_center(self, r, c):
        return (c * Config.CELL_SIZE + Config.CELL_SIZE // 2, r * Config.CELL_SIZE + Config.CELL_SIZE // 2)

    def draw(self, screen, game_state, current_player, mouse_pos):
        # 1. Vẽ nền và lưới
        screen.fill(Config.BG_COLOR)
        for i in range(0, Config.WIDTH, 12):
            pygame.draw.rect(screen, (220, 200, 170), (i, 0, 12 // 3, self.size * Config.CELL_SIZE))

        for r in range(self.size):
            for c in range(self.size):
                rect = self.cell_rect(r, c)
                pygame.draw.rect(screen, Config.CELL_BG, rect)
                pygame.draw.rect(screen, Config.WOOD_BORDER, rect, 2)

        # 2. Hiệu ứng Hover (Chỉ khi chưa thắng)
        if game_state == "game" and not self.winning_line and mouse_pos[1] < self.size * Config.CELL_SIZE:
            col = mouse_pos[0] // Config.CELL_SIZE
            row = mouse_pos[1] // Config.CELL_SIZE
            if 0 <= row < self.size and 0 <= col < self.size and self.grid[row][col] == "":
                # Vẽ shadow mờ của quân cờ sắp đánh
                pygame.draw.rect(screen, Config.HOVER_COLOR, self.cell_rect(row, col))
                
                # Preview quân cờ mờ
                color = Config.X_COLOR if current_player == "X" else Config.O_COLOR
                surf = Config.FONT_XO.render(current_player, True, color)
                surf.set_alpha(100)
                center = self.pixel_center(row, col)
                screen.blit(surf, (center[0] - surf.get_width() // 2, center[1] - surf.get_height() // 2))

        # 3. Vẽ quân cờ (X/O)
        now = pygame.time.get_ticks()
        to_delete = []
        for r in range(self.size):
            for c in range(self.size):
                v = self.grid[r][c]
                if v == "": continue
                
                center = self.pixel_center(r, c)
                color = Config.X_COLOR if v == "X" else Config.O_COLOR
                surf = Config.FONT_XO.render(v, True, color)

                key = (r, c)
                scale = 1.0
                if key in self.place_animations:
                    start, dur = self.place_animations[key]
                    elapsed = now - start
                    if elapsed < dur:
                        t = elapsed / dur
                        scale = 1.6 - 0.6 * t
                    else:
                        scale = 1.0
                        to_delete.append(key)
                
                if scale != 1.0:
                    sw = max(1, int(surf.get_width() * scale))
                    sh = max(1, int(surf.get_height() * scale))
                    surf = pygame.transform.scale(surf, (sw, sh))
                
                screen.blit(surf, (center[0] - surf.get_width() // 2, center[1] - surf.get_height() // 2))
        
        for key in to_delete:
            del self.place_animations[key]

    def draw_highlight(self, screen, flash_phase):
        if not self.winning_line: return
        
        if flash_phase % 2 == 1:
            for (r, c) in self.winning_cells:
                rct = self.cell_rect(r, c)
                pygame.draw.rect(screen, Config.HOVER_COLOR, rct.inflate(-4, -4))
            pygame.draw.line(screen, Config.HIGHLIGHT_LINE, self.winning_line[0], self.winning_line[1], 12)

    def check_winner(self):
        result, cells, line = self.check_winner_pure(self.grid)
        self.winning_cells = cells
        self.winning_line = line
        return result

    def check_winner_pure(self, grid):
        dirs = [(0, 1), (1, 0), (1, 1), (1, -1)]
        size = self.size
        win_cond = self.win_cond
        
        for r in range(size):
            for c in range(size):
                p = grid[r][c]
                if p == "": continue
                
                for dr, dc in dirs:
                    count = 1
                    sr, sc = r, c
                    er, ec = r, c
                    
                    rr, cc = r + dr, c + dc
                    while 0 <= rr < size and 0 <= cc < size and grid[rr][cc] == p:
                        count += 1
                        er, ec = rr, cc
                        rr += dr; cc += dc
                        
                    rr, cc = r - dr, c - dc
                    while 0 <= rr < size and 0 <= cc < size and grid[rr][cc] == p:
                        count += 1
                        sr, sc = rr, cc
                        rr -= dr; cc -= dc
                        
                    if count >= win_cond:
                        if not self.allow_blocked:
                            prev_r, prev_c = sr - dr, sc - dc
                            next_r, next_c = er + dr, ec + dc
                            
                            blocked_start = 0 <= prev_r < size and 0 <= prev_c < size and grid[prev_r][prev_c] != ""
                            blocked_end = 0 <= next_r < size and 0 <= next_c < size and grid[next_r][next_c] != ""
                            
                            if blocked_start and blocked_end:
                                continue 
                        
                        cells = []
                        rr, cc = sr, sc
                        for _ in range(count):
                            cells.append((rr, cc))
                            rr += dr; cc += dc
                        
                        line_start = (sc * Config.CELL_SIZE + Config.CELL_SIZE // 2, sr * Config.CELL_SIZE + Config.CELL_SIZE // 2)
                        line_end = (ec * Config.CELL_SIZE + Config.CELL_SIZE // 2, er * Config.CELL_SIZE + Config.CELL_SIZE // 2)

                        return p, cells, (line_start, line_end)
                        
        return None, [], None

# ==============================================================================
# 3a. CLASS HardAI (Minimax 3-ply)
# ==============================================================================
class HardAI:
    def __init__(self, board):
        self.board = board
        self.max_depth = 3 
        self.ai_char = "O"
        self.opp_char = "X"

    def available_moves(self):
        return [(r, c) for r in range(self.board.size) for c in range(self.board.size) if self.board.grid[r][c] == ""]

    def find_winning_move_for(self, player_char):
        for r in range(self.board.size):
            for c in range(self.board.size):
                if self.board.grid[r][c] == "":
                    self.board.grid[r][c] = player_char
                    winner, _, _ = self.board.check_winner_pure(self.board.grid)
                    self.board.grid[r][c] = ""
                    if winner == player_char:
                        return (r, c)
        return None

    def score_board_for(self, player_char):
        opp_char = self.opp_char if player_char == self.ai_char else self.ai_char
        size = self.board.size
        
        def count_score(ch, opp):
            score = 0
            dirs = [(0, 1), (1, 0), (1, 1), (1, -1)]
            for r in range(size):
                for c in range(size):
                    if self.board.grid[r][c] != ch: continue
                    for dr, dc in dirs:
                        if dr < 0 or (dr == 0 and dc < 0) or (dr < 0 and dc == 0): continue
                        
                        length = 0
                        rr, cc = r, c
                        while 0 <= rr < size and 0 <= cc < size and self.board.grid[rr][cc] == ch:
                            length += 1
                            rr += dr; cc += dc
                        
                        if length >= self.board.win_cond: score += 1000000 
                        elif length >= 2:
                            is_start_open = 0 <= r - dr < size and 0 <= c - dc < size and self.board.grid[r - dr][c - dc] == ""
                            is_end_open = 0 <= rr < size and 0 <= cc < size and self.board.grid[rr][cc] == ""
                            is_start_blocked = 0 <= r - dr < size and 0 <= c - dc < size and self.board.grid[r - dr][c - dc] == opp
                            is_end_blocked = 0 <= rr < size and 0 <= cc < size and self.board.grid[rr][cc] == opp

                            if length == 4:
                                if is_start_open and is_end_open: score += 500000 
                                elif is_start_open or is_end_open: score += 5000
                                elif not self.board.allow_blocked and is_start_blocked and is_end_blocked: continue
                            elif length == 3:
                                if is_start_open and is_end_open: score += 5000
                                elif is_start_open or is_end_open: score += 100
                            elif length == 2:
                                if is_start_open and is_end_open: score += 10
            return score

        return count_score(player_char, opp_char) - count_score(opp_char, player_char) * 1.2 

    def minimax(self, depth, maximizing, alpha=-inf, beta=inf):
        winner, _, _ = self.board.check_winner_pure(self.board.grid)
        
        if winner:
            return (10000000 + depth if winner == self.ai_char else -10000000 - depth), None
        if depth == 0:
            return self.score_board_for(self.ai_char), None

        moves = self.available_moves()
        if not moves: return 0, None

        best_move = None
        current_player = self.ai_char if maximizing else self.opp_char
        center_moves = self.get_centered_moves(moves)
        
        if maximizing:
            max_eval = -inf
            for (r, c) in center_moves:
                self.board.grid[r][c] = current_player
                val, _ = self.minimax(depth - 1, False, alpha, beta)
                self.board.grid[r][c] = ""
                
                if val > max_eval:
                    max_eval = val; best_move = (r, c)
                alpha = max(alpha, val)
                if beta <= alpha: break
            return max_eval, best_move
        else:
            min_eval = inf
            for (r, c) in center_moves:
                self.board.grid[r][c] = current_player
                val, _ = self.minimax(depth - 1, True, alpha, beta)
                self.board.grid[r][c] = ""
                
                if val < min_eval:
                    min_eval = val; best_move = (r, c)
                beta = min(beta, val)
                if beta <= alpha: break
            return min_eval, best_move

    def get_centered_moves(self, moves):
        if not any(self.board.grid[r][c] != "" for r in range(self.board.size) for c in range(self.board.size)):
             return [(self.board.size//2, self.board.size//2)] 
             
        scored_moves = []
        center = (self.board.size // 2, self.board.size // 2)
        
        for r, c in moves:
            score = 0
            score -= (abs(r - center[0]) + abs(c - center[1])) 
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0: continue
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < self.board.size and 0 <= cc < self.board.size:
                        if self.board.grid[rr][cc] != "": score += 5 
            scored_moves.append((score, (r, c)))
        
        scored_moves.sort(key=lambda x: x[0], reverse=True)
        return [move for score, move in scored_moves[:20]] 

    def get_move(self):
        mv = self.find_winning_move_for(self.ai_char)
        if mv: return mv
        mv = self.find_winning_move_for(self.opp_char)
        if mv: return mv
        
        val, mv = self.minimax(self.max_depth, True)
        if mv: return mv
        
        moves = self.available_moves()
        if not moves: return None
        return self.get_centered_moves(moves)[0] if moves else random.choice(moves)

# ==============================================================================
# 3b. CLASS EasyAI (1-ply + Random)
# ==============================================================================
class EasyAI:
    def __init__(self, board):
        self.board = board
        self.ai_char = "O"
        self.opp_char = "X"

    def available_moves(self):
        return [(r, c) for r in range(self.board.size) for c in range(self.board.size) if self.board.grid[r][c] == ""]

    def find_winning_move_for(self, player_char):
        for r in range(self.board.size):
            for c in range(self.board.size):
                if self.board.grid[r][c] == "":
                    self.board.grid[r][c] = player_char
                    winner, _, _ = self.board.check_winner_pure(self.board.grid)
                    self.board.grid[r][c] = ""
                    if winner == player_char:
                        return (r, c)
        return None

    def get_adjacent_moves(self, moves):
        if not any(self.board.grid[r][c] != "" for r in range(self.board.size) for c in range(self.board.size)):
             return [(self.board.size//2, self.board.size//2)]
        
        adjacent_moves = []
        for r, c in moves:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0: continue
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < self.board.size and 0 <= cc < self.board.size:
                        if self.board.grid[rr][cc] != "": 
                            adjacent_moves.append((r, c))
                            break
        
        return adjacent_moves if adjacent_moves else moves

    def get_move(self):
        mv = self.find_winning_move_for(self.ai_char)
        if mv: return mv
        mv = self.find_winning_move_for(self.opp_char)
        if mv: return mv
        
        moves = self.available_moves()
        if not moves: return None
        
        center_moves = self.get_adjacent_moves(moves)
        return random.choice(center_moves)
    
# ==============================================================================
# 4. CLASS GAME: Quản lý trạng thái và vòng lặp chính
# ==============================================================================
class Game:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.board = Board(Config.BOARD_SIZE, Config.WIN_CONDITION, Config.ALLOW_BLOCKED_WIN)
        self.ai = None
        self.ai_level = "hard"
        self.lang = "vi"
        self.music_on = True
        self.state = "menu"
        self.ai_enabled = False
        
        self.player = "X"
        self.game_over = False
        self.winner = None
        self.move_history = []
        self.scores = {"X": 0, "O": 0}
        
        self.flash_phase = 0
        self.flash_interval = 300
        self.last_flash_time = 0
        
        self.particles = []
        
        # Leaderboard
        self.leaderboard = Leaderboard()
        self.show_save_prompt = False
        self.player_name_input = ""
        
        # --- [NEW] Biến ghi nhớ tên người chơi cho session hiện tại ---
        self.cached_player_name = None 

        # Rects (Giữ nguyên như cũ)
        self.restart_rect = pygame.Rect(0, 0, 1, 1) 
        self.menuback_rect = pygame.Rect(0, 0, 1, 1)
        self.music_rect = pygame.Rect(0, 0, 1, 1)
        self.undo_rect = pygame.Rect(0, 0, 1, 1)
        
        self.play_rect = pygame.Rect(0, 0, 1, 1)
        self.ai_select_rect = pygame.Rect(0, 0, 1, 1)
        self.leaderboard_rect = pygame.Rect(0, 0, 1, 1)
        self.tutorial_rect = pygame.Rect(0, 0, 1, 1)
        self.lang_rect = pygame.Rect(0, 0, 1, 1)
        self.quit_rect = pygame.Rect(0, 0, 1, 1)
        self.easy_ai_rect = pygame.Rect(0, 0, 1, 1)
        self.hard_ai_rect = pygame.Rect(0, 0, 1, 1)
        self.back_ai_rect = pygame.Rect(0, 0, 1, 1)
        self.back_leaderboard_rect = pygame.Rect(0, 0, 1, 1)
        self.back_tutorial_rect = pygame.Rect(0, 0, 1, 1)

    def get_text(self, key):
        return Config.TEXTS.get(key, {}).get(self.lang, key)
    
    # --- AUDIO UTILS (Giữ nguyên) ---
    def play_click(self):
        if Config.CLICK_SOUND: Config.CLICK_SOUND.play()

    def play_end_sound(self):
        if self.winner == "X":
            if Config.WIN_SOUND: Config.WIN_SOUND.play()
        elif self.winner == "O":
            if self.ai_enabled and Config.LOSE_SOUND:
                Config.LOSE_SOUND.play()
            elif Config.WIN_SOUND:
                Config.WIN_SOUND.play()
        elif self.game_over and Config.LOSE_SOUND:
            Config.LOSE_SOUND.play()

    def start_music(self):
        if not self.music_on: return
        music_file = Config.MUSIC_GAME_FILE if self.state == "game" else Config.MUSIC_MENU_FILE
        if not os.path.exists(music_file): return
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.set_volume(0.45)
            pygame.mixer.music.play(-1, 0.0)
        except Exception as e:
            print(f"Lỗi khi phát nhạc: {e}")

    def stop_music(self):
        try: pygame.mixer.music.stop()
        except: pass
    
    # --- PARTICLE EFFECT (Giữ nguyên) ---
    def create_win_particles(self):
        if not self.board.winning_cells: return
        target_cells = self.board.winning_cells
        if len(target_cells) > 3:
            target_cells = random.sample(self.board.winning_cells, 3)
        for r, c in target_cells:
            center = self.board.pixel_center(r, c)
            color = Config.X_COLOR if self.winner == "X" else Config.O_COLOR
            for _ in range(30):
                self.particles.append(Particle(center[0], center[1], color))

    def update_particles(self):
        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)

    def draw_particles(self):
        for p in self.particles:
            p.draw(self.screen)

    # --- STATE MANAGEMENT ---
    def reset_game(self, ai_mode=False):
        self.board.reset()
        self.player = "X"
        self.game_over = False
        self.winner = None
        self.move_history = []
        self.particles = []
        self.flash_phase = 0
        self.ai_enabled = ai_mode
        self.state = "game"
        self.show_save_prompt = False
        self.player_name_input = "" 
        # Lưu ý: Không reset cached_player_name ở đây để giữ tên khi Restart
        
        if ai_mode:
            if self.ai_level == "easy":
                self.ai = EasyAI(self.board)
            else:
                self.ai = HardAI(self.board)
        else:
            self.ai = None
            
        self.start_music()

    def undo_move(self):
        if self.game_over or not self.move_history: return
        def pop_one():
            if not self.move_history: return
            r, c = self.move_history.pop()
            self.board.grid[r][c] = ""
            if (r, c) in self.board.place_animations:
                del self.board.place_animations[(r, c)]

        if self.ai_enabled:
            pop_one()
            pop_one()
            self.player = "X"
        else:
            pop_one()
            self.player = "O" if self.player == "X" else "X"
        self.play_click()

    def go_to_menu(self):
        self.state = "menu"
        self.show_save_prompt = False
        self.cached_player_name = None # [NEW] Về menu thì quên tên đi
        self.start_music()
        
    def go_to_ai_select(self):
        self.state = "ai_select"
        self.cached_player_name = None # [NEW] Đổi chế độ cũng quên tên luôn
        
    def go_to_leaderboard(self):
        self.state = "leaderboard"
        
    def go_to_tutorial(self):
        self.state = "tutorial"
        
    def toggle_music(self):
        self.music_on = not self.music_on
        if self.music_on: self.start_music()
        else: self.stop_music()

    def save_score_to_leaderboard(self):
        """Lưu điểm vào bảng xếp hạng"""
        # Nếu đang có input thì lấy input, nếu không (auto save) thì lấy cache
        name = self.player_name_input.strip()
        if not name and self.cached_player_name:
             name = self.cached_player_name

        if not name: name = "Player"
        
        # [NEW] Cập nhật Cache để lần sau dùng lại
        self.cached_player_name = name

        mode = ""
        if not self.ai_enabled: mode = self.get_text("mode_2p")
        elif self.ai_level == "easy": mode = self.get_text("mode_ai_easy")
        else: mode = self.get_text("mode_ai_hard")
        
        self.leaderboard.add_or_update_score(
            name,
            self.scores["X"],
            self.scores["O"],
            mode
        )
        self.show_save_prompt = False
        self.player_name_input = ""

    # --- DRAWING (Giữ nguyên toàn bộ phần Draw) ---
    def draw_menu(self):
        self.screen.fill(Config.BG_COLOR)
        title = Config.FONT_UI_MSG.render(self.get_text("title"), True, Config.GRID_LINE)
        self.screen.blit(title, (Config.WIDTH // 2 - title.get_width() // 2, 20))

        btn_w, btn_h = 300, 50
        start_y = 100
        gap = 10
        
        self.play_rect = pygame.Rect(Config.WIDTH // 2 - btn_w // 2, start_y, btn_w, btn_h)
        self.ai_select_rect = pygame.Rect(Config.WIDTH // 2 - btn_w // 2, start_y + btn_h + gap, btn_w, btn_h)
        self.leaderboard_rect = pygame.Rect(Config.WIDTH // 2 - btn_w // 2, start_y + 2*(btn_h + gap), btn_w, btn_h)
        self.tutorial_rect = pygame.Rect(Config.WIDTH // 2 - btn_w // 2, start_y + 3*(btn_h + gap), btn_w, btn_h)
        self.lang_rect = pygame.Rect(Config.WIDTH // 2 - btn_w // 2, start_y + 4*(btn_h + gap), btn_w, btn_h)
        self.quit_rect = pygame.Rect(Config.WIDTH // 2 - btn_w // 2, start_y + 5*(btn_h + gap), btn_w, btn_h)

        buttons = [
            (self.play_rect, "play_2p"),
            (self.ai_select_rect, "play_ai"),
            (self.leaderboard_rect, "leaderboard"),
            (self.tutorial_rect, "tutorial"),
            (self.lang_rect, None),
            (self.quit_rect, "quit")
        ]

        for rect, key in buttons:
            pygame.draw.rect(self.screen, Config.BTN_BG, rect)
            pygame.draw.rect(self.screen, Config.WOOD_BORDER, rect, 2)
            
            if key is None:
                lang_display = "Tiếng Việt" if self.lang == "vi" else "ENGLISH"
                txt = Config.FONT_UI_MED.render(f"{self.get_text('lang_btn')} {lang_display}", True, Config.BTN_TEXT)
            else:
                txt_str = self.get_text(key)
                if key == "play_2p":
                    txt_str = f"{txt_str} ({Config.BOARD_SIZE}x{Config.BOARD_SIZE})"
                txt = Config.FONT_UI_MED.render(txt_str, True, Config.BTN_TEXT)
            
            self.screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

        hint = Config.FONT_UI_SMALL.render(self.get_text("hint"), True, Config.GRID_LINE)
        self.screen.blit(hint, (Config.WIDTH // 2 - hint.get_width() // 2, Config.HEIGHT - 30))

    def draw_ai_select(self):
        self.screen.fill(Config.BG_COLOR)
        title = Config.FONT_UI_MSG.render(self.get_text("ai_select_title"), True, Config.GRID_LINE)
        self.screen.blit(title, (Config.WIDTH // 2 - title.get_width() // 2, 26))

        btn_w, btn_h = 350, 60
        self.easy_ai_rect = pygame.Rect(Config.WIDTH // 2 - btn_w // 2, 120, btn_w, btn_h)
        self.hard_ai_rect = pygame.Rect(Config.WIDTH // 2 - btn_w // 2, 200, btn_w, btn_h)
        self.back_ai_rect = pygame.Rect(Config.WIDTH // 2 - btn_w // 2, 360, btn_w, btn_h)

        if self.ai_level == "easy":
            pygame.draw.rect(self.screen, Config.HIGHLIGHT_LINE, self.easy_ai_rect.inflate(8, 8), 4)
        else:
            pygame.draw.rect(self.screen, Config.HIGHLIGHT_LINE, self.hard_ai_rect.inflate(8, 8), 4)

        for rect in [self.easy_ai_rect, self.hard_ai_rect, self.back_ai_rect]:
            pygame.draw.rect(self.screen, Config.BTN_BG, rect)

        easy_txt = Config.FONT_UI_MED.render(self.get_text("ai_easy"), True, Config.BTN_TEXT)
        hard_txt = Config.FONT_UI_MED.render(self.get_text("ai_hard"), True, Config.BTN_TEXT)
        back_txt = Config.FONT_UI_MED.render(self.get_text("menu_back"), True, Config.BTN_TEXT)

        for txt, rect in [(easy_txt, self.easy_ai_rect), (hard_txt, self.hard_ai_rect), (back_txt, self.back_ai_rect)]:
            self.screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.y + (btn_h - txt.get_height()) // 2))

    def draw_leaderboard(self):
        self.screen.fill(Config.BG_COLOR)
        title = Config.FONT_UI_MSG.render(self.get_text("leaderboard_title"), True, Config.GRID_LINE)
        self.screen.blit(title, (Config.WIDTH // 2 - title.get_width() // 2, 20))
        top_scores = self.leaderboard.get_top_scores()
        
        if not top_scores:
            no_score_txt = Config.FONT_UI_MED.render(self.get_text("no_scores"), True, Config.MSG_COLOR)
            self.screen.blit(no_score_txt, (Config.WIDTH // 2 - no_score_txt.get_width() // 2, 150))
        else:
            y = 80
            header_font = Config.FONT_UI_SMALL
            headers = [self.get_text("rank"), self.get_text("name"), self.get_text("total"), self.get_text("mode"), self.get_text("date")]
            x_positions = [20, 70, 190, 270, 370]
            for i, header in enumerate(headers):
                txt = header_font.render(header, True, Config.GRID_LINE)
                self.screen.blit(txt, (x_positions[i], y))
            pygame.draw.line(self.screen, Config.WOOD_BORDER, (15, y + 25), (Config.WIDTH - 15, y + 25), 2)
            y = 115
            for idx, score in enumerate(top_scores):
                rank = f"#{idx + 1}"
                name = score["name"][:12]
                total = f"{score['total']}"
                mode = score["mode"]
                date = score["date"].split()[0]
                data = [rank, name, total, mode, date]
                if idx < 3:
                    bg_rect = pygame.Rect(15, y - 5, Config.WIDTH - 30, 25)
                    pygame.draw.rect(self.screen, Config.SCORE_BG, bg_rect)
                for i, text in enumerate(data):
                    txt = Config.FONT_UI_SMALL.render(str(text), True, Config.BTN_TEXT)
                    self.screen.blit(txt, (x_positions[i], y))
                y += 30
        
        btn_w, btn_h = 200, 50
        self.back_leaderboard_rect = pygame.Rect(Config.WIDTH // 2 - btn_w // 2, Config.HEIGHT - 70, btn_w, btn_h)
        pygame.draw.rect(self.screen, Config.BTN_BG, self.back_leaderboard_rect)
        back_txt = Config.FONT_UI_MED.render(self.get_text("back"), True, Config.BTN_TEXT)
        self.screen.blit(back_txt, (self.back_leaderboard_rect.centerx - back_txt.get_width() // 2, self.back_leaderboard_rect.centery - back_txt.get_height() // 2))

    def draw_tutorial(self):
        self.screen.fill(Config.TUTORIAL_BG)
        title = Config.FONT_UI_MSG.render(self.get_text("tutorial_title"), True, Config.GRID_LINE)
        self.screen.blit(title, (Config.WIDTH // 2 - title.get_width() // 2, 15))
        y = 65
        sections = [("tut_1", "tut_1_desc"), ("tut_2", "tut_2_desc"), ("tut_3", "tut_3_desc"), ("tut_4", "tut_4_desc"), ("tut_5", "tut_5_desc")]
        for title_key, desc_key in sections:
            title_txt = Config.FONT_UI_MED.render(self.get_text(title_key), True, Config.MSG_COLOR)
            self.screen.blit(title_txt, (20, y))
            y += 25
            desc = self.get_text(desc_key)
            lines = desc.split('\n')
            for line in lines:
                line_txt = Config.FONT_UI_SMALL.render(line, True, Config.TUTORIAL_TEXT)
                self.screen.blit(line_txt, (30, y))
                y += 20
            y += 10
        btn_w, btn_h = 200, 50
        self.back_tutorial_rect = pygame.Rect(Config.WIDTH // 2 - btn_w // 2, Config.HEIGHT - 70, btn_w, btn_h)
        pygame.draw.rect(self.screen, Config.BTN_BG, self.back_tutorial_rect)
        back_txt = Config.FONT_UI_MED.render(self.get_text("back"), True, Config.BTN_TEXT)
        self.screen.blit(back_txt, (self.back_tutorial_rect.centerx - back_txt.get_width() // 2, self.back_tutorial_rect.centery - back_txt.get_height() // 2))

    def draw_control(self):
        bar_y = Config.BOARD_SIZE * Config.CELL_SIZE
        bar_rect = pygame.Rect(0, bar_y, Config.WIDTH, Config.BOTTOM_BAR)
        pygame.draw.rect(self.screen, Config.BG_COLOR, bar_rect)
        pygame.draw.rect(self.screen, Config.WOOD_BORDER, (0, bar_y, Config.WIDTH, 2))
        btn_w, btn_h = 100, 40
        gap = 10
        total_w = 4 * btn_w + 3 * gap
        start_x = (Config.WIDTH - total_w) // 2
        btn_y = bar_y + 70

        self.menuback_rect = pygame.Rect(start_x, btn_y, btn_w, btn_h)
        self.undo_rect = pygame.Rect(start_x + btn_w + gap, btn_y, btn_w, btn_h)
        self.music_rect = pygame.Rect(start_x + 2*btn_w + 2*gap, btn_y, btn_w, btn_h)
        self.restart_rect = pygame.Rect(start_x + 3*btn_w + 3*gap, btn_y, btn_w, btn_h)

        music_txt = "Music: On" if self.music_on else "Music: Off"
        if self.lang == "vi": music_txt = "Nhạc: Bật" if self.music_on else "Nhạc: Tắt"
        buttons = [(self.menuback_rect, "menu_back", False), (self.undo_rect, "undo", self.game_over or not self.move_history), (self.music_rect, music_txt, False), (self.restart_rect, "restart", False)]

        for rect, key, disabled in buttons:
            color = (180, 160, 140) if disabled else Config.BTN_BG
            pygame.draw.rect(self.screen, color, rect)
            txt_str = key if key == music_txt else self.get_text(key)
            txt = Config.FONT_UI_SMALL.render(txt_str, True, Config.BTN_TEXT)
            self.screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

        msg_y = bar_y + 10
        score_str = f"X: {self.scores['X']}  |  O: {self.scores['O']}"
        score_surf = Config.FONT_UI_MED.render(score_str, True, Config.BTN_TEXT)
        score_bg_rect = score_surf.get_rect(topleft=(20, msg_y))
        pygame.draw.rect(self.screen, Config.SCORE_BG, score_bg_rect.inflate(10, 6))
        self.screen.blit(score_surf, score_bg_rect)

        if not self.game_over:
            turn_msg = f"{self.get_text('turn_of')} {self.player}"
            msg_surf = Config.FONT_UI_MED.render(turn_msg, True, Config.MSG_COLOR)
        else:
            if self.winner == "X": msg = self.get_text("win_x")
            elif self.winner == "O": msg = self.get_text("win_o")
            else: msg = self.get_text("draw")
            msg_surf = Config.FONT_UI_MSG.render(msg, True, Config.MSG_COLOR)
        self.screen.blit(msg_surf, (Config.WIDTH // 2 - msg_surf.get_width() // 2, msg_y))
        if self.show_save_prompt:
            self.draw_save_prompt()

    def draw_save_prompt(self):
        overlay = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        box_w, box_h = 350, 150
        box_x = (Config.WIDTH - box_w) // 2
        box_y = (Config.HEIGHT - box_h) // 2
        pygame.draw.rect(self.screen, Config.TUTORIAL_BG, (box_x, box_y, box_w, box_h))
        pygame.draw.rect(self.screen, Config.WOOD_BORDER, (box_x, box_y, box_w, box_h), 3)
        prompt_txt = Config.FONT_UI_MED.render(self.get_text("save_score_prompt"), True, Config.BTN_TEXT)
        self.screen.blit(prompt_txt, (box_x + box_w // 2 - prompt_txt.get_width() // 2, box_y + 20))
        input_box = pygame.Rect(box_x + 25, box_y + 60, box_w - 50, 35)
        pygame.draw.rect(self.screen, (255, 255, 255), input_box)
        pygame.draw.rect(self.screen, Config.WOOD_BORDER, input_box, 2)
        input_txt = Config.FONT_UI_MED.render(self.player_name_input, True, Config.BTN_TEXT)
        self.screen.blit(input_txt, (input_box.x + 5, input_box.y + 5))
        hint = Config.FONT_UI_SMALL.render("Enter: Save | Esc: Cancel", True, Config.BTN_TEXT)
        self.screen.blit(hint, (box_x + box_w // 2 - hint.get_width() // 2, box_y + 110))
    
    # --- GAME LOGIC ---
    def handle_place_move(self, row, col):
        if not (0 <= row < self.board.size and 0 <= col < self.board.size) or self.board.grid[row][col] != "":
            return
            
        self.board.grid[row][col] = self.player
        self.move_history.append((row, col))
        self.board.place_animations[(row, col)] = (pygame.time.get_ticks(), 250)
        self.play_click()

        self.winner = self.board.check_winner()
        
        # LOGIC THẮNG HOẶC HÒA
        if self.winner or all(self.board.grid[r][c] != "" for r in range(self.board.size) for c in range(self.board.size)):
            self.game_over = True
            self.play_end_sound()
            
            if self.winner:
                self.flash_phase = 1
                self.last_flash_time = pygame.time.get_ticks()
                self.scores[self.winner] += 1
                self.create_win_particles()
            
            # [NEW] KIỂM TRA ĐỂ TỰ ĐỘNG LƯU
            if self.cached_player_name:
                # Nếu đã có tên từ ván trước, lưu luôn
                self.player_name_input = self.cached_player_name
                self.save_score_to_leaderboard()
                self.show_save_prompt = False # Chắc chắn là không hiện popup
            else:
                # Nếu chưa có tên (ván đầu), hiện popup
                self.show_save_prompt = True
        else:
            self.player = "O" if self.player == "X" else "X"

    def handle_ai_move(self):
        if self.ai_enabled and not self.game_over and self.player == "O" and self.ai:
            pygame.time.delay(150)
            mv = self.ai.get_move()
            if mv:
                self.handle_place_move(mv[0], mv[1])
    
    # --- EVENT HANDLING ---
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False
        
        if self.show_save_prompt:
            if event.type == pygame.TEXTINPUT:
                if len(self.player_name_input) < 15:
                    self.player_name_input += event.text
                return True
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.save_score_to_leaderboard()
                elif event.key == pygame.K_ESCAPE:
                    self.show_save_prompt = False
                    self.player_name_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.player_name_input = self.player_name_input[:-1]
                return True
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            
            if self.state == "menu":
                if self.play_rect.collidepoint(mx, my):
                    self.reset_game(ai_mode=False)
                elif self.ai_select_rect.collidepoint(mx, my):
                    self.go_to_ai_select()
                elif self.leaderboard_rect.collidepoint(mx, my):
                    self.go_to_leaderboard()
                elif self.tutorial_rect.collidepoint(mx, my):
                    self.go_to_tutorial()
                elif self.lang_rect.collidepoint(mx, my):
                    self.lang = "en" if self.lang == "vi" else "vi"
                elif self.quit_rect.collidepoint(mx, my):
                    return False
            
            elif self.state == "ai_select":
                if self.easy_ai_rect.collidepoint(mx, my):
                    self.ai_level = "easy"
                    self.reset_game(ai_mode=True)
                elif self.hard_ai_rect.collidepoint(mx, my):
                    self.ai_level = "hard"
                    self.reset_game(ai_mode=True)
                elif self.back_ai_rect.collidepoint(mx, my):
                    self.go_to_menu()
            
            elif self.state == "leaderboard":
                if self.back_leaderboard_rect.collidepoint(mx, my):
                    self.go_to_menu()
            
            elif self.state == "tutorial":
                if self.back_tutorial_rect.collidepoint(mx, my):
                    self.go_to_menu()
            
            elif self.state == "game":
                if self.show_save_prompt:
                    pass 
                elif self.restart_rect.collidepoint(mx, my):
                    self.reset_game(self.ai_enabled)
                elif self.menuback_rect.collidepoint(mx, my):
                    self.go_to_menu()
                elif self.music_rect.collidepoint(mx, my):
                    self.toggle_music()
                elif self.undo_rect.collidepoint(mx, my):
                    self.undo_move()
                
                elif my < Config.BOARD_SIZE * Config.CELL_SIZE and not self.game_over:
                    if not (self.ai_enabled and self.player == "O"):
                        col = mx // Config.CELL_SIZE
                        row = my // Config.CELL_SIZE
                        self.handle_place_move(row, col)
        
        return True

    def update_flash(self):
        if self.flash_phase > 0:
            now = pygame.time.get_ticks()
            if now - self.last_flash_time >= self.flash_interval:
                self.flash_phase += 1
                self.last_flash_time = now
                if self.flash_phase > 6:
                    self.flash_phase = 0

    def run(self):
        self.start_music()
        running = True
        
        while running:
            self.clock.tick(Config.FPS)
            
            for event in pygame.event.get():
                if not self.handle_event(event):
                    running = False
                    break
            
            if not running: break
            
            self.handle_ai_move()
            self.update_flash()
            self.update_particles()

            mouse_pos = pygame.mouse.get_pos()
            
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "ai_select":
                self.draw_ai_select()
            elif self.state == "leaderboard":
                self.draw_leaderboard()
            elif self.state == "tutorial":
                self.draw_tutorial()
            elif self.state == "game":
                self.board.draw(self.screen, self.state, self.player, mouse_pos)
                self.draw_control()
                self.board.draw_highlight(self.screen, self.flash_phase)
                self.draw_particles()

            pygame.display.flip()

        pygame.quit()
        sys.exit()

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
try:
    from splash import show_splash
except ImportError:
    def show_splash(screen, clock): pass

if __name__ == '__main__':
    if not os.path.exists("assets"):
        print("Cảnh báo: Không tìm thấy thư mục 'assets'.")

    screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
    pygame.display.set_caption(Config.TEXTS['title']['vi'])
    clock = pygame.time.Clock()

    show_splash(screen, clock)
    
    game = Game(screen, clock)
    game.run()
