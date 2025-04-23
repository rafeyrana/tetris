import random
import time
import curses
import os

# tetris

# what im thinking of doing:
'''
have an empty matrix which is a 2d list, the dimensions would be 20 rows and 10 cols
this will be the be maintained as the current state of the game


the other thing we need to track is the shapes of the current peices, each piece can have multipe representations
these include O, I, S, Z ,L, T, J
how to represent these?
store them as a map with the key and the value can be a box which will be a 2d list which will be different size for different sizes

for example the S shape can be: 
[[b, 0, b],
 [b, r, b],
 [b,r, b]]

 b = black 
 r = red 
 g = fixed pieces


representations of the shapes:
S , Z, L, T, J will be 3x3
O will be 2x2
I will be 4x4

now for each piece we store these representations and have a rotate function using the mirror and transpose to get all versions of it

so all the pieces come from the top of the matrix and the coordinates are going to relative to the bottom top left corner of the grid

we will maintain an incremental counter to keep track of the time

each second we will get the position of the current piece which is the top left corner of the grid and move it down by 1
check for collision / final position:
if the piece is at the bottom of the grid or if it is colliding with the other pieces then we stop the piece there and make it a permanent piece
everytime we can check if it can go down by one, if it overlaps with any of the fixed pieces then it can be made permanent at its old position and it it can go down one then we let it, not let the reds be overlapping with the greens
this is going to be a function that we can call and it will return a boolean value (canGoDown)
so the moving piece is going to be in a different matrix and the fixed pieces be on the board and the comparisons will be done using the overlap of these


how do we check for collision?
we can have a function that takes the overlay board and the fixed board, it will make a set of both non empty coordinates for both boards in a set and returns a boolean value (isCollision)


'''

def initialize_game():
    # Create empty board (20x10)
    board = [["b" for _ in range(10)] for _ in range(20)]
    
    # Create tetromino dictionary
    tetromino_shapes = create_tetromino_shapes()
    
    # Generate first random piece and its position
    piece_type = random.choice(list(tetromino_shapes.keys()))
    piece = tetromino_shapes[piece_type]
    
    # Set initial piece position (top center)
    position = {
        "x": 3,  # Center horizontally
        "y": 0   # Top of the board
    }
    
    return board, tetromino_shapes, piece, position

def create_tetromino_shapes():
    # Define all tetromino shapes (O, I, S, Z, L, T, J)
    # b = black/empty, r = red/active piece
    
    shapes = {
        "O": [
            ["r", "r"],
            ["r", "r"]
        ],
        "I": [
            ["b", "b", "b", "b"],
            ["r", "r", "r", "r"],
            ["b", "b", "b", "b"],
            ["b", "b", "b", "b"]
        ],
        "S": [
            ["b", "r", "r"],
            ["r", "r", "b"],
            ["b", "b", "b"]
        ],
        "Z": [
            ["r", "r", "b"],
            ["b", "r", "r"],
            ["b", "b", "b"]
        ],
        "L": [
            ["r", "b", "b"],
            ["r", "r", "r"],
            ["b", "b", "b"]
        ],
        "J": [
            ["b", "b", "r"],
            ["r", "r", "r"],
            ["b", "b", "b"]
        ],
        "T": [
            ["b", "r", "b"],
            ["r", "r", "r"],
            ["b", "b", "b"]
        ]
    }
    
    return shapes

def rotate_piece(piece):
    # Implement rotation using transpose and mirror operations, always clockwise
    # First, get the dimensions of the piece
    n = len(piece)
    
    # Create a new matrix for the rotated piece
    rotated = [["b" for _ in range(n)] for _ in range(n)]
    
    # Rotate the piece 90 degrees clockwise (transpose and then mirror horizontally)
    # Step 1: Transpose the matrix
    for i in range(n):
        for j in range(n):
            rotated[i][j] = piece[j][i]
    
    # Step 2: Mirror horizontally (reverse each row)
    for i in range(n):
        rotated[i] = rotated[i][::-1]
    
    return rotated

def get_random_piece():
    # Select a random piece from available shapes
    tetromino_shapes = create_tetromino_shapes()
    piece_type = random.choice(list(tetromino_shapes.keys()))
    piece = tetromino_shapes[piece_type]
    
    # Set initial position (top center)
    position = {
        "x": 3,  # Center horizontally
        "y": 0   # Top of the board
    }
    
    return piece, position

def can_move(board, piece, new_position):
    # Check if piece can move to new position without collision
    # check for being in the grid bounds
    # check for collisions with the fixed pieces
    return not is_collision(board, piece, new_position)

def is_collision(board, piece, position):
    # Check if piece at position collides with settled pieces or boundaries
    piece_coordinates = get_piece_coordinates(piece, position)
    
    # Check for each coordinate of the piece
    for x, y in piece_coordinates:
        # Check if the coordinate is out of bounds
        if x < 0 or x >= 10 or y < 0 or y >= 20:
            return True
        
        # Check if the coordinate collides with a fixed piece
        if y < len(board) and x < len(board[0]) and board[y][x] == "g":
            return True
    
    return False

def get_piece_coordinates(piece, position):
    # Convert piece matrix and position to list of absolute coordinates
    coordinates = []
    for y in range(len(piece)):
        for x in range(len(piece[y])):
            if piece[y][x] == "r":  # Only consider non-empty cells
                abs_x = position["x"] + x
                abs_y = position["y"] + y
                coordinates.append((abs_x, abs_y))
    
    return coordinates

def drop_piece(board, piece, position):
    # Move piece down until collision
    # Create a new position that's one row down
    current_position = position.copy()
    new_position = position.copy()
    
    # Keep moving down until collision
    while True:
        new_position["y"] += 1
        if is_collision(board, piece, new_position):
            return current_position  # Return the last valid position
        current_position = new_position.copy()

def settle_piece(board, piece, position):
    # Convert active piece to settled piece
    # Update board with new settled piece
    piece_coordinates = get_piece_coordinates(piece, position)
    
    # Update the board by changing the color of the piece from "r" to "g"
    for x, y in piece_coordinates:
        if 0 <= y < len(board) and 0 <= x < len(board[0]):
            board[y][x] = "g"  # Fixed pieces are represented by "g"
    
    return board

def game_loop(stdscr):
    # Set up curses
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(True)  # Make getch non-blocking
    
    # Initialize colors if supported
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)  # For active pieces
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # For fixed pieces
    
    # Initialize game
    board, tetromino_shapes, current_piece, current_position = initialize_game()
    
    game_over = False
    last_move_time = time.time()
    move_interval = 1.0  # Move down every 1 second
    
    while not game_over:
        # Clear screen
        stdscr.clear()
        
        # Get terminal dimensions
        max_y, max_x = stdscr.getmaxyx()
        
        # Render the current state
        display_board = overlay_piece(board, current_piece, current_position)
        render_board(stdscr, display_board)
        
        # Check if it's time to move the piece down automatically
        current_time = time.time()
        if current_time - last_move_time >= move_interval:
            # Create a new position that's one row down
            new_position = current_position.copy()
            new_position["y"] += 1
            
            # Check if the move is valid
            if can_move(board, current_piece, new_position):
                current_position = new_position
            else:
                # Settle the piece
                board = settle_piece(board, current_piece, current_position)
                
                # Generate a new piece
                current_piece, current_position = get_random_piece()
                
                # Check if the new piece can be placed
                if is_collision(board, current_piece, current_position):
                    game_over = True
                    # Only show game over if there's room
                    if 22 < max_y:
                        stdscr.addstr(22, 0, "Game Over!")
            
            last_move_time = current_time
        
        # Add score and game info (if there's room)
        info_y = min(len(board)+2, max_y-1)
        if info_y > 0 and info_y < max_y:
            info_text = "Use controls to move. Press 'q' to quit."
            if len(info_text) >= max_x:
                info_text = info_text[:max_x-1]
            stdscr.addstr(info_y, 0, info_text)
        
        # Get user input (non-blocking)
        key = stdscr.getch()
        
        if key != -1:  # If a key was pressed
            if key == ord('q'):
                game_over = True
                continue
            
            # Process user input
            new_position = current_position.copy()
            new_piece = current_piece
            
            if key == ord('a') or key == curses.KEY_LEFT:  # Move left
                new_position["x"] -= 1
            elif key == ord('d') or key == curses.KEY_RIGHT:  # Move right
                new_position["x"] += 1
            elif key == ord('s') or key == curses.KEY_DOWN:  # Move down
                new_position["y"] += 1
                last_move_time = current_time  # Reset the timer when manually moving down
            elif key == ord('w') or key == curses.KEY_UP:  # Rotate
                new_piece = rotate_piece(current_piece)
            elif key == ord(' '):  # Hard drop
                new_position = drop_piece(board, current_piece, current_position)
            
            # Check if the move is valid
            if can_move(board, new_piece, new_position):
                current_piece = new_piece
                current_position = new_position
                
                # If it was a hard drop, settle immediately
                if key == ord(' '):
                    board = settle_piece(board, current_piece, current_position)
                    current_piece, current_position = get_random_piece()
                    
                    # Check if the new piece can be placed
                    if is_collision(board, current_piece, current_position):
                        game_over = True
                        # Only show game over if there's room
                        if 22 < max_y:
                            stdscr.addstr(22, 0, "Game Over!")
        
        # Refresh the screen
        stdscr.refresh()
        
        # Small delay to reduce CPU usage
        time.sleep(0.05)
    
    # Wait for a key press before exiting
    stdscr.nodelay(False)
    
    # Only show exit message if there's room
    max_y, max_x = stdscr.getmaxyx()
    if 23 < max_y:
        exit_msg = "Press any key to exit..."
        if len(exit_msg) >= max_x:
            exit_msg = exit_msg[:max_x-1]
        stdscr.addstr(23, 0, exit_msg)
    
    stdscr.getch()

def overlay_piece(board, piece, position):
    # Create a temporary board with the piece overlaid at position
    overlay = [row[:] for row in board]  # Create a deep copy of the board
    piece_coordinates = get_piece_coordinates(piece, position)
    
    # Add the piece to the overlay
    for x, y in piece_coordinates:
        if 0 <= y < len(overlay) and 0 <= x < len(overlay[0]):
            overlay[y][x] = "r"  # Active piece is represented by "r"
    
    return overlay

def render_board(stdscr, board):
    # Get terminal dimensions
    max_y, max_x = stdscr.getmaxyx()
    
    # Render the board using curses
    stdscr.addstr(0, 0, "+--------------------+")
    for i, row in enumerate(board):
        if i+1 >= max_y:  # Check if we're exceeding vertical space
            break
        line = "|"
        for cell in row:
            if cell == "b":
                line += "  "  # Empty cell
            elif cell == "r":
                line += "[]"  # Active piece
            elif cell == "g":
                line += "##"  # Fixed piece
        line += "|"
        stdscr.addstr(i+1, 0, line)
    
    if len(board)+1 < max_y:
        stdscr.addstr(len(board)+1, 0, "+--------------------+")
    
    # Add controls info (only if we have room)
    if len(board)+3 < max_y:
        control_text = "Controls: a/←: left, d/→: right, w/↑: rotate, s/↓: down, space: drop, q: quit"
        # Truncate control text if it's too long for the terminal width
        if len(control_text) >= max_x:
            control_text = control_text[:max_x-1]
        stdscr.addstr(len(board)+3, 0, control_text)

def main():
    # Initialize curses
    os.environ.setdefault('ESCDELAY', '25')  # Reduce delay for escape sequences
    curses.wrapper(game_loop)

if __name__ == "__main__":
    main()