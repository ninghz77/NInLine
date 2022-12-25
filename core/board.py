import turtle, math


class Board:

  def __init__(
    self,
    grid_size,
    N,
    player1_desc=None,
    player2_desc=None,
  ):
    self.dx = grid_size
    self.dy = -grid_size
    self.N = N
    self.radius = 0.4 * grid_size
    self.top_left = (-grid_size * N * 0.5, grid_size * N * 0.5)
    self.player_colors = ['red', 'green', 'white']
    self.player_desc = [player1_desc, player2_desc]
    self.turn_pos = [
      (-grid_size * (N * 0.5 + 2), -self.radius),
      (grid_size * (N * 0.5 + 2), -self.radius),
    ]
    self.draw_grid()
    self.draw_players()
    self.draw_turn(1)

  def mouse_point_to_grid_index(self, x, y):
    x0, y0 = self.top_left
    i = math.floor((y - y0) / self.dy)
    j = math.floor((x - x0) / self.dx)
    return i, j

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
    self.draw_line_num()

  def draw_circle(self, pos, color):
    turtle.penup()
    turtle.goto(pos[0], pos[1])
    turtle.begin_fill()
    turtle.color(color)
    turtle.pendown()
    turtle.circle(self.radius)
    turtle.end_fill()
    turtle.penup()
    turtle.goto(1000, 1000)

  def opponent_player(self, player):
    if player == 0:
      return 0
    return 2 if player == 1 else 1

  def draw_turn(self, player):
    opp_player  = self.opponent_player(player)
    # erase the opp player turn
    self.draw_circle(self.turn_pos[opp_player - 1], "white")
    # draw player turn
    self.draw_circle(
      self.turn_pos[player - 1], 
      self.player_colors[player - 1],
    )

  def draw_mark(self, i, j, player):
    x0, y0 = self.top_left
    x = x0 + (j + 0.5) * self.dx
    y = y0 + (i + 0.5) * self.dy - self.radius
    self.draw_circle((x, y), self.player_colors[player - 1])

  def draw_text(self, x, y, txt, player):
    turtle.penup()
    turtle.goto(x, y)
    turtle.color(self.player_colors[player - 1])
    turtle.write(txt, font=("Arial", 16))

  def draw_game_over_text(self, txt, player):
    self.draw_text(
      -2 * self.dx,
      (self.N / 2 + 1) * self.dy,
      txt,
      player,
    )

  def draw_player(self, x, y, player):
    desc = self.player_desc[player - 1]
    if desc:
      txt = "P{}: {}".format(player, desc)
    else:
      txt = "Player {}".format(player)
    self.draw_text(x, y, txt, player)

  def draw_players(self):
    self.draw_player(
      -(self.N / 2) * self.dx,
      -(self.N / 2 + 1) * self.dy,
      1,
    )
    self.draw_player(
      0,
      -(self.N / 2 + 1) * self.dy,
      2,
    ),

  def draw_line_num(self):
    x0, y0 = self.top_left
    for i in range(self.N):
      turtle.penup()
      turtle.goto(x0 - self.dx, y0 + (i + 1) * self.dy)
      turtle.write(str(i), font=("Arial", 16))
    for i in range(self.N):
      turtle.penup()
      turtle.goto(x0 + (i + 0.3) * self.dx, y0)
      turtle.write(str(i), font=("Arial", 16))

