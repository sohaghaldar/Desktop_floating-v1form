# -*- coding: utf-8 -*-
"""
Desktop Pet Ecosystem - Custom Dark Neon UI Widgets
"""

import tkinter as tk
from core.config import IS_WINDOWS

class ModernSlider(tk.Frame):
    """
    Sleek Futuristic / Cyber Dark UI Slider Widget.
    Features:
    - Glowing smooth progress bar (height 6px)
    - Glowing circular neon knob with white border and outer aura
    - Quick micro-stepper [-] and [+] buttons with responsive hover feedback, packed left & right so NEVER clipped
    - Live numeric value badge displayed directly ABOVE the slider (e.g. 1.05x, 6.0 px/s, 30s)
    - Zero lag: live in-memory updates on drag (<B1-Motion>), disk commit only on release (<ButtonRelease-1>)
    - Supports click-to-jump, drag-to-slide, and mouse wheel
    - 100% custom drawn on Canvas - ZERO retro Tkinter bevels!
    """
    def __init__(self, parent, from_=0.0, to=100.0, initial=50.0, step=1.0, 
                 is_int=False, unit="", command=None, on_commit=None, bg="#131c2e", 
                 accent="#00f5d4", bar_color="#0284c7", track_bg="#090d16"):
        super().__init__(parent, bg=bg)
        self.from_ = float(from_)
        self.to = float(to)
        self.step = float(step)
        self.is_int = is_int
        self.unit = unit
        self.command = command
        self.on_commit = on_commit
        self.accent = accent
        self.bar_color = bar_color
        self.track_bg = track_bg
        
        self.val = float(initial)
        self.canvas_w = 260
        self.canvas_h = 24

        # Row 1: Header / Live Value Badge (Directly ABOVE the slider track, centered)
        val_row = tk.Frame(self, bg=bg)
        val_row.pack(fill="x", pady=(1, 2))
        self.lbl_value = tk.Label(val_row, text=self.format_value(), font=("Segoe UI", 10, "bold"),
                                  fg=self.accent, bg=bg)
        self.lbl_value.pack(anchor="center")

        # Row 2: Control Row ([-] on left, [+] on right, Canvas in the middle)
        control_row = tk.Frame(self, bg=bg)
        control_row.pack(fill="x", pady=(0, 2))

        # [-] Stepper Button
        self.btn_minus = tk.Label(control_row, text=" − ", font=("Segoe UI", 10, "bold"),
                                  fg="#94a3b8", bg="#090d16", cursor="hand2", padx=8, pady=1,
                                  relief="solid", bd=1)
        self.btn_minus.pack(side="left", padx=(0, 6))
        self.btn_minus.bind("<Button-1>", lambda e: self.step_value(-1))
        self.btn_minus.bind("<Enter>", lambda e: self.btn_minus.configure(fg="#38bdf8", bg="#1e293b"))
        self.btn_minus.bind("<Leave>", lambda e: self.btn_minus.configure(fg="#94a3b8", bg="#090d16"))

        # [+] Stepper Button (Packed to right FIRST so it NEVER gets pushed off screen)
        self.btn_plus = tk.Label(control_row, text=" + ", font=("Segoe UI", 10, "bold"),
                                 fg="#94a3b8", bg="#090d16", cursor="hand2", padx=8, pady=1,
                                 relief="solid", bd=1)
        self.btn_plus.pack(side="right", padx=(6, 0))
        self.btn_plus.bind("<Button-1>", lambda e: self.step_value(+1))
        self.btn_plus.bind("<Enter>", lambda e: self.btn_plus.configure(fg="#38bdf8", bg="#1e293b"))
        self.btn_plus.bind("<Leave>", lambda e: self.btn_plus.configure(fg="#94a3b8", bg="#090d16"))

        # Canvas Slider Track (Fills remaining horizontal space between buttons)
        self.canvas = tk.Canvas(control_row, height=self.canvas_h, bg=bg,
                                highlightthickness=0, cursor="hand2")
        self.canvas.pack(side="left", fill="x", expand=True)

        # Canvas events
        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<MouseWheel>", self._on_wheel)

        self.draw_slider()

    def format_value(self):
        if self.is_int:
            return f"{int(round(self.val))}{self.unit}"
        else:
            val_str = f"{self.val:.2f}"
            if val_str.endswith("0"):
                val_str = f"{self.val:.1f}"
            return f"{val_str}{self.unit}"

    def set(self, new_val):
        self.val = max(self.from_, min(self.to, float(new_val)))
        if self.is_int:
            self.val = round(self.val)
        self.draw_slider()

    def get(self):
        return int(round(self.val)) if self.is_int else float(self.val)

    def step_value(self, direction):
        new_val = self.val + direction * self.step
        self.set(new_val)
        if self.command:
            self.command(self.get())
        if self.on_commit:
            self.on_commit(self.get())

    def _on_wheel(self, event):
        direction = 1 if event.delta > 0 else -1
        self.step_value(direction)
        return "break"

    def _on_resize(self, event):
        self.canvas_w = event.width
        self.draw_slider()

    def _x_to_val(self, x):
        pad = 12
        usable_w = max(10, self.canvas_w - pad * 2)
        ratio = max(0.0, min(1.0, (x - pad) / usable_w))
        raw_val = self.from_ + ratio * (self.to - self.from_)
        steps = round((raw_val - self.from_) / self.step)
        val = self.from_ + steps * self.step
        return max(self.from_, min(self.to, val))

    def _val_to_x(self):
        pad = 12
        usable_w = max(10, self.canvas_w - pad * 2)
        ratio = (self.val - self.from_) / max(0.001, (self.to - self.from_))
        return pad + ratio * usable_w

    def _on_click(self, event):
        self.val = self._x_to_val(event.x)
        if self.is_int:
            self.val = round(self.val)
        self.draw_slider()
        if self.command:
            self.command(self.get())
        return "break"

    def _on_drag(self, event):
        new_val = self._x_to_val(event.x)
        if self.is_int:
            new_val = round(new_val)
        if new_val != self.val:
            self.val = new_val
            self.draw_slider()
            if self.command:
                self.command(self.get())
        return "break"

    def _on_release(self, event):
        if self.on_commit:
            self.on_commit(self.get())
        return "break"

    def draw_slider(self):
        self.canvas.delete("all")
        w = max(40, self.canvas_w)
        h = self.canvas_h
        cy = h / 2.0
        pad = 12
        track_h = 6

        # Dark Track Background
        self.canvas.create_rectangle(pad, cy - track_h/2, w - pad, cy + track_h/2,
                                     fill=self.track_bg, outline="#1e293b", width=1)

        # Progress Fill Bar
        thumb_x = self._val_to_x()
        if thumb_x > pad:
            self.canvas.create_rectangle(pad, cy - track_h/2, thumb_x, cy + track_h/2,
                                         fill=self.bar_color, outline="")

        # Glowing Knob / Thumb
        r = 7
        self.canvas.create_oval(thumb_x - r - 2, cy - r - 2, thumb_x + r + 2, cy + r + 2,
                                fill="", outline=self.accent, width=1)
        self.canvas.create_oval(thumb_x - r, cy - r, thumb_x + r, cy + r,
                                fill=self.accent, outline="#ffffff", width=1.5)

        # Update Live Value Badge (Above Slider)
        if hasattr(self, 'lbl_value') and self.lbl_value:
            self.lbl_value.configure(text=self.format_value())


class HotkeyRecorderButton(tk.Button):
    """
    Interactive Hotkey Recorder Widget.
    Replaces clumsy text entry boxes with an interactive key-capture button.
    When clicked, listens for real-time key combinations (Ctrl, Shift, Alt + Key)
    and formats them cleanly without any manual typing mistakes.
    """
    def __init__(self, master, initial_val="Shift+W", on_change=None, prompt_text="[Press Key...]", **kwargs):
        self.val = str(initial_val).strip() if initial_val else "Shift+W"
        self.on_change = on_change
        self.prompt_text = prompt_text
        self.recording = False
        
        # Default styling
        btn_kwargs = {
            "font": ("Segoe UI", 9, "bold"),
            "bg": "#090d16",
            "fg": "#38bdf8",
            "activebackground": "#0284c7",
            "activeforeground": "#ffffff",
            "relief": "solid",
            "bd": 1,
            "cursor": "hand2",
            "padx": 6,
            "pady": 2,
            "width": 11
        }
        btn_kwargs.update(kwargs)
        super().__init__(master, text=self.val, command=self.start_recording, **btn_kwargs)

    def start_recording(self):
        if self.recording:
            return
        self.recording = True
        self.configure(text=self.prompt_text, bg="#0369a1", fg="#ffffff")
        self.focus_set()
        self.bind("<KeyPress>", self._on_key_press)
        self.bind("<KeyRelease>", self._on_key_release)
        self.bind("<FocusOut>", self._on_focus_out)

    def _get_active_modifiers(self, event):
        mods = []
        sym = event.keysym.lower()
        if IS_WINDOWS:
            try:
                import ctypes
                u32 = ctypes.windll.user32
                # Use synchronized GetKeyState rather than asynchronous hardware state
                is_ctrl = bool((u32.GetKeyState(0x11) & 0x8000) or ("control" in sym) or (event.state & 0x0004))
                is_shift = bool((u32.GetKeyState(0x10) & 0x8000) or ("shift" in sym) or (event.state & 0x0001))
                is_alt = bool((u32.GetKeyState(0x12) & 0x8000) or ("alt" in sym) or (event.state & 0x20000) or (event.state & 0x0008))
                if is_ctrl:
                    mods.append("Ctrl")
                if is_shift:
                    mods.append("Shift")
                if is_alt:
                    mods.append("Alt")
                return mods
            except Exception:
                pass

        # Fallback for Linux / macOS
        if (event.state & 0x0004) or ("control" in sym):
            mods.append("Ctrl")
        if (event.state & 0x0001) or ("shift" in sym):
            mods.append("Shift")
        if (event.state & 0x0008) or ("alt" in sym):
            mods.append("Alt")
        return mods

    def _on_key_press(self, event):
        sym = event.keysym
        sym_lower = sym.lower()
        mods = self._get_active_modifiers(event)
        
        # Modifier-only press: show 'Ctrl + ...' or 'Shift + ...'
        if sym_lower in ["control_l", "control_r", "shift_l", "shift_r", "alt_l", "alt_r"]:
            if mods:
                self.configure(text=" + ".join(mods) + " + ...")
            return "break"

        # Normal key press:
        key_name = sym.upper()
        if sym_lower in ["grave", "asciitilde", "quoteleft"]:
            key_name = "`"
        elif sym_lower == "escape":
            if not mods:
                self.stop_recording(self.val)
                return "break"
            key_name = "ESC"
        elif sym_lower == "space":
            key_name = "SPACE"
        elif sym_lower in ["return", "enter"]:
            key_name = "ENTER"
        elif len(key_name) == 1:
            key_name = key_name.upper()

        # Build full combo string
        if mods:
            combo_mods = [m for m in ["Ctrl", "Shift", "Alt"] if m in mods]
            final_combo = "+".join(combo_mods + [key_name])
        else:
            final_combo = key_name

        self.stop_recording(final_combo)
        if self.on_change:
            self.on_change(final_combo)
        return "break"

    def _on_key_release(self, event):
        if self.recording:
            mods = self._get_active_modifiers(event)
            if mods:
                self.configure(text=" + ".join(mods) + " + ...")
            else:
                self.configure(text=self.prompt_text)

    def _on_focus_out(self, event):
        if self.recording:
            self.stop_recording(self.val)

    def stop_recording(self, final_val):
        self.recording = False
        self.val = str(final_val).strip()
        self.configure(text=self.val, bg="#090d16", fg="#38bdf8")
        self.unbind("<KeyPress>")
        self.unbind("<KeyRelease>")
        self.unbind("<FocusOut>")

    def get(self):
        return self.val

    def set(self, val):
        self.val = str(val).strip()
        self.configure(text=self.val)


