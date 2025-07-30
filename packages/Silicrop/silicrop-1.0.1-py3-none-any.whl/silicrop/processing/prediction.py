import torch
import numpy as np
import cv2
import time
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image, ImageOps
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse as MplEllipse
import segmentation_models_pytorch as smp
import psutil
from silicrop.processing.metplat import FlatSegmentDetector
import os
import math
from scipy.interpolate import splprep, splev


def smooth_contour_spline(contour, smooth_factor=0.01, num_points=1000):
    """
    Applique une interpolation spline lisse à un contour (Nx2).
    - smooth_factor : contrôle la tension (plus haut = plus lisse)
    - num_points : nombre de points interpolés à générer
    """
    # Fermer le contour si non fermé
    if not np.all(contour[0] == contour[-1]):
        contour = np.vstack([contour, contour[0]])

    x, y = contour[:, 0], contour[:, 1]
    
    # Interpolation spline paramétrique
    tck, _ = splprep([x, y], s=smooth_factor * len(contour), per=True)
    u_new = np.linspace(0, 1, num_points)
    x_new, y_new = splev(u_new, tck)
    
    contour_smooth = np.stack([x_new, y_new], axis=-1).astype(np.int32)
    return contour_smooth

class EllipsePredictor:
    def __init__(self, model_path):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # ✅ Initialise le modèle avec EfficientNet-B0
        self.model = smp.Unet(
            encoder_name="efficientnet-b0",
            encoder_weights="imagenet",
            in_channels=3,
            classes=1
        ).to(self.device)

        # ✅ Charge les poids entraînés
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
        ])

        self.process = psutil.Process()

    def predict_mask(self, img_pil):
        img_pil = ImageOps.exif_transpose(img_pil)
        img_rgb = np.array(img_pil)
        if img_rgb.shape[2] != 3:
            img_rgb = cv2.cvtColor(img_rgb, cv2.COLOR_GRAY2RGB)

        x = self.transform(Image.fromarray(img_rgb)).unsqueeze(0).to(self.device)

        with torch.no_grad():
            out = self.model(x)
            pred = torch.sigmoid(out)
            mask = (pred > 0.5).float()

        return mask.squeeze().cpu().numpy()

    def fit_and_warp(self, img_array, mask):
        h, w = img_array.shape[:2]
        mask_bin = (mask > 0.5).astype(np.uint8) * 255
        mask_resized = cv2.resize(mask_bin, (w, h), interpolation=cv2.INTER_NEAREST)
        contours, _ = cv2.findContours(mask_resized, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours or len(max(contours, key=cv2.contourArea)) < 5:
            print("Ellipse fitting failed")
            return None

        ellipse = cv2.fitEllipse(max(contours, key=cv2.contourArea))
        (cx, cy), (MA, ma), angle = ellipse

        mask_ellipse = np.zeros((h, w), np.uint8)
        cv2.ellipse(mask_ellipse, (int(cx), int(cy)), (int(MA / 2), int(ma / 2)), angle, 0, 360, 255, -1)

        diameter = int(max(MA, ma))
        box = cv2.boxPoints(ellipse).astype(np.float32)
        target = np.array([[0, 0], [diameter - 1, 0], [diameter - 1, diameter - 1], [0, diameter - 1]], np.float32)
        M = cv2.getPerspectiveTransform(box, target)

        warped = cv2.warpPerspective(img_array, M, (diameter, diameter))
        warped_mask = cv2.warpPerspective(mask_ellipse, M, (diameter, diameter))

        white_bg = np.ones_like(warped, np.uint8) * 255
        for c in range(3):
            white_bg[:, :, c] = np.where(warped_mask == 255, warped[:, :, c], 255)

        return white_bg

    def run_inference(self, img_path, dataset_type='200', plot=True):
        mem_before = self.process.memory_info().rss / 1024 ** 2

        img_pil = Image.open(img_path).convert('RGB')
        img_pil = ImageOps.exif_transpose(img_pil)
        orig_img = np.array(img_pil)
        orig_img = cv2.cvtColor(orig_img, cv2.COLOR_RGB2BGR)

        start_time = time.time()
        mask = self.predict_mask(img_pil)

        elapsed = time.time() - start_time
        mem_after = self.process.memory_info().rss / 1024 ** 2

        h, w = orig_img.shape[:2]
        mask_bin = (mask > 0.5).astype(np.uint8) * 255
        mask_resized = cv2.resize(mask_bin, (w, h), interpolation=cv2.INTER_NEAREST)
        _, mask_thresh = cv2.threshold(mask_resized, 127, 255, cv2.THRESH_BINARY)
        kernel = np.ones((5,5), np.uint8)
        mask_clean = cv2.morphologyEx(mask_thresh, cv2.MORPH_CLOSE, kernel)
        mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if not contours:
            print("❌ Aucun contour détecté.")
            return None, None, None

        contour = max(contours, key=cv2.contourArea)
        contour = contour[:, 0, :]  # (N, 1, 2) → (N, 2)
        contour= self.smooth_contour_spline(contour, smooth_factor=5, num_points=300)

      
        # contour = smooth_contour_spline(contour, smooth_factor=0.01, num_points=1500)
        if dataset_type == '150':
            detector = FlatSegmentDetector(
                contour,
                init_window=500,
                max_dist=2
            )

            mask_flat = detector.get_mask()
            flat_part = contour[mask_flat]
            curved_part = contour[~mask_flat]
            show_flat = True

            if len(curved_part) < 5:
                print("❌ Pas assez de points pour ellipse (150).")
                return None, mask, None
            ellipse = cv2.fitEllipse(curved_part.reshape(-1, 1, 2))
        else:
            if len(contour) < 5:
                print("❌ Pas assez de points pour ellipse (200).")
                return None, mask, None
            ellipse = cv2.fitEllipse(contour.reshape(-1, 1, 2))

        result_img = self.fit_and_warp(orig_img, mask)
        if result_img is None:
            print("❌ Transformation échouée.")
            return None, mask, ellipse

        if plot:
            plt.figure(figsize=(12, 5))

            plt.subplot(1, 3, 1)
            plt.title("Image d'origine")
            plt.imshow(cv2.cvtColor(orig_img, cv2.COLOR_BGR2RGB))
            plt.axis('off')

            plt.subplot(1, 3, 2)
            plt.title("Mask + ellipse")
            plt.imshow(mask_resized, cmap='gray')
            ax = plt.gca()
            (cx, cy), (MA, ma), angle = ellipse
            ell_patch = MplEllipse((cx, cy), MA, ma, angle=angle, edgecolor='red', facecolor='none', linewidth=2)
            ax.add_patch(ell_patch)

            if show_flat and flat_part is not None and len(flat_part) > 0:
                plt.scatter(flat_part[:, 0], flat_part[:, 1], s=5, c='cyan', label='Méplat')
                plt.legend()

            plt.axis('off')

            plt.subplot(1, 3, 3)
            plt.title("Image transformée")
            plt.imshow(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB))
            plt.axis('off')

            plt.tight_layout()
            plt.show()

        print(f"✅ Inference: {elapsed:.3f}s | RAM: {mem_after - mem_before:.2f}MB")

        # Sauvegarde du masque pour analyse
        debug_mask_path = r'C:\Users\TM273821\mask.png'
        cv2.imwrite(debug_mask_path, mask_clean)
        print(f"💾 Masque sauvegardé dans : {debug_mask_path}")
        return result_img, mask, ellipse
    
    def smooth_contour_spline(self, contour, smooth_factor=300, num_points=300):
        if not np.all(contour[0] == contour[-1]):
            contour = np.vstack([contour, contour[0]])

        x, y = contour[:, 0], contour[:, 1]
        tck, _ = splprep([x, y], s=smooth_factor * len(contour), per=True)
        u_new = np.linspace(0, 1, num_points)
        x_new, y_new = splev(u_new, tck)
        return np.stack([x_new, y_new], axis=-1).astype(np.int32)
# ==== Test ====
if __name__ == "__main__":
    model_path = r"C:\Users\TM273821\Desktop\Silicrop - Database\Model\Model_200.pth"
    img_path = r"C:\Users\TM273821\Desktop\Database\200\Image\1.jpg"

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"❌ Modèle non trouvé : {model_path}")
    if not os.path.exists(img_path):
        raise FileNotFoundError(f"❌ Image non trouvée : {img_path}")

    predictor = EllipsePredictor(model_path)
    result_img, mask, ellipse = predictor.run_inference(img_path, dataset_type='150', plot=True)

