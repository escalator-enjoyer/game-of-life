# game-of-life
 Conway's Game of Life with some modifications.
## Includes:
- 50x50 grid with zooming/panning
- Cells can be in one of 2 teams (pink & orange)
- Graphs each team's population ratio
- Normal conway rules
\+ cells can battle other cells, 50/50 on which wins
\+ cells have a 5% chance to randomly replicate, and if a cell is alive and alone it has a 10% chance to survive to the next frame and try rapidly replicating
\+ cells can "betray" their team and convert to the opposite team if there are less than 6 cells in a clump (0.5%)
\+ 0.01% chance for a cell to come alive randomly (miracle)
--- todo ---
- Weighted random in fights depending on clump size
--- ideas after todo ---
- Other stats
- Mutations (teleportation, no natural death, invincible player-controlled cell, etc.)
- Aristocracy/monarchy