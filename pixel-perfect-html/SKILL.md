---
name: pixel-perfect-html
description: A specialized workflow to precisely recreate an original image (like a diagram or UI) in HTML/SVG using an iterative visual diffing feedback loop. Use this whenever the user asks you to recreate an image as code.
---

# Pixel Perfect HTML

You are a specialized agent capable of recreating an image (like a diagram, UI screenshot, or chart) perfectly into HTML/SVG. You achieve high accuracy by writing code, rendering it in a headless browser, and automatically comparing it with the original image until the pixel differences are minimized.

## The Workflow

When asked to recreate an image:

1.  **Analyze the Original Image**
    - Read the image using `read_file`.
    - Check the dimensions of the original image using a command like `sips -g pixelWidth -g pixelHeight "image.png"` (on macOS) or `identify` (Linux/ImageMagick).

2.  **Generate Initial HTML/SVG**
    - Write an HTML file (`output.html`) containing HTML and/or SVG.
    - Match the original dimensions strictly.
    - Set absolute sizing to prevent layout shifts.
    - **Arrow markers**: When drawing lines with arrows, ensure the tips of the arrows point *away* from the line segment (outwards). For `marker-start`, define your marker with `orient="auto-start-reverse"` or ensure you handle marker orientations correctly so both arrow ends face outward from the line segment.

3.  **Render the HTML**
    - Use Google Chrome in headless mode to take a screenshot of your generated HTML file.
    - Make sure to specify the window size to match the original image exactly.
    - Command example (macOS):
      ```bash
      "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --screenshot=rendered.png --window-size=WIDTH,HEIGHT output.html
      ```
    - (Adjust path based on OS: `google-chrome` or `google-chrome-stable` on Linux).

4.  **Run Automated Visual Diff**
    - Use the provided comparison script to automatically diff the original image and the rendered output.
    - The script requires `opencv-python-headless` and `numpy`. Install them if needed (`pip install opencv-python-headless numpy --quiet`).
    - Command:
      ```bash
      python .gemini/skills/pixel-perfect-html/scripts/compare.py <original_image.png> rendered.png diff_result.png
      ```
    - The script will output the percentage of mismatched pixels, count of discrepancies, and exit with `1` if there are significant errors. 
    - It generates a **Color-Coded Overlay Diff** (`diff_result.png`) to help you debug structurally:
      - **RED**: Pixels present in the original but missing in your generated HTML.
      - **CYAN**: Pixels present in your generated HTML but NOT in the original (i.e., extra, misplaced, or incorrectly sized).
      - **GRAY/WHITE**: Perfect match.
      - **YELLOW BOXES**: Bounding boxes drawn around areas with significant differences.

5.  **Iterate and Fix**
    - If the script returns an error, use `read_file` to view `diff_result.png`.
    - Observe the yellow bounding boxes and the Red/Cyan overlay carefully.
    - **CRITICAL STRUCTURAL CHECK:** Don't just guess coordinate shifts. Look at the logical connections. If a red line goes to the corner of a box, but the cyan line goes to the middle of the edge, your SVG coordinates are structurally incorrect. Fix the math based on the SVG element sizes (e.g., if box top is y=360, the line must end at y2=360).
    - Use `replace` to adjust the HTML/SVG code (e.g., tweak X/Y coordinates, font sizes, padding).
    - Repeat steps 3 through 5 until the comparison script returns a successful match (Exit Code 0) or the differences are so negligible that the layout is functionally identical.

## Available Resources

- **`scripts/compare.py`**: A robust OpenCV script that calculates absolute visual differences, groups them, and draws bounding boxes around discrepancies to guide your debugging process.
