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

    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]
    min_h = min(h1, h2)
    min_w = min(w1, w2)
    
    img1_cropped = img1[:min_h, :min_w]
    img2_cropped = img2[:min_h, :min_w]

    # Calculate differences
    diff = cv2.absdiff(img1_cropped, img2_cropped)
    gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray_diff, 50, 255, cv2.THRESH_BINARY)
    
    # Analyze Missing (Red) vs Extra (Cyan)
    # Missing: In original (img1) but not in generated (img2)
    missing_mask = cv2.subtract(cv2.cvtColor(img1_cropped, cv2.COLOR_BGR2GRAY), cv2.cvtColor(img2_cropped, cv2.COLOR_BGR2GRAY))
    _, missing_thresh = cv2.threshold(missing_mask, 50, 255, cv2.THRESH_BINARY)
    
    # Extra: In generated (img2) but not in original (img1)
    extra_mask = cv2.subtract(cv2.cvtColor(img2_cropped, cv2.COLOR_BGR2GRAY), cv2.cvtColor(img1_cropped, cv2.COLOR_BGR2GRAY))
    _, extra_thresh = cv2.threshold(extra_mask, 50, 255, cv2.THRESH_BINARY)

    # Color-coded overlay
    overlay = np.zeros_like(img1_cropped)
    overlay[:, :, 2] = img1_cropped[:, :, 2] # Red channel from Original
    overlay[:, :, 1] = img2_cropped[:, :, 1] # Green channel from Generated
    overlay[:, :, 0] = img2_cropped[:, :, 0] # Blue channel from Generated
    
    kernel = np.ones((5,5), np.uint8)
    dilated = cv2.dilate(thresh, kernel, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    diff_count = 0
    for contour in contours:
        if cv2.contourArea(contour) > 100:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(overlay, (x, y), (x+w, y+h), (0, 255, 255), 2)
            diff_count += 1
            
    cv2.imwrite(out_path, overlay)
    
    missing_pixels = np.sum(missing_thresh > 0)
    extra_pixels = np.sum(extra_thresh > 0)
    
    print(f"Comparison completed.")
    print(f"Total Discrepancy Regions: {diff_count}")
    print(f"Missing Content (RED pixels): {missing_pixels}")
    print(f"Extra/Redundant Content (CYAN pixels): {extra_pixels}")
    
    if diff_count > 0:
        if extra_pixels > missing_pixels * 2:
            print("WARNING: High Cyan count detected. You are likely drawing redundant lines or boxes not present in the original.")
        if missing_pixels > extra_pixels * 2:
            print("WARNING: High Red count detected. You have missed structural elements or text.")
        sys.exit(1)
    else:
        print("Perfect match (within tolerance)!")
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        compare_images(sys.argv[1], sys.argv[2], sys.argv[3])
