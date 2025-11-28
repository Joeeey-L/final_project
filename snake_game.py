# snake_game.py
from tkinter import *
import random

WIDTH = 500
HEIGHT = 500
SPEED = 200
SPACE_SIZE = 20
BODY_SIZE = 2
SNAKE_COLOR = "#00FF00"
FOOD_COLOR = "#FFFFFF"
BG_COLOR = "#000000"


class SnakeGame:
    def __init__(self, master):
        """
        master: 父窗口，通常是 GUI.Window
        """
        self.gamewin = Toplevel(master)
        self.gamewin.title("Snake Game")
        self.gamewin.resizable(False, False)

        # --- game variables ---
        self.score = 0
        self.direction = "down"

        # Score Label
        self.label = Label(self.gamewin, text=f"Points: {self.score}", font=("consolas", 20))
        self.label.pack()

        # Canvas
        self.canvas = Canvas(self.gamewin, bg=BG_COLOR, width=WIDTH, height=HEIGHT)
        self.canvas.pack()

        # Center window
        self.gamewin.update()
        w = self.gamewin.winfo_width()
        h = self.gamewin.winfo_height()
        sw = self.gamewin.winfo_screenwidth()
        sh = self.gamewin.winfo_screenheight()
        x = int((sw - w) / 2)
        y = int((sh - h) / 2)
        self.gamewin.geometry(f"{w}x{h}+{x}+{y}")

        # Snake & Food
        self.snake = Snake(self.canvas)
        self.food = Food(self.canvas)

        # Key bindings
        self.gamewin.bind('<Left>', lambda e: self.change_direction("left"))
        self.gamewin.bind('<Right>', lambda e: self.change_direction("right"))
        self.gamewin.bind('<Up>', lambda e: self.change_direction("up"))
        self.gamewin.bind('<Down>', lambda e: self.change_direction("down"))

        # Start game loop
        self.next_turn()

    # ------------------------
    #   GAME LOOP
    # ------------------------
    def next_turn(self):
        x, y = self.snake.coordinates[0]

        if self.direction == "up":
            y -= SPACE_SIZE
        elif self.direction == "down":
            y += SPACE_SIZE
        elif self.direction == "left":
            x -= SPACE_SIZE
        elif self.direction == "right":
            x += SPACE_SIZE

        # Insert new head
        self.snake.coordinates.insert(0, (x, y))
        square = self.canvas.create_rectangle(
            x, y, x + SPACE_SIZE, y + SPACE_SIZE,
            fill=SNAKE_COLOR
        )
        self.snake.squares.insert(0, square)

        # Eat food
        if x == self.food.coordinates[0] and y == self.food.coordinates[1]:
            self.score += 1
            self.label.config(text=f"Points: {self.score}")
            self.canvas.delete("food")
            self.food = Food(self.canvas)

        else:
            # Remove tail
            self.canvas.delete(self.snake.squares[-1])
            del self.snake.squares[-1]
            del self.snake.coordinates[-1]

        # Check game over
        if self.check_collisions():
            self.game_over()
        else:
            self.gamewin.after(SPEED, self.next_turn)

    # ------------------------
    #   DIRECTION CONTROL
    # ------------------------
    def change_direction(self, new):
        if new == "left" and self.direction != "right":
            self.direction = new
        elif new == "right" and self.direction != "left":
            self.direction = new
        elif new == "up" and self.direction != "down":
            self.direction = new
        elif new == "down" and self.direction != "up":
            self.direction = new

    # ------------------------
    #   COLLISION CHECK
    # ------------------------
    def check_collisions(self):
        x, y = self.snake.coordinates[0]

        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            return True

        for body in self.snake.coordinates[1:]:
            if x == body[0] and y == body[1]:
                return True

        return False

    # ------------------------
    #   GAME OVER
    # ------------------------
    def game_over(self):
        self.canvas.delete(ALL)
        self.canvas.create_text(
            WIDTH/2, HEIGHT/2,
            text="GAME OVER",
            fill="red",
            font=("consolas", 50)
        )


# ------------------------
#   SNAKE CLASS
# ------------------------
class Snake:
    def __init__(self, canvas):
        self.coordinates = [[0, 0]] * BODY_SIZE
        self.squares = []

        for x, y in self.coordinates:
            square = canvas.create_rectangle(
                x, y, x + SPACE_SIZE, y + SPACE_SIZE,
                fill=SNAKE_COLOR, tag="snake"
            )
            self.squares.append(square)


# ------------------------
#   FOOD CLASS
# ------------------------
class Food:
    def __init__(self, canvas):
        x = random.randint(0, (WIDTH / SPACE_SIZE) - 1) * SPACE_SIZE
        y = random.randint(0, (HEIGHT / SPACE_SIZE) - 1) * SPACE_SIZE
        self.coordinates = [x, y]

        canvas.create_oval(
            x, y, x + SPACE_SIZE, y + SPACE_SIZE,
            fill=FOOD_COLOR, tag="food"
        )
