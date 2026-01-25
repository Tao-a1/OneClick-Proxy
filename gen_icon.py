from PIL import Image, ImageDraw

def create_icon(path):
    size = (128, 128)
    # Dark purple background
    bg_color = (26, 27, 30) 
    accent_color = (121, 80, 242) # Purple
    white = (255, 255, 255)
    
    img = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw a rounded rectangle (background)
    draw.rounded_rectangle([(10, 10), (118, 118)], radius=20, fill=bg_color, outline=accent_color, width=4)
    
    # Draw a shield-like shape or just a "P" for Proxy
    # Let's draw a simple shield
    # Shield points
    # Top-Left: (30, 30), Top-Right: (98, 30)
    # Bottom tip: (64, 100)
    # Curves are hard with simple polygon, let's do a simple polygon shield
    shield_points = [
        (30, 30), 
        (98, 30), 
        (98, 60), 
        (64, 100), 
        (30, 60)
    ]
    draw.polygon(shield_points, fill=accent_color)
    
    # Draw a lock body in center (white)
    # Lock body rect: (54, 55) to (74, 75)
    draw.rectangle([(54, 55), (74, 75)], fill=white)
    # Lock shackle (arc) - approximated by lines/rect for simplicity or arc if available
    draw.arc([(54, 40), (74, 60)], start=180, end=0, fill=white, width=3)

    img.save(path)
    print(f"Icon saved to {path}")

if __name__ == "__main__":
    create_icon("https_proxy_setup/extension/icon.png")
