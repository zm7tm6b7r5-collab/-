import tkinter as tk
import math
import winsound

WORK_SEC = 25 * 60
BREAK_SEC = 5 * 60

COLOR_WORK = "#e74c3c"
COLOR_BREAK = "#2ecc71"
BG = "#1a1a2e"
SURFACE = "#16213e"
TEXT = "#eeeeee"
TEXT_DIM = "#888888"
RING_BG = "rgba(255,255,255,0.08)"  # fallback: use hex


class Pomodoro:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("番茄钟")
        self.window.geometry("400x520")
        self.window.resizable(False, False)
        self.window.configure(bg=BG)

        # State
        self.status = "idle"  # idle | running | paused
        self.mode = "work"  # work | break
        self.remaining = WORK_SEC
        self.after_id = None

        self._build_ui()
        self._draw_ring(1.0)

    def _build_ui(self):
        # Canvas for ring + time
        self.canvas = tk.Canvas(
            self.window, width=260, height=260,
            bg=BG, highlightthickness=0
        )
        self.canvas.pack(pady=(60, 20))

        # Mode label
        self.mode_label = tk.Label(
            self.window, text="专注", font=("Microsoft YaHei", 12, "bold"),
            bg=BG, fg=COLOR_WORK
        )
        self.mode_label.place(relx=0.5, y=98, anchor="center")

        # Time label (overlaid on canvas center)
        self.time_label = tk.Label(
            self.window, text="25:00", font=("Consolas", 48, "normal"),
            bg=BG, fg=TEXT
        )
        self.time_label.place(relx=0.5, y=175, anchor="center")

        # Status label
        self.status_label = tk.Label(
            self.window, text="准备开始", font=("Microsoft YaHei", 9),
            bg=BG, fg=TEXT_DIM
        )
        self.status_label.place(relx=0.5, y=215, anchor="center")

        # Button area
        btn_frame = tk.Frame(self.window, bg=BG)
        btn_frame.pack(pady=30)

        self.start_btn = tk.Button(
            btn_frame, text="开始", font=("Microsoft YaHei", 11),
            bg=COLOR_WORK, fg="#fff", activebackground="#c0392b",
            activeforeground="#fff", relief="flat", cursor="hand2",
            padx=30, pady=8, borderwidth=0,
            command=self._on_start
        )
        self.start_btn.pack(side="left", padx=8)

        self.reset_btn = tk.Button(
            btn_frame, text="重置", font=("Microsoft YaHei", 11),
            bg=SURFACE, fg=TEXT_DIM, activebackground="#1a1a3e",
            activeforeground=TEXT, relief="flat", cursor="hand2",
            padx=30, pady=8, borderwidth=0,
            command=self._on_reset, state="disabled"
        )
        self.reset_btn.pack(side="left", padx=8)

        # Round corners on buttons via config
        for btn in [self.start_btn, self.reset_btn]:
            btn.configure(
                borderwidth=0,
                highlightthickness=0,
            )

    # ---- ring drawing ----
    def _draw_ring(self, progress):
        self.canvas.delete("ring")
        cx, cy, r, sw = 130, 130, 105, 5

        A = (2 * math.pi / 360)

        # Background ring
        self._create_circle_arc(cx, cy, r, sw, 0, 360, "#2a2a4a", "ring")

        # Progress arc (clockwise from top)
        if progress > 0:
            extent = progress * 360
            color = COLOR_WORK if self.mode == "work" else COLOR_BREAK
            self._create_circle_arc(cx, cy, r, sw, 90, 90 - extent, color, "ring")

    def _create_circle_arc(self, cx, cy, r, sw, start, extent, color, tag):
        """Draw an arc on the canvas. start in degrees, extent in degrees (clockwise)."""
        A = (2 * math.pi) / 360
        points = []
        steps = max(2, int(abs(extent) * 2))
        for i in range(steps + 1):
            angle_deg = start - (extent * i / steps)
            angle_rad = angle_deg * A
            x = cx + r * math.cos(angle_rad)
            y = cy - r * math.sin(angle_rad)
            points.extend([x, y])
        if len(points) >= 4:
            self.canvas.create_line(points, width=sw, fill=color,
                                    capstyle="round", tags=tag)

    # ---- timer logic ----
    def _on_start(self):
        if self.status == "idle":
            self.status = "running"
        elif self.status == "paused":
            self.status = "running"

        self.start_btn.configure(text="暂停", bg="#f39c12", command=self._on_pause)
        self.reset_btn.configure(state="normal")
        self.status_label.configure(text="")
        self._tick()

    def _on_pause(self):
        self.status = "paused"
        if self.after_id:
            self.window.after_cancel(self.after_id)
            self.after_id = None
        self.start_btn.configure(text="继续", bg=COLOR_WORK, command=self._on_start)
        self.status_label.configure(text="已暂停")

    def _on_reset(self):
        self.status = "idle"
        self.mode = "work"
        self.remaining = WORK_SEC
        if self.after_id:
            self.window.after_cancel(self.after_id)
            self.after_id = None

        self.start_btn.configure(text="开始", bg=COLOR_WORK, command=self._on_start)
        self.reset_btn.configure(state="disabled")
        self.mode_label.configure(text="专注", fg=COLOR_WORK)
        self.time_label.configure(text="25:00")
        self.status_label.configure(text="准备开始")
        self.window.configure(bg=BG)
        self._draw_ring(1.0)

    def _tick(self):
        if self.status != "running":
            return

        if self.remaining <= 0:
            self._on_complete()
            return

        self.remaining -= 1
        total = WORK_SEC if self.mode == "work" else BREAK_SEC
        progress = self.remaining / total
        self._draw_ring(progress)
        self._update_time_label()

        self.after_id = self.window.after(1000, self._tick)

    def _on_complete(self):
        self.status = "idle"
        if self.after_id:
            self.window.after_cancel(self.after_id)
            self.after_id = None

        # Beep
        try:
            winsound.Beep(1000, 300)
        except Exception:
            pass

        # Switch mode
        if self.mode == "work":
            self.mode = "break"
            self.remaining = BREAK_SEC
            self.mode_label.configure(text="休息", fg=COLOR_BREAK)
            self.status_label.configure(text="工作时间结束，休息一下吧！")
        else:
            self.mode = "work"
            self.remaining = WORK_SEC
            self.mode_label.configure(text="专注", fg=COLOR_WORK)
            self.status_label.configure(text="休息结束，开始专注！")

        self.time_label.configure(text=self._fmt(self.remaining))
        self._draw_ring(1.0)
        self.start_btn.configure(text="开始", bg=COLOR_WORK, command=self._on_start)
        self.reset_btn.configure(state="disabled")

    # ---- helpers ----
    def _update_time_label(self):
        self.time_label.configure(text=self._fmt(self.remaining))

    @staticmethod
    def _fmt(seconds):
        m = seconds // 60
        s = seconds % 60
        return f"{m:02d}:{s:02d}"

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    Pomodoro().run()
