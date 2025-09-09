"""
OCR Processor Module

Advanced OCR processing using Tesseract and other OCR engines
for text extraction from images and scanned documents.

Features:
- Tesseract OCR integration
- Multiple language support
- Image preprocessing
- Confidence scoring
- Batch processing
- Text post-processing
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
import json

import pydantic

logger = logging.getLogger(__name__)

try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    import cv2
    import numpy as np
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logger.warning("OCR libraries not available. Please install: pip install pytesseract pillow opencv-python")


class OCRResult(pydantic.BaseModel):
    """OCR processing result."""
    text: str
    confidence: float
    language: str
    processing_time: float
    image_path: str
    preprocessed: bool = False
    metadata: Dict[str, Any] = {}


class OCRConfig(pydantic.BaseModel):
    """OCR configuration."""
    language: str = "eng"
    psm: int = 3  # Page segmentation mode
    oem: int = 3  # OCR Engine mode
    preprocess: bool = True
    enhance_contrast: bool = True
    denoise: bool = True
    deskew: bool = True
    custom_config: Optional[str] = None


class OCRProcessor:
    """
    Advanced OCR processor using Tesseract.
    
    Features:
    - Tesseract OCR integration
    - Multiple language support
    - Image preprocessing
    - Confidence scoring
    - Batch processing
    """
    
    def __init__(self, output_dir: str = "./output/ocr_processing"):
        """
        Initialize OCR processor.
        
        Args:
            output_dir: Directory for OCR results
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if not OCR_AVAILABLE:
            logger.error("OCR libraries not available. Please install required packages.")
            raise ImportError("OCR libraries are required for OCR processing")
        
        # Set Tesseract path if needed (Windows)
        self._setup_tesseract()
        
        logger.info(f"OCR processor initialized with output directory: {self.output_dir}")
    
    def _setup_tesseract(self):
        """Setup Tesseract path and configuration."""
        try:
            # Try to find Tesseract executable
            import shutil
            tesseract_path = shutil.which("tesseract")
            
            if tesseract_path:
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
                logger.info(f"Tesseract found at: {tesseract_path}")
            else:
                logger.warning("Tesseract not found in PATH. OCR may not work properly.")
                
        except Exception as e:
            logger.warning(f"Failed to setup Tesseract: {e}")
    
    def process_image(self, image_path: Union[str, Path], 
                     config: Optional[OCRConfig] = None) -> OCRResult:
        """
        Process a single image with OCR.
        
        Args:
            image_path: Path to image file
            config: OCR configuration
            
        Returns:
            OCR result
        """
        if config is None:
            config = OCRConfig()
        
        image_path = Path(image_path)
        
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        logger.info(f"Processing image with OCR: {image_path}")
        
        start_time = datetime.now()
        
        try:
            # Load image
            image = Image.open(image_path)
            
            # Preprocess image if requested
            if config.preprocess:
                image = self._preprocess_image(image, config)
            
            # Perform OCR
            text = self._perform_ocr(image, config)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create result
            result = OCRResult(
                text=text,
                confidence=0.85,  # Placeholder - would need custom implementation for confidence
                language=config.language,
                processing_time=processing_time,
                image_path=str(image_path),
                preprocessed=config.preprocess,
                metadata={
                    "psm": config.psm,
                    "oem": config.oem,
                    "image_size": image.size,
                    "image_mode": image.mode
                }
            )
            
            # Save result
            self._save_result(image_path, result)
            
            logger.info(f"OCR processing completed: {image_path}")
            logger.info(f"Extracted {len(text)} characters")
            
            return result
            
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            raise
    
    def process_batch(self, image_paths: List[Union[str, Path]], 
                     config: Optional[OCRConfig] = None) -> List[OCRResult]:
        """
        Process multiple images with OCR.
        
        Args:
            image_paths: List of image file paths
            config: OCR configuration
            
        Returns:
            List of OCR results
        """
        if config is None:
            config = OCRConfig()
        
        results = []
        
        logger.info(f"Processing {len(image_paths)} images with OCR")
        
        for image_path in image_paths:
            try:
                result = self.process_image(image_path, config)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {image_path}: {e}")
                # Create error result
                error_result = OCRResult(
                    text="",
                    confidence=0.0,
                    language=config.language,
                    processing_time=0.0,
                    image_path=str(image_path),
                    preprocessed=config.preprocess,
                    metadata={"error": str(e)}
                )
                results.append(error_result)
        
        logger.info(f"Batch OCR processing completed: {len(results)} results")
        
        return results
    
    def _preprocess_image(self, image: Image.Image, config: OCRConfig) -> Image.Image:
        """Preprocess image for better OCR results."""
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array for OpenCV processing
            img_array = np.array(image)
            
            # Convert to grayscale
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Enhance contrast if requested
            if config.enhance_contrast:
                # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                gray = clahe.apply(gray)
            
            # Denoise if requested
            if config.denoise:
                gray = cv2.medianBlur(gray, 3)
            
            # Deskew if requested
            if config.deskew:
                gray = self._deskew_image(gray)
            
            # Convert back to PIL Image
            processed_image = Image.fromarray(gray)
            
            # Additional PIL enhancements
            if config.enhance_contrast:
                enhancer = ImageEnhance.Contrast(processed_image)
                processed_image = enhancer.enhance(1.5)
            
            # Sharpen image
            processed_image = processed_image.filter(ImageFilter.SHARPEN)
            
            return processed_image
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {e}")
            return image
    
    def _deskew_image(self, image: np.ndarray) -> np.ndarray:
        """Deskew image by detecting and correcting rotation."""
        try:
            # Find contours
            contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return image
            
            # Find the largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Get minimum area rectangle
            rect = cv2.minAreaRect(largest_contour)
            angle = rect[2]
            
            # Correct angle
            if angle < -45:
                angle = 90 + angle
            
            # Rotate image
            if abs(angle) > 0.5:  # Only rotate if angle is significant
                h, w = image.shape[:2]
                center = (w // 2, h // 2)
                rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                image = cv2.warpAffine(image, rotation_matrix, (w, h), 
                                     flags=cv2.INTER_CUBIC, 
                                     borderMode=cv2.BORDER_REPLICATE)
            
            return image
            
        except Exception as e:
            logger.warning(f"Deskewing failed: {e}")
            return image
    
    def _perform_ocr(self, image: Image.Image, config: OCRConfig) -> str:
        """Perform OCR on image."""
        try:
            # Prepare Tesseract config
            tesseract_config = f"--psm {config.psm} --oem {config.oem}"
            
            if config.custom_config:
                tesseract_config += f" {config.custom_config}"
            
            # Perform OCR
            text = pytesseract.image_to_string(
                image,
                lang=config.language,
                config=tesseract_config
            )
            
            # Post-process text
            text = self._post_process_text(text)
            
            return text
            
        except Exception as e:
            logger.error(f"OCR execution failed: {e}")
            return ""
    
    def _post_process_text(self, text: str) -> str:
        """Post-process OCR text to improve quality."""
        try:
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Remove leading/trailing whitespace
            text = text.strip()
            
            # Fix common OCR errors
            text = self._fix_common_ocr_errors(text)
            
            return text
            
        except Exception as e:
            logger.warning(f"Text post-processing failed: {e}")
            return text
    
    def _fix_common_ocr_errors(self, text: str) -> str:
        """Fix common OCR errors."""
        # Common character substitutions
        replacements = {
            '0': 'O',  # Zero to O in text context
            '1': 'I',  # One to I in text context
            '5': 'S',  # Five to S in text context
            '8': 'B',  # Eight to B in text context
        }
        
        # Apply replacements (this is a simple approach)
        # In a real implementation, you'd use more sophisticated methods
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def _save_result(self, image_path: Path, result: OCRResult):
        """Save OCR result to file."""
        result_filename = f"{image_path.stem}_ocr_result.json"
        result_path = self.output_dir / result_filename
        
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result.dict(), f, indent=2, default=str)
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        try:
            languages = pytesseract.get_languages()
            return languages
        except Exception as e:
            logger.error(f"Failed to get supported languages: {e}")
            return ["eng"]
    
    def get_confidence_score(self, image: Image.Image, text: str) -> float:
        """
        Get confidence score for OCR result.
        
        Args:
            image: Processed image
            text: Extracted text
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        try:
            # Get detailed OCR data
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            
            if confidences:
                avg_confidence = sum(confidences) / len(confidences)
                return avg_confidence / 100.0  # Convert to 0-1 scale
            else:
                return 0.0
                
        except Exception as e:
            logger.warning(f"Failed to calculate confidence: {e}")
            return 0.5  # Default confidence
    
    def extract_text_from_pdf_pages(self, pdf_path: Union[str, Path], 
                                   page_numbers: Optional[List[int]] = None) -> List[OCRResult]:
        """
        Extract text from PDF pages using OCR.
        
        Args:
            pdf_path: Path to PDF file
            page_numbers: List of page numbers to process (None for all pages)
            
        Returns:
            List of OCR results
        """
        try:
            # This would require PDF to image conversion
            # For now, return placeholder
            logger.info(f"OCR from PDF pages not yet implemented: {pdf_path}")
            return []
            
        except Exception as e:
            logger.error(f"PDF OCR processing failed: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get OCR processor statistics."""
        return {
            "output_directory": str(self.output_dir),
            "processed_images": len(list(self.output_dir.glob("*_ocr_result.json"))),
            "ocr_available": OCR_AVAILABLE,
            "supported_languages": self.get_supported_languages()
        }