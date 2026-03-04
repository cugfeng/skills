import cv2
import numpy as np
import sys
import os

def compare_images(img1_path, img2_path, out_path):
    if not os.path.exists(img1_path) or not os.path.exists(img2_path):
        print(f"Error: Could not find images.")
        sys.exit(1)

    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)

    min_h = min(img1.shape[0], img2.shape[0])
    min_w = min(img1.shape[1], img2.shape[1])
    img1 = img1[:min_h, :min_w]
    img2 = img2[:min_h, :min_w]

    # Calculate absolute difference
    diff = cv2.absdiff(img1, img2)
    gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray_diff, 40, 255, cv2.THRESH_BINARY)
    
    # Analyze Red (Missing) vs Cyan (Extra)
    # Use bitwise logic to find specific missing/extra pixels
    img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    # Missing: pixel is dark in original but light in generated
    missing = cv2.threshold(cv2.subtract(img2_gray, img1_gray), 40, 255, cv2.THRESH_BINARY)[1]
    # Extra: pixel is light in original but dark in generated
    extra = cv2.threshold(cv2.subtract(img1_gray, img2_gray), 40, 255, cv2.THRESH_BINARY)[1]

    # Visual Overlay
    overlay = np.zeros_like(img1)
    overlay[:, :, 2] = img1[:, :, 2] # R from Original
    overlay[:, :, 1] = img2[:, :, 1] # G from Generated
    overlay[:, :, 0] = img2[:, :, 0] # B from Generated
    
    # Detect discrepancy regions
    kernel = np.ones((3,3), np.uint8)
    dilated = cv2.dilate(thresh, kernel, iterations=2)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    diff_count = 0
    small_detail_errors = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 5: # High sensitivity to small details like arrowheads
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(overlay, (x, y), (x+w, y+h), (0, 255, 255), 1)
            diff_count += 1
            if area < 150: small_detail_errors += 1
            
    cv2.imwrite(out_path, overlay)
    
    print(f"Comparison Result:")
    print(f"- Discrepancy Regions: {diff_count}")
    print(f"- Small Detail Errors (likely arrowheads/text): {small_detail_errors}")
    print(f"- Missing Pixels (RED): {np.sum(missing > 0)}")
    print(f"- Extra Pixels (CYAN): {np.sum(extra > 0)}")
    
    if diff_count > 0:
        print("\nCRITICAL: Visual discrepancies detected.")
        print("Note: If red/cyan clusters appear at line ends, your ARROWHEADS are misaligned or misshaped.")
        sys.exit(1)
    else:
        print("Perfect Match!")
        sys.exit(0)

if __name__ == "__main__":
    compare_images(sys.argv[1], sys.argv[2], sys.argv[3])
