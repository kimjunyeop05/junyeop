# This example is not working in Spyder directly (F5 or Run)
# Please type '!python turtle_runaway.py' on IPython console in your Spyder.
import tkinter as tk
import turtle, random, time

# UI 상수

UI = {
    "BAR_BG": "#F5F7FA",
    "BG": "#3399FF",                 # 파란 배경
    "FONT": ("Arial", 14, "bold"),
    "FONT_SMALL": ("Arial", 12, "normal"),
    "ARENA_BORDER": "#AAB2BD",
    "ARENA_HALF": 320,
}

# 난이도별 추격자 속도/틱 주기 (느려짐)
DIFF_CFG = {
    1: {"move": 8,  "turn": 10, "timer": 130},  # 쉬움
    2: {"move": 10, "turn": 12, "timer": 115},
    3: {"move": 12, "turn": 14, "timer": 105},
    4: {"move": 13, "turn": 15, "timer": 95},
    5: {"move": 14, "turn": 16, "timer": 85},   # 어려움
}

# 단계별 점수 가속 (높을수록 더 빨리 오름)
SCORE_MULT = {1: 1.00, 2: 1.25, 3: 1.60, 4: 2.00, 5: 2.60}

class RunawayGame:
    def __init__(self, canvas, runner, chaser,
                 catch_radius=50, time_limit_sec=30, ai_timer_msec=100):
        self.canvas = canvas          # TurtleScreen
        self.runner = runner
        self.chaser = chaser
        self.catch_radius2 = catch_radius ** 2
        self.ai_timer_msec = ai_timer_msec
        self.time_limit_sec = time_limit_sec

        # 기본 모양/색 + 크기
        self.runner.shape('turtle'); self.runner.color('blue'); self.runner.shapesize(2.0); self.runner.penup()
        self.chaser.shape('turtle'); self.chaser.color('red');  self.chaser.shapesize(2.5); self.chaser.penup()

        # UI 터틀
        self.drawer_bar = turtle.RawTurtle(canvas);    self.drawer_bar.hideturtle();    self.drawer_bar.penup();    self.drawer_bar.speed(0)
        self.drawer_status = turtle.RawTurtle(canvas); self.drawer_status.hideturtle(); self.drawer_status.penup(); self.drawer_status.speed(0)
        self.drawer_arena = turtle.RawTurtle(canvas);  self.drawer_arena.hideturtle();  self.drawer_arena.penup();  self.drawer_arena.speed(0)

        # 상태
        self.game_over = False
        self.paused = False
        self.start_time = None
        self.score = 0
        self.level = 1

    #유틸
    def is_catched(self):
        p = self.runner.pos(); q = self.chaser.pos()
        dx, dy = p[0] - q[0], p[1] - q[1]
        return dx*dx + dy*dy < self.catch_radius2

    def _clamp_inside(self, t, size=UI["ARENA_HALF"]):
        x, y = t.position()
        x = max(-size, min(size, x))
        y = max(-size, min(size, y))
        t.setpos(x, y)

    #UI
    def _draw_arena(self, size=UI["ARENA_HALF"]):
        self.drawer_arena.clear()
        self.drawer_arena.pensize(2)
        self.drawer_arena.pencolor(UI["ARENA_BORDER"])
        self.drawer_arena.setpos(-size, -size)
        self.drawer_arena.setheading(0)
        self.drawer_arena.pendown()
        for _ in range(4):
            self.drawer_arena.forward(2*size); self.drawer_arena.left(90)
        self.drawer_arena.penup()
        self.drawer_arena.pensize(1)
        self.drawer_arena.pencolor("black")

    def _draw_status_bar_static(self):
        t = self.drawer_bar
        t.clear()
        t.setheading(0)
        t.setpos(-350, 320)
        t.pendown()
        t.fillcolor(UI["BAR_BG"])
        t.begin_fill()
        for w,h in [(700,0),(0,-40),(-700,0),(0,40)]:
            if h == 0: t.forward(abs(w))
            else: t.right(90 if h < 0 else -90); t.forward(abs(h))
        t.end_fill()
        t.penup()
        t.setpos(-350, -345)
        t.write("Arrow Keys: Move  |  P: Pause/Resume  |  R: Restart",
                font=UI["FONT_SMALL"])

    def _draw_status_bar(self, is_catched, remain, score):
        s = self.drawer_status
        s.clear()
        status_txt = "CAUGHT" if is_catched else ("PAUSED" if self.paused else "RUNNING")
        s.setpos(-330, 295)
        s.write(f"Status: {status_txt}", font=UI["FONT"])
        s.setpos(70, 295)
        s.write(f"Time {int(remain)}s   Score {score}   Lv.{self.level}", font=UI["FONT"])

    #루프
    def start(self, init_dist=400):
        self.runner.setpos((-init_dist/2, 0)); self.runner.setheading(0)
        self.chaser.setpos((+init_dist/2, 0)); self.chaser.setheading(180)

        self.start_time = time.time()
        self.game_over = False
        self.paused = False
        self.score = 0

        self._draw_arena()
        self._draw_status_bar_static()
        self._draw_status_bar(False, self.time_limit_sec, self.score)
        self.canvas.update()  # tracer(0)일 때 초기 그리기 반영

        self.canvas.ontimer(self.step, self.ai_timer_msec)

    def step(self):
        if self.game_over or self.paused:
            return

        self.runner.run_ai(self.chaser.pos(), self.chaser.heading())
        self.chaser.run_ai(self.runner.pos(), self.runner.heading())

        self._clamp_inside(self.runner)
        self._clamp_inside(self.chaser)

        catched = self.is_catched()
        elapsed = time.time() - self.start_time
        remain = max(0, self.time_limit_sec - elapsed)

        # 단계 가중 점수
        mult = SCORE_MULT.get(self.level, 1.0)
        self.score = int(elapsed * mult)

        self._draw_status_bar(catched, remain, self.score)

        if catched or remain <= 0:
            self.game_over = True
            self.drawer_status.setpos(-90, 0)
            end_msg = "Caught!" if catched else "Time Up!"
            self.drawer_status.write(f"{end_msg}\nFinal Score: {self.score}",
                                     align="left", font=("Arial", 16, "bold"))
            self.canvas.update()
            return

        self.canvas.ontimer(self.step, self.ai_timer_msec)
        self.canvas.update()  # 한 프레임 갱신

    #컨트롤
    def toggle_pause(self):
        if self.game_over:
            return
        self.paused = not self.paused
        elapsed = time.time() - self.start_time
        remain = max(0, self.time_limit_sec - elapsed)
        self._draw_status_bar(False, remain, self.score)
        if not self.paused:
            self.canvas.ontimer(self.step, self.ai_timer_msec)
        self.canvas.update()

    def set_level(self, level:int):
        """난이도 적용: 추격자 속도/회전/틱 주기 변경 + 상태 텍스트 반영"""
        self.level = max(1, min(5, int(level)))
        cfg = DIFF_CFG[self.level]
        self.chaser.step_move = cfg["move"]
        self.chaser.step_turn = cfg["turn"]
        self.ai_timer_msec = cfg["timer"]
        #성태표시: caught인지 아닌지
        if self.start_time is not None and not self.game_over:
            elapsed = time.time() - self.start_time
            remain = max(0, self.time_limit_sec - elapsed)
            self._draw_status_bar(False, remain, self.score)
            self.canvas.update()

class ManualMover(turtle.RawTurtle):
    def __init__(self, canvas, step_move=10, step_turn=10):
        super().__init__(canvas)
        self.step_move = step_move
        self.step_turn = step_turn
        canvas.onkey(lambda: self.forward(self.step_move), 'Up')
        canvas.onkey(lambda: self.backward(self.step_move), 'Down')
        canvas.onkey(lambda: self.left(self.step_turn), 'Left')
        canvas.onkey(lambda: self.right(self.step_turn), 'Right')
        canvas.listen()
    def run_ai(self, opp_pos, opp_heading): pass

class ChaseMover(turtle.RawTurtle):
    def __init__(self, canvas, step_move=10, step_turn=10):
        super().__init__(canvas)
        self.step_move = step_move
        self.step_turn = step_turn
    def run_ai(self, opp_pos, opp_heading):
        target = self.towards(opp_pos)
        current = self.heading()
        turn = (target - current + 540) % 360 - 180
        if turn > 0: self.left(min(self.step_turn, turn))
        else:        self.right(min(self.step_turn, -turn))
        self.forward(self.step_move)

#엔트리 포인트
if __name__ == '__main__':
    root = tk.Tk()
    root.title("Turtle Runaway")
    canvas_widget = tk.Canvas(root, width=700, height=700)
    canvas_widget.pack()

    screen = turtle.TurtleScreen(canvas_widget)
    screen.bgcolor(UI["BG"])

    # 깜빡임 줄이기, 수동 갱신 모드
    screen.tracer(0)

    #포커스, 키
    canvas_widget.focus_set()
    screen.listen()
    root.after(100, canvas_widget.focus_set)
    root.bind("<FocusIn>", lambda e: canvas_widget.focus_set())

    #도망
    runner = ManualMover(screen, step_move=12, step_turn=15)   # 러너 고정
    chaser = ChaseMover(screen,  step_move=DIFF_CFG[1]["move"], step_turn=DIFF_CFG[1]["turn"])

    game = RunawayGame(screen, runner, chaser,
                       catch_radius=50, time_limit_sec=30, ai_timer_msec=DIFF_CFG[1]["timer"])

    #버튼바
    controls = tk.Frame(root); controls.pack(pady=6)
    tk.Button(controls, text="Start", command=game.start).pack(side="left", padx=4)
    tk.Button(controls, text="Pause/Resume", command=game.toggle_pause).pack(side="left", padx=4)
    tk.Button(controls, text="Restart", command=game.start).pack(side="left", padx=4)

    #난이도 선택
    diff_frame = tk.Frame(root); diff_frame.pack(pady=2)
    tk.Label(diff_frame, text="Difficulty:").pack(side="left")
    diff_var = tk.IntVar(value=1)
    def on_set_diff():
        game.set_level(diff_var.get())
    for lv in range(1, 6):
        tk.Radiobutton(diff_frame, text=str(lv), variable=diff_var, value=lv,
                       command=on_set_diff).pack(side="left", padx=2)

    #단축키
    screen.onkey(game.toggle_pause, "p")
    screen.onkey(game.start, "r")

    #Tk에도 방향키 보강 (포커스 유실 대비)
    root.bind_all("<Up>",    lambda e: runner.forward(runner.step_move))
    root.bind_all("<Down>",  lambda e: runner.backward(runner.step_move))
    root.bind_all("<Left>",  lambda e: runner.left(runner.step_turn))
    root.bind_all("<Right>", lambda e: runner.right(runner.step_turn))


    screen.mainloop()
