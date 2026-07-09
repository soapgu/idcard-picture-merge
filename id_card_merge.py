#!/usr/bin/env python3
"""
身份证正反面合并脚本

将两张身份证图片（正反面）裁剪掉四周空白，合并到一张图片中，
保持原始尺寸（1654×2338），内容不缩放。

用法:
    python id_card_merge.py <正面图片> <反面图片> [选项]

选项:
    -o, --output PATH   输出路径 (默认: id_card_merged.jpg)
    -g, --gap PX        上下间距像素 (默认: 100)
    -a, --align {left,center} 对齐方式 (默认: left)
    -t, --target WxH    目标画布尺寸 (默认: 1654x2338)
    --threshold VAL     检测内容边界的亮度阈值 (默认: 250)
"""

import argparse
from PIL import Image


def find_content_bounds(img, threshold=250):
    """找到图片中非空白内容的边界"""
    gray = img.convert('L')
    w, h = img.size
    px = gray.load()

    # 每行平均亮度，用滑动平均找内容区域
    row_avg = []
    for y in range(h):
        s = sum(px[x, y] for x in range(w))
        row_avg.append(s / w)

    window = 20
    smooth = []
    for y in range(h):
        start = max(0, y - window)
        end = min(h, y + window + 1)
        smooth.append(sum(row_avg[start:end]) / (end - start))

    diffs = [smooth[y] - row_avg[y] for y in range(h)]
    max_diff = max(diffs)
    thresh = max_diff * 0.3

    top = next(y for y in range(h) if diffs[y] > thresh)
    bottom = next(y for y in range(h - 1, -1, -1) if diffs[y] > thresh)

    left = next(
        x for x in range(w) if any(px[x, y] < threshold for y in range(top, bottom + 1))
    )
    right = next(
        x
        for x in range(w - 1, -1, -1)
        if any(px[x, y] < threshold for y in range(top, bottom + 1))
    )

    # 向外扩展 padding，避免切到内容边缘
    padding = 45
    left = max(0, left - padding)
    top = max(0, top - padding)
    right = min(w - 1, right + padding)
    bottom = min(h - 1, bottom + padding)

    return left, top, right, bottom


def merge_id_cards(
    front_path,
    back_path,
    output_path="id_card_merged.jpg",
    gap=100,
    align="left",
    target_size=(1654, 2338),
    threshold=250,
):
    target_w, target_h = target_size

    cropped = []
    for fp in (front_path, back_path):
        img = Image.open(fp)
        left, top, right, bottom = find_content_bounds(img, threshold)
        crop = img.crop((left, top, right + 1, bottom + 1))
        cropped.append(crop)
        print(f"  {fp}: 裁剪 ({left},{top})-({right},{bottom}) -> {crop.size}")

    max_w = max(c.size[0] for c in cropped)

    if align == "left":
        x_off = (target_w - max_w) // 2
    else:
        x_off = None  # 每个图片单独居中

    total_h = cropped[0].size[1] + gap + cropped[1].size[1]
    merged = Image.new("RGB", (target_w, target_h), (255, 255, 255))
    y_off = (target_h - total_h) // 2
    x_off = (target_w - max_w) // 2

    for c in cropped:
        if align == "center":
            x_off = (target_w - c.size[0]) // 2
        merged.paste(c, (x_off, y_off))
        y_off += c.size[1] + gap

    merged.save(output_path, "JPEG", quality=95)
    print(f"  输出: {output_path} ({merged.size}), 间距={gap}px, 对齐={align}")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="身份证正反面合并")
    parser.add_argument("front", help="正面图片路径")
    parser.add_argument("back", help="反面图片路径")
    parser.add_argument("-o", "--output", default="id_card_merged.jpg", help="输出路径")
    parser.add_argument("-g", "--gap", type=int, default=100, help="上下间距 (默认: 100)")
    parser.add_argument(
        "-a",
        "--align",
        choices=["left", "center"],
        default="left",
        help="对齐方式 (默认: left)",
    )
    parser.add_argument(
        "-t",
        "--target",
        default="1654x2338",
        help="目标画布尺寸 宽x高 (默认: 1654x2338)",
    )
    parser.add_argument("--threshold", type=int, default=250, help="内容检测阈值 (默认: 250)")

    args = parser.parse_args()
    target = tuple(map(int, args.target.split("x")))

    merge_id_cards(
        args.front,
        args.back,
        args.output,
        args.gap,
        args.align,
        target,
        args.threshold,
    )
