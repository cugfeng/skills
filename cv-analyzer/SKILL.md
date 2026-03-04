---
name: cv-analyzer
description: OpenCV-based computer vision analysis tool to extract bounding boxes, lines, and text regions from an image. Use this to automatically get precise x, y, width, height coordinates before recreating UI/diagrams in HTML/SVG.
---

# Computer Vision Image Analyzer

This skill uses OpenCV to analyze a source image and return a structured JSON output of its geometric shapes and text regions. This provides deterministic coordinates (`x`, `y`, `w`, `h`) to make recreating the image in HTML/SVG pixel-perfect from the start.

## The Workflow

When you need to exactly recreate an image as code:

1. **Run the Analyzer**
   Before guessing coordinates, run the provided analysis script on the source image:
   ```bash
   python .gemini/skills/cv-analyzer/scripts/analyze_layout.py <path_to_image.png>
   ```

2. **Analyze the Output**
   The script outputs a JSON object containing three lists:
   - `rectangles`: Bounding boxes of borders and containers (`x`, `y`, `w`, `h`).
   - `lines`: Separator lines and arrows (`x1`, `y1`, `x2`, `y2`).
   - `text_blocks`: Coordinates and computed center points (`center_x`, `center_y`) of text regions.

3. **Apply to Code**
   Use these precise coordinates directly in your SVG `<rect>`, `<line>`, or `<text>` tags. 
   - For text elements, the `center_x` and `center_y` properties are highly recommended to use in combination with CSS `text-anchor: middle;` and `alignment-baseline: central;` to perfectly align text, regardless of font rendering differences.

## Available Resources

- **`scripts/analyze_layout.py`**: An OpenCV script that performs morphological operations and contour detection to extract precise geometry and text bounding boxes from an image. It handles noise filtering and deduplication automatically.
