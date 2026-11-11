
import tkinter as tk
import random


class InfiniteMinesweeper:
    def __init__(self, root):
        self.root = root
        self.root.title("Infinite Minesweeper")
        self.root.geometry("800x630")
        self.root.minsize(500, 400)

        self.cell_size = 30
        self.chunk_size = 16
        self.mine_density = 0.15

        self.generated_chunks = {}
        self.revealed_cells = set()
        self.flagged_cells = set()

        self.first_click = True
        self.game_over = False

        self.offset_x = 0
        self.offset_y = 0

        self.last_drag_x = 0
        self.last_drag_y = 0
        self.dragging = False

        self.status = tk.Label(
            root,
            text="First click is safe! Left-click to reveal, "
                 "right-click to flag. Middle-drag or use arrow keys.",
            font=("Arial", 10),
            bg="#263238",
            fg="white",
            padx=5,
            pady=8
        )
        self.status.pack(side=tk.TOP, fill=tk.X)

        self.canvas = tk.Canvas(
            root,
            bg="#606060",
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.handle_left_click)
        self.canvas.bind("<ButtonPress-3>", self.handle_right_click)

        self.canvas.bind("<ButtonPress-2>", self.start_pan)
        self.canvas.bind("<B2-Motion>", self.pan_grid)
        self.canvas.bind("<ButtonRelease-2>", self.stop_pan)

        self.root.bind("<Up>", lambda e: self.move_camera(0, 60))
        self.root.bind("<Down>", lambda e: self.move_camera(0, -60))
        self.root.bind("<Left>", lambda e: self.move_camera(60, 0))
        self.root.bind("<Right>", lambda e: self.move_camera(-60, 0))

        self.root.bind("<r>", lambda e: self.reset_game())
        self.root.bind("<R>", lambda e: self.reset_game())

        self.canvas.bind("<Configure>", lambda e: self.redraw())

        self.root.after(100, self.redraw)

    def get_chunk_coords(self, x, y):
        return x // self.chunk_size, y // self.chunk_size

    def ensure_chunk(self, cx, cy, safe_zone=None):
        if (cx, cy) in self.generated_chunks:
            return

        chunk = {}
        rng = random.Random(f"infinite_mines_{cx}_{cy}")

        for lx in range(self.chunk_size):
            for ly in range(self.chunk_size):
                ax = cx * self.chunk_size + lx
                ay = cy * self.chunk_size + ly

                is_safe = safe_zone is not None and (ax, ay) in safe_zone

                chunk[(ax, ay)] = {
                    "mine": False if is_safe else (
                        rng.random() < self.mine_density
                    ),
                    "count": 0
                }

        self.generated_chunks[(cx, cy)] = chunk

        # Recalculate this chunk and existing neighbouring chunks.
        for ncx in range(cx - 1, cx + 2):
            for ncy in range(cy - 1, cy + 2):
                if (ncx, ncy) in self.generated_chunks:
                    self.recalculate_chunk(ncx, ncy)

    def recalculate_chunk(self, cx, cy):
        chunk = self.generated_chunks[(cx, cy)]

        for (x, y), cell in chunk.items():
            if cell["mine"]:
                cell["count"] = 0
                continue

            count = 0

            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue

                    nx = x + dx
                    ny = y + dy
                    ncx, ncy = self.get_chunk_coords(nx, ny)

                    if (ncx, ncy) in self.generated_chunks:
                        neighbour = self.generated_chunks[
                            (ncx, ncy)
                        ].get((nx, ny))

                        if neighbour and neighbour["mine"]:
                            count += 1

            cell["count"] = count

    def get_cell(self, x, y):
        cx, cy = self.get_chunk_coords(x, y)
        self.ensure_chunk(cx, cy)
        return self.generated_chunks[(cx, cy)][(x, y)]

    def generate_safe_start(self, x, y):
        safe_zone = {
            (x + dx, y + dy)
            for dx in (-1, 0, 1)
            for dy in (-1, 0, 1)
        }

        cx, cy = self.get_chunk_coords(x, y)

        # Regenerate nearby chunks to guarantee the safe zone.
        for ncx in range(cx - 1, cx + 2):
            for ncy in range(cy - 1, cy + 2):
                self.generated_chunks.pop((ncx, ncy), None)

        for ncx in range(cx - 1, cx + 2):
            for ncy in range(cy - 1, cy + 2):
                self.ensure_chunk(ncx, ncy, safe_zone)

        self.first_click = False

    def screen_to_grid(self, event):
        x = int((event.x - self.offset_x) // self.cell_size)
        y = int((event.y - self.offset_y) // self.cell_size)
        return x, y

    def handle_left_click(self, event):
        if self.game_over:
            return

        x, y = self.screen_to_grid(event)

        if (x, y) in self.flagged_cells:
            return

        if self.first_click:
            self.generate_safe_start(x, y)

        cell = self.get_cell(x, y)

        if cell["mine"]:
            self.game_over = True
            self.status.config(
                text="BOOM! You hit a mine! Restarting..."
            )
            self.redraw()
            self.root.after(1500, self.reset_game)
            return

        self.reveal_recursive(x, y)
        self.redraw()

    def reveal_recursive(self, x, y):
        # Use a stack to avoid Python's recursion-depth limit.
        stack = [(x, y)]

        while stack:
            ax, ay = stack.pop()

            if (ax, ay) in self.revealed_cells:
                continue

            if (ax, ay) in self.flagged_cells:
                continue

            cell = self.get_cell(ax, ay)

            if cell["mine"]:
                continue

            self.revealed_cells.add((ax, ay))

            if cell["count"] == 0:
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue

                        nx, ny = ax + dx, ay + dy

                        if (nx, ny) not in self.revealed_cells:
                            if (nx, ny) not in self.flagged_cells:
                                stack.append((nx, ny))

    def handle_right_click(self, event):
        if self.game_over:
            return

        x, y = self.screen_to_grid(event)

        if (x, y) in self.revealed_cells:
            return

        if (x, y) in self.flagged_cells:
            self.flagged_cells.remove((x, y))
        else:
            self.flagged_cells.add((x, y))

        self.redraw()

    def start_pan(self, event):
        self.dragging = True
        self.last_drag_x = event.x
        self.last_drag_y = event.y

    def pan_grid(self, event):
        if not self.dragging:
            return

        dx = event.x - self.last_drag_x
        dy = event.y - self.last_drag_y

        self.offset_x += dx
        self.offset_y += dy

        self.last_drag_x = event.x
        self.last_drag_y = event.y

        self.redraw()

    def stop_pan(self, event):
        self.dragging = False

    def move_camera(self, dx, dy):
        self.offset_x += dx
        self.offset_y += dy
        self.redraw()

    def reset_game(self):
        self.generated_chunks.clear()
        self.revealed_cells.clear()
        self.flagged_cells.clear()

        self.first_click = True
        self.game_over = False

        self.offset_x = 0
        self.offset_y = 0
        self.dragging = False

        self.status.config(
            text="New board! Left-click to reveal, "
                 "right-click to flag. Explore infinitely!"
        )

        self.redraw()

    def draw_flag(self, x1, y1, x2, y2):
        # Draw a flag using shapes for better font compatibility.
        pole_x = x1 + self.cell_size * 0.43
        pole_top = y1 + self.cell_size * 0.22
        pole_bottom = y1 + self.cell_size * 0.78

        self.canvas.create_line(
            pole_x, pole_top, pole_x, pole_bottom,
            fill="#333333", width=2
        )

        self.canvas.create_polygon(
            pole_x, pole_top,
            pole_x + self.cell_size * 0.36,
            pole_top + self.cell_size * 0.12,
            pole_x, pole_top + self.cell_size * 0.32,
            fill="#e53935", outline="#b71c1c"
        )

        self.canvas.create_line(
            pole_x - 4, pole_bottom,
            pole_x + 5, pole_bottom,
            fill="#333333", width=2
        )

    def redraw(self):
        if not hasattr(self, "canvas"):
            return

        self.canvas.delete("all")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width <= 1 or height <= 1:
            return

        size = self.cell_size

        start_x = int((-self.offset_x) // size) - 1
        end_x = int((width - self.offset_x) // size) + 1

        start_y = int((-self.offset_y) // size) - 1
        end_y = int((height - self.offset_y) // size) + 1

        # Generate the chunks needed for the visible area.
        for gx in range(start_x, end_x):
            for gy in range(start_y, end_y):
                cx, cy = self.get_chunk_coords(gx, gy)
                self.ensure_chunk(cx, cy)

        number_colors = {
            1: "#1565c0",
            2: "#2e7d32",
            3: "#d32f2f",
            4: "#4527a0",
            5: "#880e4f",
            6: "#00838f",
            7: "#212121",
            8: "#616161"
        }

        for gx in range(start_x, end_x):
            for gy in range(start_y, end_y):
                cell = self.get_cell(gx, gy)

                x1 = gx * size + self.offset_x
                y1 = gy * size + self.offset_y
                x2 = x1 + size
                y2 = y1 + size

                if (gx, gy) in self.revealed_cells:
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill="#d0d0d0",
                        outline="#999999"
                    )

                    if cell["count"] > 0:
                        self.canvas.create_text(
                            x1 + size / 2,
                            y1 + size / 2,
                            text=str(cell["count"]),
                            fill=number_colors.get(
                                cell["count"], "black"
                            ),
                            font=("Arial", 12, "bold")
                        )

                else:
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill="#bdbdbd",
                        outline="#777777",
                        width=1
                    )

                    # Raised-tile effect.
                    self.canvas.create_line(
                        x1 + 1, y1 + 1,
                        x2 - 1, y1 + 1,
                        fill="white", width=2
                    )

                    self.canvas.create_line(
                        x1 + 1, y1 + 1,
                        x1 + 1, y2 - 1,
                        fill="white", width=2
                    )

                    self.canvas.create_line(
                        x1 + 1, y2 - 1,
                        x2 - 1, y2 - 1,
                        fill="#777777", width=2
                    )

                    self.canvas.create_line(
                        x2 - 1, y1 + 1,
                        x2 - 1, y2 - 1,
                        fill="#777777", width=2
                    )

                    if (gx, gy) in self.flagged_cells:
                        self.draw_flag(x1, y1, x2, y2)

                    elif self.game_over and cell["mine"]:
                        self.canvas.create_oval(
                            x1 + 7, y1 + 7,
                            x2 - 7, y2 - 7,
                            fill="black", outline="black"
                        )


if __name__ == "__main__":
    window = tk.Tk()
    app = InfiniteMinesweeper(window)
    window.mainloop()
