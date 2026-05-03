"""
Image Processing Pipeline
Handles image capture, processing, and feature extraction
"""

import cv2
import numpy as np
from PIL import Image
import base64
from pathlib import Path
from typing import Dict, Tuple, Optional, List
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Process images for medical analysis"""
    
    def __init__(self, target_size: Tuple[int, int] = (512, 512)):
        self.target_size = target_size
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.webp']
    
    def load_image(self, image_path: str) -> Optional[np.ndarray]:
        """Load image from file"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Cannot read image: {image_path}")
            return img
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            return None
    
    def load_from_bytes(self, image_bytes: bytes) -> Optional[np.ndarray]:
        """Load image from bytes"""
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            logger.error(f"Error loading image from bytes: {e}")
            return None
    
    def preprocess(self, image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Preprocess image: resize, normalize, enhance contrast
        Returns: processed image and original resized image
        """
        try:
            # Resize
            resized = cv2.resize(image, self.target_size)
            
            # Convert BGR to RGB
            rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            
            # Normalize to 0-1
            normalized = rgb.astype(np.float32) / 255.0
            
            # CLAHE for contrast enhancement
            lab = cv2.cvtColor((normalized * 255).astype(np.uint8), cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
            enhanced = enhanced.astype(np.float32) / 255.0
            
            return enhanced, rgb
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return None, None
    
    def extract_roi(self, image: np.ndarray, roi_type: str = "center") -> np.ndarray:
        """Extract region of interest"""
        try:
            h, w = image.shape[:2]
            if roi_type == "center":
                # Center 70% of image
                x1, y1 = int(w * 0.15), int(h * 0.15)
                x2, y2 = int(w * 0.85), int(h * 0.85)
            elif roi_type == "tongue":
                # Focus on lower part for tongue
                x1, y1 = int(w * 0.1), int(h * 0.3)
                x2, y2 = int(w * 0.9), int(h * 0.95)
            elif roi_type == "eye":
                # Focus on eye area
                x1, y1 = int(w * 0.2), int(h * 0.2)
                x2, y2 = int(w * 0.8), int(h * 0.8)
            else:
                return image
            
            roi = image[y1:y2, x1:x2]
            return cv2.resize(roi, self.target_size)
        except Exception as e:
            logger.error(f"Error extracting ROI: {e}")
            return image
    
    def to_base64(self, image: np.ndarray) -> str:
        """Convert image to base64 string for API transmission"""
        try:
            # Convert to PIL Image
            if image.dtype == np.float32 or image.dtype == np.float64:
                image = (image * 255).astype(np.uint8)
            
            if len(image.shape) == 3 and image.shape[2] == 3:
                # RGB to PIL
                pil_img = Image.fromarray(image.astype(np.uint8))
            else:
                pil_img = Image.fromarray(image)
            
            # Save to bytes
            import io
            buffer = io.BytesIO()
            pil_img.save(buffer, format="JPEG", quality=95)
            img_bytes = buffer.getvalue()
            
            # Encode to base64
            return base64.b64encode(img_bytes).decode('utf-8')
        except Exception as e:
            logger.error(f"Error converting image to base64: {e}")
            return ""
    
    def save_image(self, image: np.ndarray, output_path: str) -> bool:
        """Save processed image"""
        try:
            if image.dtype == np.float32 or image.dtype == np.float64:
                image = (image * 255).astype(np.uint8)
            
            if len(image.shape) == 3 and image.shape[2] == 3:
                # RGB to BGR for OpenCV
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            cv2.imwrite(output_path, image)
            return True
        except Exception as e:
            logger.error(f"Error saving image: {e}")
            return False
    
    def batch_process(self, image_paths: List[str]) -> Dict[str, np.ndarray]:
        """Process multiple images"""
        results = {}
        for path in image_paths:
            try:
                img = self.load_image(path)
                if img is not None:
                    processed, _ = self.preprocess(img)
                    results[Path(path).name] = processed
            except Exception as e:
                logger.error(f"Error processing {path}: {e}")
        
        return results


class MultiModalImageAnalyzer:
    """Analyze multiple body parts images"""
    
    def __init__(self):
        self.processor = ImageProcessor()
        self.body_parts = ["eye", "nails", "tongue"]
    
    def analyze_body_parts(self, image_dict: Dict[str, str]) -> Dict[str, np.ndarray]:
        """
        Process images of different body parts
        
        Args:
            image_dict: {"eye": path, "nails": path, "tongue": path}
        
        Returns:
            Dict of processed images with metadata
        """
        analysis = {}
        
        for part, image_path in image_dict.items():
            if part not in self.body_parts:
                continue
            
            try:
                # Load image
                img = self.processor.load_image(image_path)
                if img is None:
                    continue
                
                # Preprocess
                processed, rgb = self.processor.preprocess(img)
                
                # Extract ROI specific to body part
                roi = self.processor.extract_roi(processed, roi_type=part)
                
                # Convert to base64 for API
                b64 = self.processor.to_base64(roi)
                
                analysis[part] = {
                    "processed": roi,
                    "rgb": rgb,
                    "base64": b64,
                    "original_path": image_path,
                    "status": "processed"
                }
            except Exception as e:
                logger.error(f"Error analyzing {part}: {e}")
                analysis[part] = {"status": "error", "error": str(e)}
        
        return analysis
    
    def combine_for_analysis(self, analysis: Dict) -> np.ndarray:
        """
        Combine images of different body parts into a composite
        for comprehensive analysis
        """
        try:
            images = []
            for part in self.body_parts:
                if part in analysis and analysis[part].get("processed") is not None:
                    images.append(analysis[part]["processed"])
            
            if not images:
                return None
            
            # Vertical concatenation
            composite = np.vstack(images)
            return composite
        except Exception as e:
            logger.error(f"Error combining images: {e}")
            return None


# Convenience functions
def process_single_image(image_path: str) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    """Quick function to process a single image"""
    processor = ImageProcessor()
    img = processor.load_image(image_path)
    if img is None:
        return None, None
    return processor.preprocess(img)


def process_multipart(eye_path: str, nails_path: str, tongue_path: str) -> Dict:
    """Quick function to process all three body parts"""
    analyzer = MultiModalImageAnalyzer()
    return analyzer.analyze_body_parts({
        "eye": eye_path,
        "nails": nails_path,
        "tongue": tongue_path
    })
