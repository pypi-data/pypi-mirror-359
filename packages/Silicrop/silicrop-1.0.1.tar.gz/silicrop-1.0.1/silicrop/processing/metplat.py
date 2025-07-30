import cv2
import numpy as np
from scipy.spatial import cKDTree
import matplotlib.pyplot as plt

class FlatSegmentDetector:
    def __init__(self, contour, init_window=500, max_dist=2.0):
        """
        contour : ndarray de forme (N, 2)
        init_window : taille initiale du segment droit
        max_dist : tolérance de distance pour l'adhérence au contour
        """
        self.contour = contour
        self.N = len(contour)
        self.init_window = init_window
        self.max_dist = max_dist
        self.mask = np.zeros(self.N, dtype=bool)
        self.start_idx = None
        self.end_idx = None

        self._tree = cKDTree(contour)
        self._detect_flat_segment()

    def _is_close_to_contour(self, line):
        dists, _ = self._tree.query(line)
        return np.all(dists < self.max_dist)

    def _detect_flat_segment(self):
        for i in range(self.N - self.init_window):
            seg = self.contour[i:i + self.init_window]
            line = np.linspace(seg[0], seg[-1], num=self.init_window)
            if self._is_close_to_contour(line):
                self.start_idx = i
                self.end_idx = i + self.init_window
                break

        if self.start_idx is None:
            return

        max_iter = 2000
        count = 0
        while self.start_idx > 0 and count < max_iter:
            line = np.linspace(
                self.contour[self.start_idx - 1],
                self.contour[self.end_idx - 1],
                self.end_idx - self.start_idx + 1
            )
            if self._is_close_to_contour(line):
                self.start_idx -= 1
            else:
                break
            count += 1

        # Extension à droite
        count = 0
        while self.end_idx < self.N - 1 and count < max_iter:
            line = np.linspace(
                self.contour[self.start_idx],
                self.contour[self.end_idx + 1],
                self.end_idx - self.start_idx + 2
            )
            if self._is_close_to_contour(line):
                self.end_idx += 1
            else:
                break
            count += 1

        self.mask[self.start_idx:self.end_idx] = True

    def get_mask(self):
        return self.mask

    def get_endpoints(self):
        if self.start_idx is None or self.end_idx is None:
            return None, None
        return (
            tuple(self.contour[self.start_idx]),
            tuple(self.contour[self.end_idx - 1])
        )


# === Test autonome ===
if __name__ == "__main__":
    # === 1. Charger l'image ===
    image_path = r'C:\Users\TM273821\Desktop\Database\200\Masque_plat\98.png'
    mask = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if mask is None:
        raise FileNotFoundError(f"Image non trouvée : {image_path}")
    
    _, thresh = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)

    # === 2. Extraire le contour principal ===
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contour = max(contours, key=cv2.contourArea)
    contour = contour[:, 0, :]  # (N, 1, 2) → (N, 2)

    # === 3. Détection du méplat ===
    detector = FlatSegmentDetector(contour, init_window=500, max_dist=2.0)
    flat_mask = detector.get_mask()
    pt1, pt2 = detector.get_endpoints()
    print("Extrémités du méplat :", pt1, pt2)

    # === 4. Séparer méplat et courbe ===
    contour_flat = contour[flat_mask]
    contour_curved = contour[~flat_mask]

    # === 5. Fit ellipse sur la partie courbe ===
    def fit_ellipse(points):
        if len(points) < 5:
            return None
        return cv2.fitEllipse(points.astype(np.float32).reshape(-1, 1, 2))

    ellipse = fit_ellipse(contour_curved)

    # === 6. Affichage matplotlib ===
    output = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    if ellipse:
        cv2.ellipse(output, ellipse, (0, 255, 0), 2)

    plt.figure(figsize=(8, 8))
    plt.imshow(output[..., ::-1])
    if len(contour_curved) > 0:
        plt.scatter(contour_curved[:, 0], contour_curved[:, 1], s=1, c='green', label="Courbe utilisée")
    if len(contour_flat) > 0:
        plt.scatter(contour_flat[:, 0], contour_flat[:, 1], s=3, c='red', label="Méplat exclu")
    plt.legend()
    plt.title("Fit elliptique excluant le méplat")
    plt.axis('equal')
    plt.axis('off')
    plt.show()
