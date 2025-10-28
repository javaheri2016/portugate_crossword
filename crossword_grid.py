from PIL import Image, ImageDraw, ImageFont

# Read grid from file
with open("data/structure1.txt", "r", encoding="utf-8") as f:
    raw_grid = [line.strip() for line in f if line.strip()]

# Convert characters to True (white) / False (black)
grid = [[c == '_' for c in row] for row in raw_grid]
rows = len(grid)
cols = len(grid[0])

# Numbering logic
numbers = [[0] * cols for _ in range(rows)]
counter = 1

for r in range(rows):
    for c in range(cols):
        if not grid[r][c]:
            continue

        start_across = (c == 0 or not grid[r][c - 1]) and (c + 1 < cols and grid[r][c + 1])
        start_down = (r == 0 or not grid[r - 1][c]) and (r + 1 < rows and grid[r + 1][c])

        if start_across or start_down:
            numbers[r][c] = counter
            counter += 1

# Drawing parameters
cell_size = 80
border = 3
padding = 10

img_w = cols * cell_size + border
img_h = rows * cell_size + border

img = Image.new("RGB", (img_w, img_h), "white")
draw = ImageDraw.Draw(img)

# Fonts
try:
    font_num = ImageFont.truetype("Roboto.ttf", 24)
    font_letter = ImageFont.truetype("Roboto.ttf", 32)
except:
    font_num = ImageFont.load_default()
    font_letter = ImageFont.load_default()

# Draw cells
for r in range(rows):
    for c in range(cols):
        x0, y0 = c * cell_size, r * cell_size
        x1, y1 = x0 + cell_size, y0 + cell_size

        if grid[r][c]:
            # white cell
            draw.rectangle([x0, y0, x1, y1], fill="white", outline="black", width=border)

            # number (if any)
            if numbers[r][c] != 0:
                draw.text((x0 + padding, y0 + padding), str(numbers[r][c]), fill="black", font=font_num)
        else:
            # black cell
            draw.rectangle([x0, y0, x1, y1], fill="black", outline="black", width=border)

# Save image
output_path = "crossword_grid_numbered.png"
img.save(output_path)
print(f"✅ Crossword image saved as: {output_path}")
