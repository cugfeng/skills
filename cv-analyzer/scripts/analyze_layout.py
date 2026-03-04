import cv2
import numpy as np
import sys
import json

def analyze_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print(json.dumps({"error": f"Failed to load {image_path}"}))
        sys.exit(1)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    # 1. Find Rectangles
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    rects = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 30 and h > 30: # Filter small noise
            area = cv2.contourArea(cnt)
            # Check if it's rectangular enough
            if area > w * h * 0.7:  
                rects.append({"x": x, "y": y, "w": w, "h": h})

    # Deduplicate rects
    final_rects = []
    for r in rects:
        duplicate = False
        for fr in final_rects:
            if abs(r["x"]-fr["x"]) < 10 and abs(r["y"]-fr["y"]) < 10 and abs(r["w"]-fr["w"]) < 10 and abs(r["h"]-fr["h"]) < 10:
                duplicate = True
                break
        if not duplicate:
            final_rects.append(r)
    
    # Sort rects
    final_rects.sort(key=lambda item: (item["y"] // 20, item["x"]))

    # 2. Extract Lines (Horizontal & Vertical)
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel)
    
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel)
    
    table_mask = cv2.add(horizontal_lines, vertical_lines)
    line_contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    lines = []
    for cnt in line_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 20 or h > 20: # It's a line
            # Determine if horizontal or vertical
            if w > h:
                lines.append({"type": "horizontal", "x1": x, "y1": y + h//2, "x2": x + w, "y2": y + h//2})
            else:
                lines.append({"type": "vertical", "x1": x + w//2, "y1": y, "x2": x + w//2, "y2": y + h})

    # 3. Extract Text Bounding Boxes
    text_mask = cv2.subtract(thresh, table_mask)
    text_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
    text_dilated = cv2.dilate(text_mask, text_kernel, iterations=1)
    text_contours, _ = cv2.findContours(text_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    texts = []
    for cnt in text_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 5 and h > 5:
            texts.append({
                "x": x, "y": y, "w": w, "h": h,
                "center_x": x + w//2, "center_y": y + h//2
            })
            
    texts.sort(key=lambda item: (item["y"] // 10, item["x"]))

    output = {
        "rectangles": final_rects,
        "lines": lines,
        "text_blocks": texts
    }
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python analyze_layout.py <image_path>"}))
        sys.exit(1)
    analyze_image(sys.argv[1])
