from PIL import Image, ImageDraw

scale = 4
size = 512 * scale

def render_icon(transparent=False):
    bg = (0, 0, 0, 0) if transparent else "#F7F5F0"
    img = Image.new("RGBA", (size, size), bg)
    overlay = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    if transparent:
        # Для мелкой вкладки (16x16): крупные круги почти во весь холст, толстый контур и яркие цвета
        width = 34 * scale
        circles = [
            (256 * scale, 168 * scale, 142 * scale, (14, 159, 181, 65), "#0E9FB5"),   # Яркий бирюзовый
            (168 * scale, 322 * scale, 142 * scale, (224, 90, 43, 65), "#E05A2B"),    # Яркий терракотово-коралловый
            (344 * scale, 322 * scale, 142 * scale, (46, 158, 75, 65), "#2E9E4B"),    # Яркий зелёный
        ]
    else:
        # Для большой иконки приложения на бежевом фоне: спокойные фирменные цвета буклетов
        width = 11 * scale
        circles = [
            (256 * scale, 196 * scale, 116 * scale, (46, 126, 139, 34), "#2E7E8B"),
            (194 * scale, 306 * scale, 116 * scale, (184, 88, 56, 34), "#B85838"),
            (318 * scale, 306 * scale, 116 * scale, (78, 124, 89, 34), "#4E7C59"),
        ]

    for cx, cy, r, fill, _ in circles:
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill)

    img = Image.alpha_composite(img, overlay)
    draw_line = ImageDraw.Draw(img)

    for cx, cy, r, _, stroke in circles:
        draw_line.ellipse((cx - r, cy - r, cx + r, cy + r), outline=stroke, width=width)

    out = img.resize((512, 512), Image.Resampling.LANCZOS)
    return out if transparent else out.convert("RGB")

render_icon(transparent=True).save("favicon.png", "PNG")
render_icon(transparent=False).save("icon.png", "PNG")
print("Готово! Яркая favicon.png и спокойная icon.png обновлены.")
