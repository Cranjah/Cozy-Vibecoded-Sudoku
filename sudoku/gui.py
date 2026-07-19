#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Tkinter GUI for Sudoku with difficulty (Leicht, Mittel, Schwer), timer, import/export, stepwise solving

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import time
from typing import Optional, List
from sudoku import (
    generate_puzzle,
    solve,
    solve_steps,
    export_grid,
    import_grid,
    copy_grid,
    is_complete,
)

BG_MAIN = "#F5F5F7"
BG_BOARD = "#FFFFFF"
BG_BOX = "#E0E0E0"
FG_TEXT = "#222222"
FG_GIVEN = "#006D77"
FG_SOLVER = "#FF6F61"
BTN_BG = "#FFFFFF"
BTN_FG = "#222222"
BTN_ACTIVE = "#D0E8F2"
FONT_UI = ("Segoe UI", 11)
FONT_CELL = ("Segoe UI", 16)

DIFFICULTY_TO_CLUES = {
    "Leicht": 36,
    "Mittel": 32,
    "Schwer": 28,
}


class SudokuGUI:
    def __init__(self, master: tk.Tk):
        self.master = master
        master.title("Sudoku – Generator & Solver")
        master.configure(bg=BG_MAIN)

        self.timer_running = False
        self.start_time = 0.0
        self.timer_id: Optional[str] = None

        self.entries: List[List[tk.Entry]] = [
            [None for _ in range(9)] for _ in range(9)
        ]
        self.puzzle: Optional[List[List[int]]] = None
        self.solver_steps = None
        self.step_delay_ms = 120

        top = tk.Frame(master, bg=BG_MAIN)
        top.pack(padx=12, pady=8, fill="x")
        tk.Label(top, text="Schwierigkeit:", bg=BG_MAIN, fg=FG_TEXT, font=FONT_UI).pack(
            side="left"
        )
        self.diff_var = tk.StringVar(value="Mittel")
        self.diff_menu = ttk.Combobox(
            top,
            textvariable=self.diff_var,
            values=list(DIFFICULTY_TO_CLUES.keys()),
            state="readonly",
        )
        self.diff_menu.pack(side="left", padx=8)

        self.timer_label = tk.Label(
            top, text="00:00", bg=BG_MAIN, fg=FG_TEXT, font=("Segoe UI", 13)
        )
        self.timer_label.pack(side="right")

        board_outer = tk.Frame(master, bg=BG_BOX, bd=4, relief="ridge")
        board_outer.pack(padx=16, pady=10)

        self.box_frames = []
        for br in range(3):
            row_frames = []
            for bc in range(3):
                box = tk.Frame(board_outer, bg=BG_BOARD, bd=2, relief="groove")
                box.grid(row=br, column=bc, padx=4, pady=4)
                row_frames.append(box)
            self.box_frames.append(row_frames)

        for br in range(3):
            for bc in range(3):
                box = self.box_frames[br][bc]
                for r in range(3):
                    for c in range(3):
                        rr = br * 3 + r
                        cc = bc * 3 + c
                        e = tk.Entry(
                            box,
                            width=2,
                            font=FONT_CELL,
                            justify="center",
                            bg=BG_BOARD,
                            fg=FG_TEXT,
                            bd=1,
                            relief="solid",
                            disabledbackground=BG_BOARD,
                            disabledforeground=FG_GIVEN,
                        )
                        e.grid(row=r, column=c, padx=2, pady=2)
                        e.bind("<KeyRelease>", self._sanitize_entry)
                        self.entries[rr][cc] = e

        btns = tk.Frame(master, bg=BG_MAIN)
        btns.pack(padx=12, pady=8)
        self.btn_new = tk.Button(
            btns,
            text="Neues Sudoku",
            command=self.new_puzzle,
            bg=BTN_BG,
            fg=BTN_FG,
            font=FONT_UI,
            relief="flat",
            width=14,
            activebackground=BTN_ACTIVE,
        )
        self.btn_new.pack(side="left", padx=6)

        self.btn_solve_step = tk.Button(
            btns,
            text="Schrittweise lösen",
            command=self.solve_stepwise,
            bg=BTN_BG,
            fg=BTN_FG,
            font=FONT_UI,
            relief="flat",
            width=16,
            activebackground=BTN_ACTIVE,
        )
        self.btn_solve_step.pack(side="left", padx=6)

        self.btn_solve_all = tk.Button(
            btns,
            text="Sofort lösen",
            command=self.solve_all,
            bg=BTN_BG,
            fg=BTN_FG,
            font=FONT_UI,
            relief="flat",
            width=14,
            activebackground=BTN_ACTIVE,
        )
        self.btn_solve_all.pack(side="left", padx=6)

        self.btn_reset = tk.Button(
            btns,
            text="Zurücksetzen",
            command=self.clear_grid,
            bg=BTN_BG,
            fg=BTN_FG,
            font=FONT_UI,
            relief="flat",
            width=12,
            activebackground=BTN_ACTIVE,
        )
        self.btn_reset.pack(side="left", padx=6)

        self.btn_export = tk.Button(
            btns,
            text="Exportieren",
            command=self.export_current,
            bg=BTN_BG,
            fg=BTN_FG,
            font=FONT_UI,
            relief="flat",
            width=12,
            activebackground=BTN_ACTIVE,
        )
        self.btn_export.pack(side="left", padx=6)

        self.btn_import = tk.Button(
            btns,
            text="Importieren",
            command=self.import_from_file,
            bg=BTN_BG,
            fg=BTN_FG,
            font=FONT_UI,
            relief="flat",
            width=12,
            activebackground=BTN_ACTIVE,
        )
        self.btn_import.pack(side="left", padx=6)

        self.new_puzzle()

    def _sanitize_entry(self, event):
        e: tk.Entry = event.widget
        txt = e.get()
        if not txt:
            return
        if not txt[-1].isdigit():
            e.delete(0, tk.END)
            return
        d = txt[-1]
        if d == "0":
            e.delete(0, tk.END)
            return
        if d not in "123456789":
            e.delete(0, tk.END)
            return
        e.delete(0, tk.END)
        e.insert(0, d)

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.start_time = time.time()
            self.update_timer()

    def stop_timer(self):
        self.timer_running = False
        if self.timer_id:
            self.master.after_cancel(self.timer_id)
            self.timer_id = None

    def reset_timer(self):
        self.stop_timer()
        self.timer_label.config(text="00:00")

    def update_timer(self):
        if not self.timer_running:
            return
        elapsed = int(time.time() - self.start_time)
        mm = elapsed // 60
        ss = elapsed % 60
        self.timer_label.config(text=f"{mm:02d}:{ss:02d}")
        self.timer_id = self.master.after(500, self.update_timer)

    def display_grid(self, grid):
        for r in range(9):
            for c in range(9):
                val = grid[r][c]
                e = self.entries[r][c]
                e.delete(0, tk.END)
                if val != 0:
                    e.insert(0, str(val))
                    e.config(fg=FG_GIVEN)
                    e.config(state="normal")
                else:
                    e.config(fg=FG_TEXT)
                    e.config(state="normal")

    def get_user_grid(self) -> List[List[int]]:
        grid = [[0 for _ in range(9)] for _ in range(9)]
        for r in range(9):
            for c in range(9):
                val = self.entries[r][c].get()
                grid[r][c] = int(val) if (val.isdigit() and val != "0") else 0
        return grid

    def set_cell(self, r: int, c: int, val: int, color: Optional[str] = None):
        e = self.entries[r][c]
        e.delete(0, tk.END)
        if val != 0:
            e.insert(0, str(val))
        e.config(fg=color or FG_TEXT)

    def clear_grid(self):
        self.stop_animation()
        for r in range(9):
            for c in range(9):
                self.entries[r][c].config(state="normal", fg=FG_TEXT)
                self.entries[r][c].delete(0, tk.END)
        self.reset_timer()

    def new_puzzle(self):
        self.stop_animation()
        self.reset_timer()
        difficulty = self.diff_var.get()
        min_clues = DIFFICULTY_TO_CLUES.get(difficulty, 32)
        self.puzzle = generate_puzzle(min_clues=min_clues, symmetry=True)
        self.display_grid(self.puzzle)
        self.start_timer()

    def solve_all(self):
        self.stop_animation()
        grid = self.get_user_grid()
        ok, sol, _ = solve(grid)
        if ok and sol:
            self.display_grid(sol)
            self.stop_timer()
            messagebox.showinfo("Sudoku", "Sudoku gelöst.")
        else:
            messagebox.showwarning("Sudoku", "Keine Lösung gefunden.")

    def solve_stepwise(self):
        self.stop_animation()
        user_grid = self.get_user_grid()
        self.solver_steps = solve_steps(user_grid)
        self.animate_next_step()

    def animate_next_step(self):
        if self.solver_steps is None:
            return
        try:
            r, c, v = next(self.solver_steps)
            self.set_cell(r, c, v, color=FG_SOLVER)
            self.anim_id = self.master.after(self.step_delay_ms, self.animate_next_step)
        except StopIteration:
            self.solver_steps = None
            final = self.get_user_grid()
            if is_complete(final):
                self.stop_timer()
                messagebox.showinfo("Sudoku", "Schrittweise Lösung abgeschlossen.")
            else:
                messagebox.showinfo(
                    "Sudoku",
                    "Keine weitere Schritte. Prüfe manuell oder 'Sofort lösen'.",
                )

    def stop_animation(self):
        if hasattr(self, "anim_id") and self.anim_id:
            self.master.after_cancel(self.anim_id)
            self.anim_id = None
        self.solver_steps = None

    def export_current(self):
        grid = self.get_user_grid()
        path = filedialog.asksaveasfilename(
            title="Sudoku exportieren",
            defaultextension=".sdk",
            filetypes=[("Sudoku-Datei", "*.sdk"), ("Text", "*.txt")],
        )
        if not path:
            return
        try:
            export_grid(grid, path)
            messagebox.showinfo("Export", "Sudoku erfolgreich exportiert.")
        except Exception as e:
            messagebox.showerror("Export", f"Fehler beim Export: {e}")

    def import_from_file(self):
        self.stop_animation()
        path = filedialog.askopenfilename(
            title="Sudoku importieren",
            filetypes=[
                ("Sudoku-Datei", "*.sdk"),
                ("Text", "*.txt"),
                ("Alle Dateien", "*.*"),
            ],
        )
        if not path:
            return
        try:
            g = import_grid(path)
            self.display_grid(g)
            self.reset_timer()
            self.start_timer()
        except Exception as e:
            messagebox.showerror("Import", f"Fehler beim Import: {e}")


if __name__ == "__main__":
    root = tk.Tk()

    try:
        style = ttk.Style()
        style.theme_use("clam")
    except Exception:
        pass
    app = SudokuGUI(root)
    root.mainloop()
