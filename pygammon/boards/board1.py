from PIL import Image, ImageDraw


def create_backgammon_board(save_path="backgammon_board.png"):
    # Dimensions
    board_width, board_height = 800, 400
    triangle_width, triangle_height = board_width // 12, board_height // 2

    # Create a blank image
    board = Image.new("RGB", (board_width, board_height), "saddlebrown")
    draw = ImageDraw.Draw(board)

    # Draw dividing line
    draw.line([(board_width // 2, 0), (board_width // 2, board_height)], fill="black", width=3)

    # Draw triangles (alternating colors)
    colors = ["white", "black"]
    for i in range(12):
        # Top triangles
        x1 = i * triangle_width
        x2 = x1 + triangle_width
        points = [(x1, 0), (x2, 0), ((x1 + x2) // 2, triangle_height)]
        draw.polygon(points, fill=colors[i % 2])

        # Bottom triangles
        points = [(x1, board_height), (x2, board_height), ((x1 + x2) // 2, board_height - triangle_height)]
        draw.polygon(points, fill=colors[i % 2])

    # Save the board as an image
    board.save(save_path)
    print(f"Backgammon board saved to {save_path}")
