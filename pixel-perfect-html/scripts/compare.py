import cv2
import numpy as np
import sys
import os

def compare_images(img1_path, img2_path, out_path):
    if not os.path.exists(img1_path) or not os.path.exists(img2_path):
        print(f"Error: Could not find one or both images: {img1_path}, {img2_path}")
        sys.exit(1)

    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)

    if img1 is None or img2 is None:
        print("Error loading images.")
        sys.exit(1)

    # Ensure sizes match exactly. If rendering size differs slightly, crop to the smallest common bounds.
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]
    min_h = min(h1, h2)
    min_w = min(w1, w2)
    
    img1_cropped = img1[:min_h, :min_w]
    img2_cropped = img2[:min_h, :min_w]

    # Calculate absolute difference
    diff = cv2.absdiff(img1_cropped, img2_cropped)
    
    # Convert difference to grayscale
    gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    
    # Thresholding: ignore small rendering differences (e.g. anti-aliasing pixels)
    # Difference > 50 in pixel intensity is considered a real discrepancy
    _, thresh = cv2.threshold(gray_diff, 50, 255, cv2.THRESH_BINARY)
    
    # Dilate the thresholded image to group nearby mismatched pixels into larger blobs
    kernel = np.ones((5,5), np.uint8)
    dilated = cv2.dilate(thresh, kernel, iterations=3)
    
    # Find contours of the discrepancies
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    img2_with_boxes = img2_cropped.copy()
    diff_count = 0
    
    for contour in contours:
        # Filter out extremely small, isolated noise (area < 100 pixels)
        if cv2.contourArea(contour) > 100:
            x, y, w, h = cv2.boundingRect(contour)
            # Draw a thick red bounding box around the discrepancy
            cv2.rectangle(img2_with_boxes, (x, y), (x+w, y+h), (0, 0, 255), 3)
            diff_count += 1
            
    # Save the highlighted result
    cv2.imwrite(out_path, img2_with_boxes)
    
    score = np.sum(thresh > 0) / (min_w * min_h)
    print(f"Comparison completed.")
    print(f"Percentage of mismatched pixels: {score * 100:.2f}%")
    print(f"Number of distinct discrepancy regions found: {diff_count}")
    
    # Return exit code based on differences found
    if diff_count > 0:
        print(f"Differences detected. Highlighted image saved to {out_path}.")
        sys.exit(1)
    else:
        print("No significant differences found! Perfect match.")
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python compare.py <original> <generated> <output_diff>")
        sys.exit(1)
    compare_images(sys.argv[1], sys.argv[2], sys.argv[3])
