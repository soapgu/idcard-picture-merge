#!/usr/bin/env python3
"""生成 README 演示示意图"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from PIL import Image, ImageDraw, ImageFont
from id_card_merge import merge_id_cards

FONT_PATH = "/System/Library/Fonts/STHeiti Medium.ttc"
TEMP_DIR = "/tmp/idcard_demo"
OUTPUT = "docs/demo.png"

CARD_COLOR = (225, 232, 241)


def make_font(size):
    return ImageFont.truetype(FONT_PATH, size)


def _draw_text(draw, pos, text, font, fill=(0, 0, 0)):
    draw.text(pos, text, font=font, fill=fill)


def generate_front_card():
    W, H = 1200, 1000
    M = 300
    img = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([M, M, W - M - 1, H - M - 1], fill=CARD_COLOR)
    f20 = make_font(22)
    f18 = make_font(18)
    f14 = make_font(14)
    # 头像占位
    ax, ay, aw, ah = M + 20, M + 30, 90, 120
    draw.rectangle([ax, ay, ax + aw, ay + ah],
                   fill=(180, 185, 190), outline=(120, 125, 130))
    _draw_text(draw, (ax + 18, ay + 44), "头像", f18, (80, 80, 80))
    # 字段
    fields = [
        ("姓名", "张三"),
        ("性别", "男"),
        ("民族", "汉"),
        ("出生", "1990.01.01"),
        ("住址", "xx市xx区xx路xx号"),
    ]
    x_label = M + 140
    x_value = M + 240
    y = M + 30
    for label, value in fields:
        _draw_text(draw, (x_label, y), label, f18, (100, 100, 100))
        _draw_text(draw, (x_value, y), value, f20, (0, 0, 0))
        y += 40
    _draw_text(draw, (x_label, y + 8), "公民身份号码", f14, (100, 100, 100))
    _draw_text(draw, (x_value, y + 8), "110101199001011234", f18, (0, 0, 0))
    return img


def generate_back_card():
    W, H = 1200, 1000
    M = 300
    img = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([M, M, W - M - 1, H - M - 1], fill=CARD_COLOR)
    f20 = make_font(22)
    f18 = make_font(18)
    f14 = make_font(14)
    # 国徽占位
    cx, cy, r = M + 300, M + 60, 50
    draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                 outline=(180, 140, 60), width=4)
    _draw_text(draw, (cx - 18, cy - 10), "国徽", f18, (160, 120, 40))
    # 字段
    _draw_text(draw, (M + 100, M + 180), "签发机关", f18, (100, 100, 100))
    _draw_text(draw, (M + 240, M + 178), "xx市公安局", f20, (0, 0, 0))
    _draw_text(draw, (M + 100, M + 230), "有效期限", f18, (100, 100, 100))
    _draw_text(draw, (M + 240, M + 228), "2020.01.01-2040.01.01", f18, (0, 0, 0))
    return img


def thumb_with_shadow(img, size, shadow_offset=5):
    thumb = img.resize(size, Image.LANCZOS)
    w, h = thumb.size
    out = Image.new("RGB", (w + shadow_offset, h + shadow_offset), (255, 255, 255))
    out.paste((220, 220, 220), [shadow_offset, shadow_offset, w + shadow_offset, h + shadow_offset])
    out.paste(thumb, (0, 0))
    # thin border
    ImageDraw.Draw(out).rectangle([0, 0, w - 1, h - 1], outline=(180, 180, 180))
    return out


def create_composite(front_img, back_img, merged_path):
    merged = Image.open(merged_path)
    mw, mh = merged.size
    target_mw = 400
    target_mh = int(mh * target_mw / mw)
    merged_small = merged.resize((target_mw, target_mh), Image.LANCZOS)

    W, H = 1360, 620
    diagram = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(diagram)
    f22 = make_font(22)
    f16 = make_font(16)
    f13 = make_font(13)

    # ===== Left Panel: Input =====
    pl = 0
    draw.rectangle([pl + 30, 14, pl + 340, 44], fill=(41, 128, 185), width=0)
    _draw_text(draw, (pl + 36, 17), "输入（原始图片）", make_font(15), (255, 255, 255))

    # front thumbnail - show the card with lots of white border
    ft = thumb_with_shadow(front_img, (200, 167))
    diagram.paste(ft, (pl + 50, 58))
    _draw_text(draw, (pl + 50, 232), "身份证正面", f13, (80, 80, 80))
    _draw_text(draw, (pl + 50, 248), "(大量空白边距)", f13, (160, 160, 160))

    # back thumbnail
    bt = thumb_with_shadow(back_img, (200, 167))
    diagram.paste(bt, (pl + 50, 278))
    _draw_text(draw, (pl + 50, 452), "身份证反面", f13, (80, 80, 80))
    _draw_text(draw, (pl + 50, 468), "(大量空白边距)", f13, (160, 160, 160))

    # ===== Center: Arrow =====
    arrow_color = (41, 128, 185)
    cx = 370
    for y_c in (145, 372):
        draw.line([cx, y_c, cx + 50, y_c], fill=arrow_color, width=3)
        draw.polygon([
            (cx + 55, y_c), (cx + 47, y_c - 6), (cx + 47, y_c + 6)
        ], fill=arrow_color)
    _draw_text(draw, (cx - 12, 210), "自 动", f16, arrow_color)
    _draw_text(draw, (cx - 12, 234), "裁 剪", f16, arrow_color)
    _draw_text(draw, (cx - 2, 258), "+", f16, arrow_color)
    _draw_text(draw, (cx - 12, 278), "合 并", f16, arrow_color)

    # ===== Right Panel: Output =====
    pr = 460
    draw.rectangle([pr, 14, W - 30, 44], fill=(39, 174, 96), width=0)
    _draw_text(draw, (pr + 10, 17), "输出（合并结果）", make_font(15), (255, 255, 255))

    # output background box
    box_l, box_t = pr, 55
    box_w = W - 30 - pr
    draw.rectangle([box_l, box_t, box_l + box_w, H - 30],
                   fill=(245, 247, 250), outline=(210, 218, 230))

    # center merged image
    img_x = box_l + (box_w - target_mw) // 2
    img_y = box_t + 20
    diagram.paste(merged_small, (img_x, img_y))
    draw.rectangle([img_x, img_y, img_x + target_mw - 1, img_y + target_mh - 1],
                   outline=(170, 180, 190))

    # annotations on merged image
    front_crop_h = 490
    gap_px = 100
    back_crop_h = 490
    total_h = front_crop_h + gap_px + back_crop_h
    y_off = (target_mh - total_h) // 2

    if y_off > 5:
        fy = img_y + y_off
        lx = img_x + target_mw + 12
        # front card label
        draw.line([lx, fy + 10, lx + 30, fy + 10], fill=(100, 180, 100), width=2)
        _draw_text(draw, (lx + 35, fy + 4), "正面（裁剪后）", f13, (60, 60, 60))
        # gap label
        gy = img_y + y_off + front_crop_h + gap_px // 2
        draw.line([lx, gy, lx + 30, gy], fill=(200, 160, 60), width=2)
        _draw_text(draw, (lx + 35, gy - 8), "间距 gap", f13, (60, 60, 60))
        # back card label
        by = img_y + y_off + front_crop_h + gap_px
        draw.line([lx, by + 10, lx + 30, by + 10], fill=(100, 180, 100), width=2)
        _draw_text(draw, (lx + 35, by + 4), "反面（裁剪后）", f13, (60, 60, 60))

    # info line
    info_y = img_y + target_mh + 22
    _draw_text(draw, (img_x, info_y), "画布: 1654 × 2338  |  左对齐  |  间距: 100px",
               f13, (120, 120, 120))

    # callout box for crop effect
    cl, ct = img_x, img_y + 8
    _draw_text(draw, (cl + 5, ct - 2), "  原始图片中的大量空白边距已被自动裁剪掉  ",
               make_font(12), (41, 128, 185))

    diagram.save(OUTPUT, "PNG")
    print(f"示意图已生成: {OUTPUT}")
    return OUTPUT


def main():
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.makedirs("docs", exist_ok=True)

    print("生成模拟身份证正面...")
    front = generate_front_card()
    front_path = os.path.join(TEMP_DIR, "front.jpg")
    front.save(front_path, "JPEG", quality=95)

    print("生成模拟身份证反面...")
    back = generate_back_card()
    back_path = os.path.join(TEMP_DIR, "back.jpg")
    back.save(back_path, "JPEG", quality=95)

    print("执行裁剪合并...")
    merged_path = merge_id_cards(
        front_path,
        back_path,
        output_path=os.path.join(TEMP_DIR, "merged.jpg"),
        gap=100,
        align="left",
        target_size=(1654, 2338),
        threshold=250,
    )

    print("组装演示示意图...")
    create_composite(front, back, merged_path)


if __name__ == "__main__":
    main()
