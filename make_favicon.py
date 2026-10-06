from PIL import Image, ImageDraw, ImageFont

SIZE = 256
img = Image.new("RGB", (SIZE, SIZE), "#14342b")
d = ImageDraw.Draw(img)
d.rounded_rectangle([0, SIZE - 22, SIZE, SIZE], radius=0, fill="#e08a1e")  # orange line, banner jaisi

font = None
for name in ["arialbd.ttf", "segoeuib.ttf", "DejaVuSans-Bold.ttf"]:
    try:
        font = ImageFont.truetype(name, 170)
        break
    except OSError:
        continue
if font is None:
    font = ImageFont.load_default()

d.text((SIZE / 2, SIZE / 2 - 10), "M", fill="#f6f1e4", font=font, anchor="mm")
img.save("app/favicon.png")
print("favicon ban gaya: app/favicon.png")