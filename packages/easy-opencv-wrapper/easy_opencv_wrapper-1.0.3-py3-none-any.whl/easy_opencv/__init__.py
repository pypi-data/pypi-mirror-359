"""
Easy OpenCV - A simplified wrapper for OpenCV functions

A powerful yet user-friendly OpenCV wrapper that makes computer vision 
accessible for everyone. Provides streamlined interface to perform 
complex computer vision operations with simple, intuitive function calls.

Author: Aksh Agrawal
License: MIT
Homepage: https://github.com/aksh-github/easy-opencv-wrapper
"""

# Import all modules
from . import image_operations
from . import video_operations
from . import image_processing
from . import feature_detection
from . import object_detection
from . import drawing_operations
from . import filters
from . import transformations
from . import utils

# Import new object detection classes for direct access
from .object_detection import (
    ImageSource, FaceDetector, EyeDetector, CascadeDetector, 
    MotionDetector, CircleDetector, LineDetector, ColorDetector, 
    DNNObjectDetector
)

# Import new image operations classes for direct access
from .image_operations import (
    ImageLoader, ImageSaver, ImageDisplayer, ImageResizer,
    ImageCropper, ColorSpaceConverter, ImageAnalyzer
)

# Import new video operations classes for direct access
from .video_operations import (
    VideoLoader, VideoSaver, VideoPlayer, FrameExtractor,
    VideoAnalyzer, WebcamCapture
)

__version__ = "1.0.3"
__author__ = "Aksh Agrawal"
__email__ = "akshagr10@gmail.com"
__license__ = "MIT"
__description__ = "A simplified and intuitive OpenCV wrapper that reduces code complexity by 50-70%"

# Package metadata
__all__ = [
    'cv',
    'EasyCV',
    # Object Detection Classes
    'ImageSource',
    'FaceDetector', 
    'EyeDetector',
    'CascadeDetector',
    'MotionDetector',
    'CircleDetector', 
    'LineDetector',
    'ColorDetector',
    'DNNObjectDetector',
    # Image Operation Classes
    'ImageLoader',
    'ImageSaver',
    'ImageDisplayer',
    'ImageResizer',
    'ImageCropper',
    'ColorSpaceConverter',
    'ImageAnalyzer',
    # Video Operation Classes
    'VideoLoader',
    'VideoSaver',
    'VideoPlayer',
    'FrameExtractor',
    'VideoAnalyzer',
    'WebcamCapture',
    # Package metadata
    '__version__',
    '__author__',
    '__email__',
    '__license__',
    '__description__',
]

# Main class for easy access to all functions
class EasyCV:
    """
    Main class that provides easy access to all OpenCV functions
    with simplified arguments and customizable parameters.
    """
    
    def __init__(self):
        # Import all functions from modules and assign them as methods
        
        # Image Operations
        self.load_image = image_operations.load_image
        self.save_image = image_operations.save_image
        self.show_image = image_operations.show_image
        self.resize_image = image_operations.resize_image
        self.crop_image = image_operations.crop_image
        self.convert_color_space = image_operations.convert_color_space
        self.get_image_info = image_operations.get_image_info
        
        # Video Operations (Legacy functions)
        self.load_video = video_operations.load_video
        self.save_video = video_operations.save_video
        self.extract_frames = video_operations.extract_frames
        self.create_video_from_frames = video_operations.create_video_from_frames
        self.get_video_info = video_operations.get_video_info
        self.play_video = video_operations.play_video
        self.webcam_capture = video_operations.webcam_capture
        
        # Video Operation Classes (New)
        self.VideoLoader = video_operations.VideoLoader
        self.VideoSaver = video_operations.VideoSaver
        self.VideoPlayer = video_operations.VideoPlayer
        self.FrameExtractor = video_operations.FrameExtractor
        self.VideoAnalyzer = video_operations.VideoAnalyzer
        self.WebcamCapture = video_operations.WebcamCapture
        
        # Image Processing
        self.apply_blur = image_processing.apply_blur
        self.apply_sharpen = image_processing.apply_sharpen
        self.apply_edge_detection = image_processing.apply_edge_detection
        self.apply_threshold = image_processing.apply_threshold
        self.apply_morphology = image_processing.apply_morphology
        self.apply_histogram_equalization = image_processing.apply_histogram_equalization
        self.adjust_brightness_contrast = image_processing.adjust_brightness_contrast
        self.apply_gamma_correction = image_processing.apply_gamma_correction
        
        # Feature Detection
        self.detect_corners = feature_detection.detect_corners
        self.detect_keypoints = feature_detection.detect_keypoints
        self.match_features = feature_detection.match_features
        self.detect_contours = feature_detection.detect_contours
        self.find_shapes = feature_detection.find_shapes
        self.template_matching = feature_detection.template_matching
        
        # Object Detection (Legacy functions)
        self.detect_faces = object_detection.detect_faces
        self.detect_eyes = object_detection.detect_eyes
        self.detect_objects_cascade = object_detection.detect_objects_cascade
        self.background_subtraction = object_detection.background_subtraction
        self.detect_motion = object_detection.detect_motion
        self.detect_circles = object_detection.detect_circles
        self.detect_lines = object_detection.detect_lines
        self.color_detection = object_detection.color_detection
        self.detect_objects_dnn = object_detection.detect_objects_dnn
        
        # Object Detection Classes (New)
        self.ImageSource = object_detection.ImageSource
        self.FaceDetector = object_detection.FaceDetector
        self.EyeDetector = object_detection.EyeDetector
        self.CascadeDetector = object_detection.CascadeDetector
        self.MotionDetector = object_detection.MotionDetector
        self.CircleDetector = object_detection.CircleDetector
        self.LineDetector = object_detection.LineDetector
        self.ColorDetector = object_detection.ColorDetector
        self.DNNObjectDetector = object_detection.DNNObjectDetector

        # Drawing Operations
        self.draw_rectangle = drawing_operations.draw_rectangle
        self.draw_circle = drawing_operations.draw_circle
        self.draw_line = drawing_operations.draw_line
        self.draw_text = drawing_operations.draw_text
        self.draw_polygon = drawing_operations.draw_polygon
        self.draw_contour = drawing_operations.draw_contour
        self.draw_arrow = drawing_operations.draw_arrow
        self.draw_grid = drawing_operations.draw_grid
        self.draw_crosshair = drawing_operations.draw_crosshair
        self.draw_bounding_boxes = drawing_operations.draw_bounding_boxes
        
        # Filters
        self.apply_gaussian_blur = filters.apply_gaussian_blur
        self.apply_median_blur = filters.apply_median_blur
        self.apply_bilateral_filter = filters.apply_bilateral_filter
        self.apply_custom_kernel = filters.apply_custom_kernel
        self.apply_noise_reduction = filters.apply_noise_reduction
        self.apply_emboss_filter = filters.apply_emboss_filter
        self.apply_edge_enhance_filter = filters.apply_edge_enhance_filter
        self.apply_unsharp_mask = filters.apply_unsharp_mask
        self.apply_high_pass_filter = filters.apply_high_pass_filter
        self.apply_motion_blur = filters.apply_motion_blur
        self.apply_vintage_filter = filters.apply_vintage_filter
        self.apply_cartoon_filter = filters.apply_cartoon_filter
        
        # Transformations
        self.rotate_image = transformations.rotate_image
        self.flip_image = transformations.flip_image
        self.translate_image = transformations.translate_image
        self.apply_perspective_transform = transformations.apply_perspective_transform
        self.apply_affine_transform = transformations.apply_affine_transform
        self.warp_image = transformations.warp_image
        self.apply_barrel_distortion = transformations.apply_barrel_distortion
        self.apply_fisheye_effect = transformations.apply_fisheye_effect
        self.resize_with_aspect_ratio = transformations.resize_with_aspect_ratio
        
        # Utilities
        self.create_trackbar = utils.create_trackbar
        self.mouse_callback = utils.mouse_callback
        self.set_mouse_callback = utils.set_mouse_callback
        self.fps_counter = utils.fps_counter
        self.color_picker = utils.color_picker
        self.image_comparison = utils.image_comparison
        self.create_image_grid = utils.create_image_grid
        self.apply_watermark = utils.apply_watermark
        self.convert_to_sketch = utils.convert_to_sketch
        self.auto_canny = utils.auto_canny
        self.download_file = utils.download_file

# Create a global instance for easy access
cv = EasyCV()
