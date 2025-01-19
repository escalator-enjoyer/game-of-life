import pygame
import random

WIDTH, HEIGHT = 800, 600
FPS_DISPLAY = 60
FPS_LOGIC = 15

travel = True
replication = True
lone_survival = True
betrayal = True
miracle = True
grid_width, grid_height = 50, 50

colors = {
  'black': (19, 19, 19),
  'gray': (80, 80, 80),
  'white': (236, 236, 236),
  'pink': (247, 140, 255),
  'orange': (255, 200, 140)
}

teams = ['pink', 'orange']
def cycle(list):
  while True: yield from list
team_cycler = cycle(teams)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("game of silly")
clock = pygame.time.Clock()

class Cell:
  def __init__(self, x, y, alive=False, team='pink'):
    self.x = x
    self.y = y
    self.alive = alive
    self.team = team

  def toggle(self, team):
    self.alive = not self.alive
    self.team = team

  def convert(self, team):
    self.team = team

  def draw(self, surface, cell_size, offset_x, offset_y):
    cell_x = self.x * cell_size + offset_x
    cell_y = self.y * cell_size + offset_y
    if self.alive:
      pygame.draw.rect(surface, colors[self.team], (cell_x, cell_y, cell_size, cell_size))
    else:
      pygame.draw.rect(surface, colors['black'], (cell_x, cell_y, cell_size, cell_size))

class Grid:
  def __init__(self):
    self.cells = {}
    self.total_pinks = 0
    self.total_oranges = 0

  def get_cell(self, x, y):
    if 0 <= x < grid_width and 0 <= y < grid_height:
      if (x, y) not in self.cells:
        self.cells[(x, y)] = Cell(x, y)
      return self.cells[(x, y)]
    return None

  def toggle_cell(self, x, y, team):
    cell = self.get_cell(x, y)
    if cell:
      cell.toggle(team)

  def update(self):
    new_cells = {}
    to_check = set((x, y) for x in range(grid_width) for y in range(grid_height))
    for x, y in self.cells.keys():
      to_check.update((x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1))

    for x, y in to_check:
      cell = self.get_cell(x, y)
      if not cell:
        continue

      live_neighbors = self.count_live_neighbors(x, y)
      neighbor_teams = self.get_neighbor_teams(x, y)

      if cell.alive:
        # Confirm cell as alive this frame if its not dead
        if live_neighbors in (2, 3):
          new_cells[(x, y)] = Cell(x, y, True, cell.team)
        
        # Betrayal (0.5%)
        if betrayal and random.random() <= 0.005 and self.calculate_clump_size(x, y) <= 5:
          new_cells[(x, y)] = Cell(x, y, True, 'orange' if cell.team == 'pink' else 'pink')

        # Travel (0.5%)
        if travel and random.random() <= 0.005:
          self.random_travel(x, y, cell.team)
        
        # Chance to replicate regardless of neighbors
        if replication and random.random() <= 0.05:
          self.random_duplicate(x, y, cell.team)
        
        if not live_neighbors in (2, 3):
          # Replication and survival if alone
          if lone_survival and live_neighbors == 0 and random.random() <= 0.1:
            new_cells[(x, y)] = Cell(x, y, True, cell.team)
            [self.random_duplicate(x, y, cell.team) for _ in range(4)]
          else:
            # Normal cog death through under- or overpopulation (neighbors < 2 or neighbors > 3)
            new_cells[(x, y)] = Cell(x, y, False)
      else:
        # Select the team for the replicated cell, 1% chance of creation of life
        if live_neighbors == 3:
          if len(neighbor_teams) > 1:
            # 50/50 between each team to select winner
            dominant_team = random.choice(neighbor_teams)
          elif len(neighbor_teams) == 1:
            dominant_team = neighbor_teams[0]
          # Cell is alive sparkle emoji
          new_cells[(x, y)] = Cell(x, y, True, dominant_team)
        # 0.01% chance of miracle
        elif miracle and live_neighbors == 0 and random.random() <= 0.0001:
          dominant_team = random.choice(teams)
          [self.random_duplicate(x, y, dominant_team) for _ in range(4)]
    
    self.cells = {pos: cell for pos, cell in new_cells.items() if cell.alive}
    self.total_pinks = sum([1 for cell in self.cells.values() if cell.team == 'pink' and cell.alive])
    self.total_oranges = sum([1 for cell in self.cells.values() if cell.team == 'orange' and cell.alive])

  # If a cell discovers mitosis
  def random_duplicate(self, x, y, team):
    directions = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx != 0 or dy != 0)]
    random.shuffle(directions)
    for dx, dy in directions:
      neighbor = self.get_cell(x + dx, y + dy)
      if neighbor and not neighbor.alive:
        neighbor.alive = True
        neighbor.team = team
        break
  
  def random_travel(self, x, y, team):
    directions = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx != 0 or dy != 0)]
    dx, dy = random.choice(directions)
    neighbor = self.get_cell(x + dx, y + dy)
    curr_cell = self.get_cell(x, y)
    if neighbor and not neighbor.alive:
      neighbor.alive = True
      neighbor.team = team
      curr_cell.alive = False
  
  def count_live_neighbors(self, x, y):
    count = 0
    for dx in (-1, 0, 1):
      for dy in (-1, 0, 1):
        if dx == 0 and dy == 0:
          continue
        neighbor = self.cells.get((x + dx, y + dy))
        if neighbor and neighbor.alive:
          count += 1
    return count

  def get_neighbor_teams(self, x, y):
    teams = []
    for dx in (-1, 0, 1):
      for dy in (-1, 0, 1):
        if dx == 0 and dy == 0:
          continue
        neighbor = self.cells.get((x + dx, y + dy))
        if neighbor and neighbor.alive:
          teams.append(neighbor.team)
    return teams

  def calculate_clump_size(self, x, y):
    visited = set()
    to_visit = [(x, y)]
    clump_size = 0

    while to_visit:
      cx, cy = to_visit.pop()
      if (cx, cy) in visited:
        continue
      visited.add((cx, cy))

      cell = self.get_cell(cx, cy)
      if cell and cell.alive:
        clump_size += 1
        to_visit.extend((cx + dx, cy + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx != 0 or dy != 0))

    return clump_size

  def draw(self, surface, cell_size, offset_x, offset_y):
    for cell in self.cells.values():
      cell.draw(surface, cell_size, offset_x, offset_y)

def draw_ui(active_color, pct_pinks, pct_oranges):
  rect_width, rect_height = 210, 440
  rect_x, rect_y = 10, 10
  pygame.draw.rect(screen, colors[active_color], (rect_x - 2, rect_y - 2, rect_width + 4, rect_height + 4), 2)
  pygame.draw.rect(screen, colors['black'], (rect_x, rect_y, rect_width, rect_height))

  color_text = font.render(f"Selected Color:", True, colors['white'])
  color_box = pygame.Surface((30, 30))
  color_box.fill(colors[active_color])

  instructions = [
    color_text,
    color_box,
    font.render('E: Switch Color', True, colors['white']),
    font.render('Left Click: Place', True, colors['white']),
    font.render('Right Click: Pan', True, colors['white']),
    font.render('Scroll: Zoom', True, colors['white']),
    font.render('R: Reset', True, colors['white']),
    font.render('Space: Pause/Play', True, colors['white']),
    font.render(f"T: Travel ({'On' if travel else 'Off'})", True, colors['white']),
    font.render(f"Y: Replication ({'On' if replication else 'Off'})", True, colors['white']),
    font.render(f"U: Lone Survival ({'On' if lone_survival else 'Off'})", True, colors['white']),
    font.render(f"I: Betrayal ({'On' if betrayal else 'Off'})", True, colors['white']),
    font.render(f"O: Miracle ({'On' if miracle else 'Off'})", True, colors['white']),
    font.render(f"Pink: {pct_pinks:.2f}%", True, colors['pink']),
    font.render(f"Orange: {pct_oranges:.2f}%", True, colors['orange']),
  ]

  screen.blit(instructions[0], (rect_x + 10, rect_y + 10))
  screen.blit(instructions[1], (rect_x + 20 + instructions[0].get_width(), rect_y + 10))
  screen.blit(instructions[2], (rect_x + 10, rect_y + 40))
  screen.blit(instructions[3], (rect_x + 10, rect_y + 70))
  screen.blit(instructions[4], (rect_x + 10, rect_y + 100))
  screen.blit(instructions[5], (rect_x + 10, rect_y + 130))
  screen.blit(instructions[6], (rect_x + 10, rect_y + 160))
  screen.blit(instructions[7], (rect_x + 10, rect_y + 190))
  screen.blit(instructions[8], (rect_x + 10, rect_y + 220))
  screen.blit(instructions[9], (rect_x + 10, rect_y + 250))
  screen.blit(instructions[10], (rect_x + 10, rect_y + 280))
  screen.blit(instructions[11], (rect_x + 10, rect_y + 310))
  screen.blit(instructions[12], (rect_x + 10, rect_y + 340))
  screen.blit(instructions[13], (rect_x + 10, rect_y + 370))
  screen.blit(instructions[14], (rect_x + 10, rect_y + 400))

def calculate_coverage(pinks, oranges):
  total_cells = grid_width * grid_height
  pct_pinks = (pinks / total_cells) * 100
  pct_oranges = (oranges / total_cells) * 100

  if (pinks / total_cells + oranges / total_cells) == 0:
    return 0, 0
  elif (pinks / total_cells + oranges / total_cells) > 0:
    pct_pinks = (pinks / total_cells) / (pinks / total_cells + oranges / total_cells) * 100
  else:
    pct_pinks = 100
  pct_oranges = 100 - pct_pinks
  return pct_pinks, pct_oranges

def draw_graph(history):
  graph_width, graph_height = 210, 100
  graph_x, graph_y = 10, 460
  pygame.draw.rect(screen, colors['black'], (graph_x, graph_y, graph_width, graph_height))

  if len(history) > 1:
    for i in range(1, len(history)):
      pygame.draw.line(screen, colors['pink'], 
                       (graph_x + (i - 1) * (graph_width / 100), graph_y + graph_height - history[i - 1][0]),
                       (graph_x + i * (graph_width / 100), graph_y + graph_height - history[i][0]))
      pygame.draw.line(screen, colors['orange'], 
                       (graph_x + (i - 1) * (graph_width / 100), graph_y + graph_height - history[i - 1][1]),
                       (graph_x + i * (graph_width / 100), graph_y + graph_height - history[i][1]))

grid = Grid()
cell_size = 10
grid_pixel_width = grid_width * cell_size
grid_pixel_height = grid_height * cell_size
offset_x = (WIDTH - grid_pixel_width) // 2 + 110
offset_y = (HEIGHT - grid_pixel_height) // 2

font = pygame.font.Font('OpenSans.ttf', 20)
running = True
paused = True
active_color = next(team_cycler)
last_logic_update = pygame.time.get_ticks()
history = []

while running:
  current_time = pygame.time.get_ticks()
  
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    elif event.type == pygame.KEYDOWN:
      if event.key == pygame.K_SPACE:
        paused = not paused
      elif event.key == pygame.K_r:
        grid = Grid()
        total_pinks = 0
        total_oranges = 0
        history = []
      elif event.key == pygame.K_e:
        active_color = next(team_cycler)
      elif event.key == pygame.K_t:
        travel = not travel
      elif event.key == pygame.K_y:
        replication = not replication
      elif event.key == pygame.K_u:
        lone_survival = not lone_survival
      elif event.key == pygame.K_i:
        betrayal = not betrayal
      elif event.key == pygame.K_o:
        miracle = not miracle
    elif event.type == pygame.MOUSEBUTTONDOWN:
      if event.button == 1:
        mouse_x, mouse_y = event.pos
        grid_x = (mouse_x - offset_x) // cell_size
        grid_y = (mouse_y - offset_y) // cell_size
        grid.toggle_cell(grid_x, grid_y, team=active_color)
      elif event.button == 4:
        cell_size = min(cell_size + 1, 50)
        grid_pixel_width = grid_width * cell_size
        grid_pixel_height = grid_height * cell_size
        offset_x = (WIDTH - grid_pixel_width) // 2 + 110
        offset_y = (HEIGHT - grid_pixel_height) // 2
      elif event.button == 5:
        cell_size = max(cell_size - 1, 2)
        grid_pixel_width = grid_width * cell_size
        grid_pixel_height = grid_height * cell_size
        offset_x = (WIDTH - grid_pixel_width) // 2 + 110
        offset_y = (HEIGHT - grid_pixel_height) // 2
    elif event.type == pygame.MOUSEMOTION:
      if event.buttons[2]:
        offset_x += event.rel[0]
        offset_y += event.rel[1]
    elif event.type == pygame.VIDEORESIZE:
      WIDTH, HEIGHT = event.size
      screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

  # Update game logic (Grid) at 10 FPS
  if current_time - last_logic_update >= 1000 / FPS_LOGIC:
    if not paused:
      grid.update()
      pct_pinks, pct_oranges = calculate_coverage(grid.total_pinks, grid.total_oranges)
      history.append((pct_pinks, pct_oranges))
      if len(history) > 100:
        history.pop(0)
    last_logic_update = current_time

  # Rendering (Display) at 60 FPS
  screen.fill(colors['black'])

  outline_rect = pygame.Rect(offset_x, offset_y, grid_pixel_width, grid_pixel_height)
  pygame.draw.rect(screen, colors['gray'], outline_rect, 1)
  grid.draw(screen, cell_size, offset_x, offset_y)

  pct_pinks, pct_oranges = calculate_coverage(grid.total_pinks, grid.total_oranges)
  draw_ui(active_color, pct_pinks, pct_oranges)
  draw_graph(history)

  pygame.display.flip()
  clock.tick(FPS_DISPLAY)

pygame.quit()
