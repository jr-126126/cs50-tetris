

class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)]

        # Check if the move is valid
    def is_valid_move(self, piece, dx=0, dy=0):
        # dx, dy are the changes we want to make (move left = dx=-1, etc) 
        for row in range(len(piece.shape)):
            for col in range(len(piece.shape[row])):
                if piece.shape[row][col] == 1:
                        new_x = piece.x + col + dx
                        new_y = piece.y + row + dy
                        if new_x < 0 or new_x >= self.width:
                            return False
                        if new_y >= self.height:
                            return False
                        
                        if new_y >= 0 and self.grid[new_y][new_x] != 0:
                            return False
                        
        return True
    

    def lock_piece(self, piece):
        for row in range(len(piece.shape)):
            for col in range(len(piece.shape[row])):
                if piece.shape[row][col] == 1:
                    grid_x = piece.x + col
                    grid_y = piece.y + row
                    self.grid[grid_y][grid_x] = piece.shape_type

    def clear_lines(self):
     lines_cleared = 0
     row = self.height - 1 # Start on the bottom row

     while row >= 0:
          if all(self.grid[row][col] != 0 for col in range(self.width)):
               # row is full - clear line
               del self.grid[row]
               # add new row to top
               self.grid.insert(0, [0 for _ in range(self.width)])
               lines_cleared += 1
          else:
               row -= 1
     return lines_cleared

    def get_cell(self, x, y):
        return self.grid[y][x]