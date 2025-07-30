import cv2
import numpy as np
from scipy.interpolate import splprep, splev
import matplotlib.pyplot as plt

def smooth_contour_spline(contour, smooth_factor=300, num_points=300):
    if not np.all(contour[0] == contour[-1]):
        contour = np.vstack([contour, contour[0]])

    x, y = contour[:, 0], contour[:, 1]
    tck, _ = splprep([x, y], s=smooth_factor * len(contour), per=True)
    u_new = np.linspace(0, 1, num_points)
    x_new, y_new = splev(u_new, tck)
    return np.stack([x_new, y_new], axis=-1).astype(np.int32)

# === Charger une image binaire ou masque ===
image_path = r'C:\Users\TM273821\Desktop\Database\mask.png'
mask = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

_, thresh = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

if not contours:
    raise ValueError("❌ Aucun contour trouvé")

# === Extraire et lisser le plus grand contour ===
contour = max(contours, key=cv2.contourArea)
contour = contour[:, 0, :]  # (N, 1, 2) → (N, 2)

contour_smooth = smooth_contour_spline(contour, smooth_factor=10, num_points=300)

# === Affichage ===
plt.figure(figsize=(10, 5))
plt.imshow(mask, cmap='gray')
plt.plot(contour[:, 0], contour[:, 1], 'r-', label='Contour brut')
plt.plot(contour_smooth[:, 0], contour_smooth[:, 1], 'c-', linewidth=2, label='Contour lissé')
plt.legend()
plt.title("Interpolation spline du contour")
plt.axis('off')
plt.tight_layout()
plt.show()
