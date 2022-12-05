import turtle, math


class Board:

  def __init__(self, grid_size, N):
    self.dx = grid_size
    self.dy = -grid_size
    self.N = N
    self.radius = 0.4 * grid_size
    self.top_left = (-grid_size * N * 0.5, grid_size * N * 0.5)
    self.player_colors = ['red', 'green']
    self.draw_grid()

  def draw_grid(self):
    x0, y0 = self.top_left
    for i in range(0, self.N + 1):
      turtle.penup()
      turtle.goto(x0, y0 + i * self.dy)
      turtle.pendown()
      turtle.goto(x0 + self.N * self.dx, y0 + i * self.dy)
    for i in range(0, self.N + 1):
      turtle.penup()
      turtle.goto(x0 + i * self.dx, y0)
      turtle.pendown()
      turtle.goto(x0 + i * self.dx, y0 + self.N * self.dy)

  def draw_mark(self, i, j, player):
    x0, y0 = self.top_left
    x = x0 + (j + 0.5) * self.dx
    y = y0 + (i + 0.5) * self.dy - self.radius
    turtle.penup()
    turtle.goto(x, y)
    turtle.begin_fill()
    turtle.color(self.player_colors[player - 1])
    turtle.pendown()
    turtle.circle(self.radius)
    turtle.end_fill()
    turtle.penup()
    turtle.goto(1000, 1000)

  def draw_game_over_text(self, txt):
    turtle.penup()
    turtle.goto(0, (self.N / 2 + 1) * self.dy)
    turtle.write(txt, font=("Arial", 16))

  def mouse_point_to_grid_index(self, x, y):
    x0, y0 = self.top_left
    i = math.floor((y - y0) / self.dy)
    j = math.floor((x - x0) / self.dx)
    return i, j

  def draw_players(self):
    turtle.goto(-self.dy * self.N, -self.dx * self.N)
    turtle.write("player 1: ")
    turtle.penup()
    turtle.begin_fill()
    turtle.color(self.player_colors[0])
    turtle.pendown()
    turtle.circle(self.radius)
    turtle.end_fill()
    turtle.penup()
    turtle.goto(1000, 1000)
    turtle.goto(-self.dy * self.N, self.dx * self.N)
    turtle.write("player 2: ")
    turtle.penup()
    turtle.begin_fill()
    turtle.color(self.player_colors[1])
    turtle.pendown()
    turtle.circle(self.radius)
    turtle.end_fill()
    turtle.penup()
    turtle.goto(1000, 1000)
