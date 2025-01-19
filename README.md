# game-of-life
 Conway's Game of Life with some modifications.

## Modifications
- Travel: 0.5% chance for a cell to travel in a random direction
- Replication: 5% chance for a cell to duplicate regardless of neighbors
- Lone Survival: 10% chance for a cell to survive and attempt to immediately replicate 4 times if it has no neighbors
- Betrayal: 0.5% chance for a cell to betray its team and turn into the opposite color if the clump* size is 5 or less
- Miracle: 0.01% chance for a dead cell to come alive if it does not have any neighbors 

*clumps are groups of neighboring living cells (area of any solid shape)

## Features
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