import sys
import os
import json
import glob
import torch
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import time
import traceback
import colorsys

# --- Core SAM2 dependencies ---
try:
    from sam2.build_sam import build_sam2
    from sam2.sam2_image_predictor import SAM2ImagePredictor

    print("Successfully imported SAM2 components.")
except ImportError as e:
    print(f"Failed to import SAM2 components: {e}", file=sys.stderr)
    print("Error: Could not import the 'sam2' library. Please ensure you have installed it as per the instructions in README.md, for example:", file=sys.stderr)
    print("pip install git+https://github.com/facebookresearch/segment-anything-2.git", file=sys.stderr)
    sys.exit(1)

# Default annotation labels
DEFAULT_LABELS = ["_background_", "Cropland", "Forest", "Grass", "Shrub", "Wetland", "Water", "Solar panel",
                  "Impervious surface", "Bareland", "Ice/snow", "desert"]


class InteractiveSAM2Annotator(tk.Tk):
    """
    An interactive annotation tool using SAM2 for image segmentation.
    Allows users to load images, apply SAM2 predictions, draw polygons,
    and save annotations in LabelMe JSON format.
    """

    def __init__(self, model_path, config_path=None, device=None, output_dir="./annotations", image_dir=None):
        """
        Initializes the interactive SAM2 annotator application.

        Args:
            model_path (str): Path to the SAM2 model checkpoint.
            config_path (str, optional): Path to the SAM2 model configuration file.
                                         If None, a default config will be inferred based on model_path.
            device (torch.device, optional): Device to run the model on (e.g., 'cuda', 'cpu').
                                             Defaults to 'cuda' if available, otherwise 'cpu'.
            output_dir (str, optional): Directory to save annotations. Defaults to "./annotations".
            image_dir (str, optional): Initial directory to load images from. Defaults to None.
        """
        super().__init__()

        # Determine the device for model inference
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu") if device is None else device
        print(f"Using device: {self.device}")

        # Set up output directories for annotations
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.last_session_file = os.path.join(self.output_dir, "last_session_state.json")

        self.dataset_dir = os.path.join(output_dir, "datasets")
        self.jpgs_path = os.path.join(self.dataset_dir, "JPEGImages")
        self.jsons_path = os.path.join(self.dataset_dir, "before")  # JSON annotations
        self.pngs_path = os.path.join(self.dataset_dir, "SegmentationClass")  # Segmentation masks
        os.makedirs(self.jpgs_path, exist_ok=True)
        os.makedirs(self.jsons_path, exist_ok=True)
        os.makedirs(self.pngs_path, exist_ok=True)

        # Load SAM2 model (model itself remains constant)
        self.model = None  # Pre-declare as None
        self.load_model(model_path, config_path)  # Load the model into self.model

        # SAM predictor instance (key change: SAM2ImagePredictor is NOT initialized here)
        self.predictor = None  # Initialize SAM predictor instance to None, will be created dynamically in load_current_image

        # --- State variables ---
        # Image-related state
        self.image_paths = []
        self.current_image_index = -1
        self.image_np = None  # NumPy array of the current image
        self.image_name = ""
        self.image_list_loaded = False
        self.display_img = None  # Image ready for display (with overlays)
        self.current_loaded_image_dir = None  # Directory from which images were last loaded

        # SAM/prediction related state
        self.points = []  # Interactive points for SAM in (y, x) format
        self.labels = []  # Labels for interactive points (1=positive, 0=negative)
        self.masks = None  # Masks predicted by SAM
        self.scores = None  # Scores of predicted masks
        self.current_mask_idx = 0  # Index of the currently displayed predicted mask
        self.selected_mask = None  # User-selected mask (from SAM or polygon)
        self.current_label = DEFAULT_LABELS[0]  # Current label for annotation
        self.available_labels = DEFAULT_LABELS.copy()  # All available labels

        # Polygon mode related state
        self.is_polygon_mode = False
        self.polygon_points = []  # Points for custom polygon annotation in (x, y) format
        self.temp_polygon_line = None  # Temporary line for polygon drawing
        self.polygon_lines = []  # Lines forming the closed polygon
        self.closed_polygon = False  # True if the polygon is closed

        # Annotation management state
        self.annotation_complete = False  # Flag indicating if current image annotation is complete
        self.is_modified = False  # True if current image's annotation has been modified
        self.annotation_masks = {}  # Dictionary to store confirmed masks: {label: [mask1, mask2, ...]}
        self.history = []  # Stores states for undo functionality
        self.previous_annotations = {}  # Cache annotations for previously visited images

        # Mask color generation
        self.colors = self.generate_colors(len(DEFAULT_LABELS))

        # Zoom and pan state
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 10.0
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.pan_step = 100

        # Edit mode related state
        self.editable_regions = []  # Stores information about editable regions: {'mask', 'label', 'bbox'}
        self.hovered_region_index = None  # Index of the currently hovered region
        self.selected_region_index = None  # Index of the currently selected region

        # Initialize the user interface
        self.init_ui()

        # Load initial images if a directory is provided
        if image_dir and os.path.exists(image_dir):
            self._initial_image_load(image_dir)
        else:
            self.status_var.set("Please load images or provide a valid initial image directory.")

        # Handle window closing event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _initial_image_load(self, folder_path):
        """Loads images on startup if a directory is provided."""
        self.current_loaded_image_dir = os.path.abspath(folder_path)  # Store absolute path
        start_idx = self._get_start_index_for_dir(self.current_loaded_image_dir)
        self._execute_load_procedure(self.current_loaded_image_dir, start_idx)

    def handle_load_button_press_ui(self):
        """Handles the 'Load Images' button click from the UI."""
        folder = filedialog.askdirectory(title="Select Image Folder")
        if folder:
            abs_folder = os.path.abspath(folder)
            self.current_loaded_image_dir = abs_folder  # Update context
            start_idx = self._get_start_index_for_dir(abs_folder)  # Check session for this new/selected folder
            self._execute_load_procedure(abs_folder, start_idx)
        elif not self.image_list_loaded:  # Only update status if nothing is loaded
            self.status_var.set("Please load images.")

    def _execute_load_procedure(self, folder_path, requested_start_index):
        """
        Core logic to load images from a given folder and jump to a specific index.

        Args:
            folder_path (str): The directory containing images.
            requested_start_index (int): The image index to start from.
        """
        supported_extensions = ['*.jpg', '*.jpeg', '*.png', '*.tif', '*.tiff']
        self.image_paths = []
        for ext in supported_extensions:
            self.image_paths.extend(glob.glob(os.path.join(folder_path, ext)))
            self.image_paths.extend(glob.glob(os.path.join(folder_path, ext.upper())))
        self.image_paths.sort()  # Ensure consistent order

        if not self.image_paths:
            messagebox.showwarning("Warning", f"No supported image files found in directory '{folder_path}'.")
            self.image_list_loaded = False
            self.current_image_index = -1
            self.image_name = ""
            self.image_canvas.delete("all")
            self.status_var.set(f"No images found in '{folder_path}'. Please load another image directory.")
            self.title("SAM2 Interactive Image Annotator - No Images")
            self.image_selector['values'] = []
            self.image_selection_var.set("")
            return False

        # Populate the image selector combobox
        image_basenames = [os.path.basename(p) for p in self.image_paths]
        self.image_selector['values'] = image_basenames

        self.image_list_loaded = True
        self.current_loaded_image_dir = folder_path  # Confirm successful load

        # Set the current image index
        if 0 <= requested_start_index < len(self.image_paths):
            self.current_image_index = requested_start_index
        else:
            self.current_image_index = -1  # No valid start index, will go to next image

        # Load the image (either the requested one or the first available)
        if self.current_image_index == -1:
            self.next_image()
        else:
            self.load_current_image()
            self._save_last_session_info()

        return True

    def _get_start_index_for_dir(self, target_dir):
        """
        Checks if there's a matching directory in the session file and returns its last image index.

        Args:
            target_dir (str): The directory path to check in the session data.

        Returns:
            int: The last saved image index for the target directory, or -1 if not found.
        """
        target_dir_abs = os.path.abspath(target_dir)
        if os.path.exists(self.last_session_file):
            try:
                with open(self.last_session_file, 'r') as f:
                    data = json.load(f)
                saved_dir_abs = os.path.abspath(data.get("last_image_dir", ""))
                if saved_dir_abs == target_dir_abs:
                    last_idx = data.get('last_image_index', -1)
                    print(f"Loading last session info: directory '{target_dir_abs}', index {last_idx}")
                    return last_idx
            except Exception as e:
                print(f"Failed to load last session file '{self.last_session_file}': {e}")
        print(f"No last session info found for directory '{target_dir_abs}'.")
        return -1

    def _save_last_session_info(self):
        """Saves the current image index and directory for future sessions."""
        if self.image_list_loaded and self.current_image_index >= 0 and self.current_loaded_image_dir:
            data = {
                "last_image_dir": os.path.abspath(self.current_loaded_image_dir),
                "last_image_index": self.current_image_index
            }
            try:
                with open(self.last_session_file, 'w') as f:
                    json.dump(data, f, indent=4)
            except Exception as e:
                print(f"Failed to save session file '{self.last_session_file}': {e}")

    def on_closing(self):
        """Handles the application closing event, prompting to save if there are pending changes."""
        if self.is_modified and self.image_list_loaded:
            if messagebox.askyesno("Exit", "There are unsaved changes. Are you sure you want to exit?"):
                self._save_last_session_info()
                self.destroy()
            else:
                return  # Prevent closing if the user cancels
        else:
            self._save_last_session_info()
            self.destroy()

    def generate_colors(self, n):
        """Generates a list of distinct RGB colors."""
        colors = []
        for i in range(n):
            hue = i / n
            saturation = 0.9
            value = 0.9
            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            colors.append(tuple(int(255 * x) for x in rgb))
        return colors

    def init_ui(self):
        """Initializes the main graphical user interface elements."""
        self.title("SAM2 Interactive Image Annotator")
        self.geometry("1200x800")

        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Image display area
        image_frame = ttk.Frame(main_frame)
        image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.image_canvas = tk.Canvas(image_frame, bg="gray")
        self.image_canvas.pack(fill=tk.BOTH, expand=True)

        # Control panel
        control_frame = ttk.Frame(main_frame, width=300)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        # Load image button
        self.load_button = ttk.Button(control_frame, text="Load Images", command=self.handle_load_button_press_ui)
        self.load_button.pack(fill=tk.X, pady=2)

        # Image selection combobox
        image_selection_frame = ttk.LabelFrame(control_frame, text="Quick Jump to Image")
        image_selection_frame.pack(fill=tk.X, pady=5)
        self.image_selection_var = tk.StringVar()
        self.image_selector = ttk.Combobox(image_selection_frame, textvariable=self.image_selection_var,
                                           state="readonly")
        self.image_selector.pack(fill=tk.X, expand=True, padx=5, pady=2)
        self.image_selector.bind("<<ComboboxSelected>>", self.on_image_select)

        # Zoom controls
        zoom_frame = ttk.Frame(control_frame)
        zoom_frame.pack(fill=tk.X, pady=2)
        ttk.Button(zoom_frame, text="Zoom In", command=lambda: self.zoom(1.2)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(zoom_frame, text="Zoom Out", command=lambda: self.zoom(0.8333)).pack(side=tk.LEFT, fill=tk.X,
                                                                                        expand=True)

        # Pan controls
        pan_frame = ttk.Frame(control_frame)
        pan_frame.pack(fill=tk.X, pady=2)
        pan_frame.columnconfigure((0, 1), weight=1)
        ttk.Button(pan_frame, text="Pan Left", command=self.pan_left).grid(row=0, column=0, sticky="ew", padx=2)
        ttk.Button(pan_frame, text="Pan Right", command=self.pan_right).grid(row=0, column=1, sticky="ew", padx=2)
        ttk.Button(pan_frame, text="Pan Up", command=self.pan_up).grid(row=1, column=0, sticky="ew", padx=2)
        ttk.Button(pan_frame, text="Pan Down", command=self.pan_down).grid(row=1, column=1, sticky="ew", padx=2)

        # Mode selection (SAM, Polygon, Edit)
        self.mode_frame = ttk.LabelFrame(control_frame, text="Select Operation Mode")
        self.mode_frame.pack(fill=tk.X, pady=2)
        self.mode_var = tk.StringVar(value="SAM Annotation")
        self.sam_mode_radio = ttk.Radiobutton(self.mode_frame, text="SAM Annotation", variable=self.mode_var, value="SAM Annotation",
                                              command=self.change_to_sam_mode)
        self.sam_mode_radio.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.polygon_mode_radio = ttk.Radiobutton(self.mode_frame, text="Polygon", variable=self.mode_var,
                                                  value="Polygon", command=self.change_to_polygon_mode)
        self.polygon_mode_radio.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.edit_mode_radio = ttk.Radiobutton(self.mode_frame, text="Edit Labels", variable=self.mode_var,
                                               value="Edit Labels", command=self.change_to_edit_mode)
        self.edit_mode_radio.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # SAM Annotation Tools Frame
        self.sam_frame = ttk.LabelFrame(control_frame, text="SAM Annotation Tools")
        self.sam_frame.pack(fill=tk.X, pady=2)
        self.predict_button = ttk.Button(self.sam_frame, text="Predict Mask", command=self.predict_masks)
        self.predict_button.pack(fill=tk.X, pady=2)
        self.select_button = ttk.Button(self.sam_frame, text="Select Mask", command=self.select_mask)
        self.select_button.pack(fill=tk.X, pady=2)
        self.next_mask_button = ttk.Button(self.sam_frame, text="Next Mask", command=self.next_mask)
        self.next_mask_button.pack(fill=tk.X, pady=2)

        # Polygon Annotation Tools Frame
        self.polygon_frame = ttk.LabelFrame(control_frame, text="Polygon Annotation Tools")
        self.close_polygon_button = ttk.Button(self.polygon_frame, text="Close Polygon", command=self.close_polygon)
        self.close_polygon_button.pack(fill=tk.X, pady=2)
        self.clear_polygon_button = ttk.Button(self.polygon_frame, text="Clear Polygon", command=self.clear_polygon)
        self.clear_polygon_button.pack(fill=tk.X, pady=2)

        # Edit Label Tools Frame
        self.edit_frame = ttk.LabelFrame(control_frame, text="Editing Tools")
        self.update_label_button = ttk.Button(self.edit_frame, text="Update Label", command=self.update_selected_label,
                                              state=tk.DISABLED)  # Disabled until a region is selected
        self.update_label_button.pack(fill=tk.X, pady=2)

        # Undo and Reset buttons
        self.undo_button = ttk.Button(control_frame, text="Undo", command=self.undo)
        self.undo_button.pack(fill=tk.X, pady=2)
        self.reset_button = ttk.Button(control_frame, text="Reset", command=self.reset_annotation)
        self.reset_button.pack(fill=tk.X, pady=2)

        # Current annotation label selection
        label_frame = ttk.Frame(control_frame)
        label_frame.pack(fill=tk.X, pady=2)
        ttk.Label(label_frame, text="Label:").pack(side=tk.LEFT)
        self.label_var = tk.StringVar(value=self.current_label)
        self.label_combo = ttk.Combobox(label_frame, textvariable=self.label_var, values=self.available_labels)
        self.label_combo.bind("<<ComboboxSelected>>", self.on_label_change)
        self.label_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Confirm and Save buttons
        self.confirm_button = ttk.Button(control_frame, text="Confirm & Lock This Region", command=self.confirm_label)
        self.confirm_button.pack(fill=tk.X, pady=2)
        self.complete_button = ttk.Button(control_frame, text="Finish & Save", command=self.complete_annotation)
        self.complete_button.pack(fill=tk.X, pady=2)

        # Navigation buttons (Previous/Next Image)
        nav_frame = ttk.Frame(control_frame)
        nav_frame.pack(fill=tk.X, pady=2)
        self.prev_button = ttk.Button(nav_frame, text="Previous", command=self.prev_image)
        self.prev_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.next_button = ttk.Button(nav_frame, text="Next", command=self.next_image)
        self.next_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Help text for different modes
        self.sam_help_text = "SAM Mode: Left click for positive points, Right click for negative points, Middle click to erase."
        self.polygon_help_text = "Polygon Mode: Left click to add vertex, Right click to delete last vertex."
        self.edit_help_text = "Edit Mode: Click an annotated region to select it, then choose a new label above and click 'Update Label' button to modify."
        self.help_var = tk.StringVar(value=self.sam_help_text)
        self.help_label = ttk.Label(control_frame, textvariable=self.help_var, wraplength=280, justify=tk.LEFT)
        self.help_label.pack(fill=tk.X, pady=10, padx=5)

        # Status bar
        self.status_var = tk.StringVar(value="Please load images.")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Set default mode to SAM
        self.change_to_sam_mode()

    def on_image_select(self, event=None):
        """
        Handles image selection from the combobox.
        Prompts to save if the current image has unsaved changes.
        """
        selected_image_name = self.image_selection_var.get()
        if not selected_image_name or not self.image_list_loaded or selected_image_name == self.image_name:
            return  # Do nothing if no selection, no images, or already on the selected image

        try:
            # Find the index of the selected image
            target_index = [os.path.basename(p) for p in self.image_paths].index(selected_image_name)
        except ValueError:
            messagebox.showerror("Error", f"'{selected_image_name}' not found in the image list.")
            self.image_selection_var.set(self.image_name)  # Revert combobox to current image
            return

        if self.is_modified:
            # If there are unsaved changes, prompt to save
            if not messagebox.askyesno("Prompt", "The current image has unsaved modifications. Do you want to proceed?"):
                self.image_selection_var.set(self.image_name)  # Revert combobox to current image
                return

        # Cache current annotations before loading a new image
        if self.annotation_masks and self.image_name:
            self.previous_annotations[self.image_name] = self.annotation_masks.copy()

        # Reset zoom/pan and load the new image
        self.current_image_index = target_index
        self.zoom_factor = 1.0
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.load_current_image()
        self._save_last_session_info()  # Save session info after loading

    def bind_sam_events(self):
        """Binds canvas events related to SAM annotation mode."""
        self.image_canvas.unbind("<Button-1>")  # Left click
        self.image_canvas.unbind("<Button-3>")  # Right click
        self.image_canvas.unbind("<Button-2>")  # Middle click
        self.image_canvas.unbind("<Motion>")  # Mouse motion
        self.image_canvas.bind("<Button-1>", self.on_left_click)
        self.image_canvas.bind("<Button-3>", self.on_right_click)
        self.image_canvas.bind("<Button-2>", self.on_middle_click)
        self.image_canvas.bind("<Configure>", self.on_canvas_resize)

    def bind_polygon_events(self):
        """Binds canvas events related to polygon annotation mode."""
        self.image_canvas.unbind("<Button-1>")
        self.image_canvas.unbind("<Button-3>")
        self.image_canvas.unbind("<Button-2>")
        self.image_canvas.unbind("<Motion>")
        self.image_canvas.bind("<Button-1>", self.on_polygon_left_click)
        self.image_canvas.bind("<Button-3>", self.on_polygon_right_click)
        self.image_canvas.bind("<Motion>", self.on_polygon_mouse_move)
        self.image_canvas.bind("<Configure>", self.on_canvas_resize)

    def bind_edit_events(self):
        """Binds canvas events related to edit label mode."""
        self.image_canvas.unbind("<Button-1>")
        self.image_canvas.unbind("<Button-3>")
        self.image_canvas.unbind("<Button-2>")
        self.image_canvas.unbind("<Motion>")
        self.image_canvas.bind("<Motion>", self.on_edit_mode_motion)
        self.image_canvas.bind("<Button-1>", self.on_edit_mode_click)
        self.image_canvas.bind("<Configure>", self.on_canvas_resize)

    def zoom(self, scale):
        """Zooms in or out on the displayed image."""
        new_zoom = self.zoom_factor * scale
        if new_zoom < self.min_zoom or new_zoom > self.max_zoom:
            return
        self.zoom_factor = new_zoom
        self.status_var.set(
            f"Current Image: {self.image_name} | Zoom: {self.zoom_factor:.2f}x | Pan: ({self.pan_offset_x}, {self.pan_offset_y})")
        if self.image_np is not None:
            self.display_image(self.image_np)

    def pan_left(self):
        """Pans the image to the left."""
        if self.image_np is None: return
        self.pan_offset_x -= self.pan_step
        self.status_var.set(
            f"Current Image: {self.image_name} | Zoom: {self.zoom_factor:.2f}x | Pan: ({self.pan_offset_x}, {self.pan_offset_y})")
        self.display_image(self.image_np)

    def pan_right(self):
        """Pans the image to the right."""
        if self.image_np is None: return
        self.pan_offset_x += self.pan_step
        self.status_var.set(
            f"Current Image: {self.image_name} | Zoom: {self.zoom_factor:.2f}x | Pan: ({self.pan_offset_x}, {self.pan_offset_y})")
        self.display_image(self.image_np)

    def pan_up(self):
        """Pans the image up."""
        if self.image_np is None: return
        self.pan_offset_y -= self.pan_step
        self.status_var.set(
            f"Current Image: {self.image_name} | Zoom: {self.zoom_factor:.2f}x | Pan: ({self.pan_offset_x}, {self.pan_offset_y})")
        self.display_image(self.image_np)

    def pan_down(self):
        """Pans the image down."""
        if self.image_np is None: return
        self.pan_offset_y += self.pan_step
        self.status_var.set(
            f"Current Image: {self.image_name} | Zoom: {self.zoom_factor:.2f}x | Pan: ({self.pan_offset_x}, {self.pan_offset_y})")
        self.display_image(self.image_np)

    def change_to_sam_mode(self):
        """Switches the application to SAM annotation mode."""
        self.sam_frame.pack(fill=tk.X, pady=2, after=self.mode_frame)
        self.polygon_frame.pack_forget()  # Hide polygon controls
        self.edit_frame.pack_forget()  # Hide edit controls
        self.confirm_button.config(state=tk.NORMAL)  # Enable confirm button for new annotations

        self.help_var.set(self.sam_help_text)
        self.bind_sam_events()
        self.clear_polygon()  # Clear any pending polygon drawing
        self._clear_selection_state()  # Clear selection if previously in edit mode
        if self.image_np is not None:
            self.display_image(self.image_np)

    def change_to_polygon_mode(self):
        """Switches the application to polygon annotation mode."""
        self.is_polygon_mode = True
        self.sam_frame.pack_forget()
        self.polygon_frame.pack(fill=tk.X, pady=2, after=self.mode_frame)
        self.edit_frame.pack_forget()
        self.confirm_button.config(state=tk.NORMAL)

        self.help_var.set(self.polygon_help_text)
        self.bind_polygon_events()
        self._clear_selection_state()
        if self.image_np is not None:
            self.display_image(self.image_np)

    def change_to_edit_mode(self):
        """Switches the application to edit labels mode."""
        self.sam_frame.pack_forget()
        self.polygon_frame.pack_forget()
        self.edit_frame.pack(fill=tk.X, pady=2, after=self.mode_frame)
        self.confirm_button.config(state=tk.DISABLED)  # Disable confirm button as new annotations aren't created here

        self.help_var.set(self.edit_help_text)
        self.bind_edit_events()
        self.clear_polygon()  # Clear any pending polygon drawing
        self._prepare_for_editing()  # Prepare data for editing existing annotations
        if self.image_np is not None:
            self.display_image(self.image_np)

    def on_polygon_left_click(self, event):
        """Handles left click event in polygon mode to add points."""
        if self.image_np is None or self.closed_polygon:
            return

        x, y = self._convert_canvas_to_image_coords(event.x, event.y)
        canvas_x = event.x
        canvas_y = event.y

        # Check if click is near the first point to close the polygon
        if len(self.polygon_points) > 2:
            first_x, first_y = self.polygon_points[0]
            canvas_first_x, canvas_first_y = self._convert_image_to_canvas_coords(first_x, first_y)
            if ((canvas_x - canvas_first_x) ** 2 + (canvas_y - canvas_first_y) ** 2) ** 0.5 < 10:
                self.close_polygon()
                return

        self.polygon_points.append((x, y))
        self.image_canvas.create_oval(
            canvas_x - 5, canvas_y - 5, canvas_x + 5, canvas_y + 5,
            fill="red", outline="white", tags="polygon_point"
        )

        if len(self.polygon_points) > 1:
            prev_x, prev_y = self._convert_image_to_canvas_coords(
                self.polygon_points[-2][0], self.polygon_points[-2][1]
            )
            line_id = self.image_canvas.create_line(
                prev_x, prev_y, canvas_x, canvas_y,
                fill="yellow", width=2, tags="polygon_line"
            )
            self.polygon_lines.append(line_id)

        self.status_var.set(f"Polygon vertex #{len(self.polygon_points)} added at ({x}, {y}).")

    def on_polygon_right_click(self, event):
        """Handles right click event in polygon mode to remove the last point."""
        if not self.polygon_points or self.closed_polygon:
            return

        self.polygon_points.pop()  # Remove the last point
        # Remove corresponding canvas elements
        points = self.image_canvas.find_withtag("polygon_point")
        if points:
            self.image_canvas.delete(points[-1])

        if self.polygon_lines:
            self.image_canvas.delete(self.polygon_lines.pop())

        # Update temporary line if there are still points
        if self.polygon_points and self.temp_polygon_line:
            prev_x, prev_y = self._convert_image_to_canvas_coords(
                self.polygon_points[-1][0], self.polygon_points[-1][1]
            )
            self.image_canvas.coords(
                self.temp_polygon_line,
                prev_x, prev_y, event.x, event.y
            )

        self.status_var.set(f"Deleted last polygon vertex, {len(self.polygon_points)} vertices remaining.")

    def on_polygon_mouse_move(self, event):
        """Handles mouse motion in polygon mode to draw a temporary line to the current cursor position."""
        if not self.polygon_points or self.closed_polygon:
            return

        last_x, last_y = self._convert_image_to_canvas_coords(
            self.polygon_points[-1][0], self.polygon_points[-1][1]
        )

        if self.temp_polygon_line:
            self.image_canvas.coords(
                self.temp_polygon_line,
                last_x, last_y, event.x, event.y
            )
        else:
            self.temp_polygon_line = self.image_canvas.create_line(
                last_x, last_y, event.x, event.y,
                fill="gray", dash=(4, 4), tags="temp_line"
            )

    def clear_polygon(self):
        """Clears all points and lines of the current polygon drawing."""
        self.polygon_points = []
        self.closed_polygon = False
        self.image_canvas.delete("polygon_point")
        self.image_canvas.delete("polygon_line")
        self.image_canvas.delete("temp_line")
        self.temp_polygon_line = None
        self.polygon_lines = []
        self.selected_mask = None  # Clear any selected mask that might have originated from polygon mode
        self.status_var.set("Polygon cleared.")
        if self.image_np is not None:
            self.display_image(self.image_np)

    def close_polygon(self):
        """
        Closes the polygon, converts it into a mask, and enforces no overlap with existing annotations.
        """
        if len(self.polygon_points) < 3:
            messagebox.showwarning("Warning", "A polygon needs at least 3 vertices.")
            return

        self.save_to_history()  # Save current state before closing polygon
        self.closed_polygon = True

        # Draw the closing line on the canvas
        first_x, first_y = self._convert_image_to_canvas_coords(
            self.polygon_points[0][0], self.polygon_points[0][1]
        )
        last_x, last_y = self._convert_image_to_canvas_coords(
            self.polygon_points[-1][0], self.polygon_points[-1][1]
        )
        line_id = self.image_canvas.create_line(
            last_x, last_y, first_x, first_y,
            fill="yellow", width=2, tags="polygon_line"
        )
        self.polygon_lines.append(line_id)

        # Create a mask from polygon points
        mask = np.zeros(self.image_np.shape[:2], dtype=np.uint8)
        pts = np.array(self.polygon_points, dtype=np.int32)
        cv2.fillPoly(mask, [pts], 1)
        mask_bool = mask.astype(bool)

        # --- Important: Enforce no overlap with existing annotations ---
        locked_mask = self._get_locked_mask()  # Get combined mask of all confirmed annotations
        if locked_mask is not None:
            original_area = np.sum(mask_bool)  # Area of polygon region before exclusion
            mask_bool = np.logical_and(mask_bool, ~locked_mask)  # Exclude already locked areas
            new_area = np.sum(mask_bool)  # Area of polygon region after exclusion

            # If the polygon became empty after exclusion, warn the user
            if original_area > 0 and new_area == 0:
                messagebox.showwarning("Warning", "The polygon you drew is entirely within an already annotated area. No valid new region. Please redraw.")
                self.clear_polygon()  # Clear invalid polygon
                self.display_image(self.image_np)
                return

        self.selected_mask = mask_bool  # The cleaned mask is now selected
        self.is_modified = True

        # Clean up polygon drawing elements on canvas
        self.image_canvas.delete("polygon_point")
        self.image_canvas.delete("polygon_line")
        self.image_canvas.delete("temp_line")
        self.temp_polygon_line = None
        self.polygon_lines = []

        self.display_image(self.image_np)
        self.status_var.set("Polygon closed. Please assign a label.")

    def on_canvas_resize(self, event):
        """Redraws the image when the canvas is resized."""
        if self.image_np is not None:
            self.display_image(self.image_np)

    def load_model(self, model_path, config_path=None):
        """Loads the SAM2 model."""
        try:
            print(f"Loading SAM2 model: {model_path}")
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found: {model_path}")
            if config_path is None:
                # Infer config path if not provided based on model name
                config_path = "configs/sam2/sam2_hiera_l.yaml" if "large" in model_path.lower() else "configs/sam2/sam2_hiera_b.yaml"
                print(f"No config path provided, using: {config_path}")
            self.model = build_sam2(config_path, model_path, device=self.device)
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Failed to load model: {e}")
            traceback.print_exc()
            messagebox.showerror("Model Load Failed", f"Could not load SAM2 model: {e}\nPlease check model and config file paths.")
            self.destroy()  # Close app if model fails to load

    def next_image(self):
        """Loads the next image in the list."""
        if not self.image_list_loaded or not self.image_paths:
            messagebox.showwarning("Warning", "No image list loaded.")
            return
        if self.is_modified:
            if not messagebox.askyesno("Prompt", "The current image has unsaved modifications. Do you want to proceed?"):
                return
        if self.current_image_index < len(self.image_paths) - 1:
            # Cache current annotations before moving to the next image
            if self.annotation_masks and self.image_name:
                self.previous_annotations[self.image_name] = self.annotation_masks.copy()
            self.current_image_index += 1
            self.zoom_factor = 1.0
            self.pan_offset_x = 0
            self.pan_offset_y = 0
            self.load_current_image()
            self._save_last_session_info()
        else:
            messagebox.showinfo("Info", "This is the last image.")

    def prev_image(self):
        """Loads the previous image in the list."""
        if not self.image_list_loaded or not self.image_paths:
            messagebox.showwarning("Warning", "No image list loaded.")
            return
        if self.is_modified:
            if not messagebox.askyesno("Prompt", "The current image has unsaved modifications. Do you want to proceed?"):
                return
        if self.current_image_index > 0:
            # Cache current annotations before moving to the previous image
            if self.annotation_masks and self.image_name:
                self.previous_annotations[self.image_name] = self.annotation_masks.copy()
            self.current_image_index -= 1
            self.zoom_factor = 1.0
            self.pan_offset_x = 0
            self.pan_offset_y = 0
            self.load_current_image()
            self._save_last_session_info()
        else:
            messagebox.showinfo("Info", "This is the first image.")

    def load_current_image(self):
        """Loads the image at current_image_index."""
        if not (0 <= self.current_image_index < len(self.image_paths)):
            print(f"Error: current_image_index ({self.current_image_index}) out of bounds (0-{len(self.image_paths) - 1})")
            self.status_var.set("Error: Image index out of bounds.")
            self.title("SAM2 Interactive Image Annotator - Index Error")
            if self.image_np is not None:
                self.image_np = None
                self.image_canvas.delete("all")
            return

        image_path = self.image_paths[self.current_image_index]
        try:
            image = Image.open(image_path)
            self.image_np = np.array(image.convert("RGB"))  # Convert to RGB for consistency
            self.image_name = os.path.basename(image_path)

            self.title(f"SAM2 Interactive Image Annotator - {self.image_name}")

            if self.image_list_loaded:
                self.image_selection_var.set(self.image_name)

            # Re-initialize SAM predictor each time a new image is loaded
            # This ensures SAM always starts processing the new image from a "clean" state
            self.predictor = SAM2ImagePredictor(self.model)  # Recreate SAM2ImagePredictor instance

            self.reset_annotation()  # Reset annotation state for the new image

            # Note: We do NOT call self.predictor.set_image() here anymore.
            # We want SAM to always use the masked image within predict_masks.

            self.annotation_masks = {}  # Initialize annotation masks for the current image
            json_file = os.path.join(self.jsons_path, self.image_name.rsplit('.', 1)[0] + '.json')

            # Load previous annotations if cached or from JSON file
            if self.image_name in self.previous_annotations:
                self.annotation_masks = self.previous_annotations[self.image_name].copy()
            elif os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for shape in data.get('shapes', []):
                    label = shape['label']
                    points = np.array(shape['points'], dtype=np.int32)
                    if points.ndim == 2 and points.shape[0] >= 3 and points.shape[1] == 2:
                        mask = np.zeros(self.image_np.shape[:2], dtype=np.uint8)
                        cv2.fillPoly(mask, [points], 1)
                        mask_bool = mask.astype(bool)
                        if label not in self.annotation_masks:
                            self.annotation_masks[label] = []
                        self.annotation_masks[label].append(mask_bool)
                    else:
                        print(f"Warning: Invalid set of points found for label '{label}' in JSON file '{json_file}'.")

            self.status_var.set(
                f"Current Image: {self.image_name} | Progress: {self.current_image_index + 1}/{len(self.image_paths)} | Zoom: {self.zoom_factor:.2f}x | Pan: ({self.pan_offset_x}, {self.pan_offset_y})")

            # Refresh UI based on current active mode
            current_mode = self.mode_var.get()
            if current_mode == "SAM Annotation":
                self.change_to_sam_mode()
            elif current_mode == "Polygon":
                self.change_to_polygon_mode()
            elif current_mode == "Edit Labels":
                self.change_to_edit_mode()

            self.display_image(self.image_np)  # Display the loaded image with existing annotations

        except FileNotFoundError:
            print(f"Error: Image file not found '{image_path}'")
            messagebox.showerror("Error", f"Image file not found: {os.path.basename(image_path)}")
            self.status_var.set(f"Error: Image file '{os.path.basename(image_path)}' not found.")
            self.title(f"SAM2 Interactive Image Annotator - File Not Found")
            if len(self.image_paths) > 1:
                self.image_paths.pop(self.current_image_index)  # Remove the corrupted path
                image_basenames = [os.path.basename(p) for p in self.image_paths]
                self.image_selector['values'] = image_basenames
                # Adjust index if necessary
                if self.current_image_index >= len(self.image_paths) and len(self.image_paths) > 0:
                    self.current_image_index = len(self.image_paths) - 1
                elif len(self.image_paths) == 0:
                    self.current_image_index = -1
                    self.image_list_loaded = False
                    self.title("SAM2 Interactive Image Annotator - No Images")
                    self.image_canvas.delete("all")
                    self.status_var.set("All images failed to load or list is empty.")
                    return
                self.load_current_image()  # Try to load the next valid image
            else:
                # No more images to load
                self.image_np = None
                self.image_name = ""
                self.image_list_loaded = False
                self.current_image_index = -1
                self.image_canvas.delete("all")
                self.status_var.set(f"Image '{os.path.basename(image_path)}' not found. List is empty.")
                self.image_selector['values'] = []
                self.image_selection_var.set("")
        except Exception as e:
            print(f"Failed to load image '{image_path}': {e}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to load image '{os.path.basename(image_path)}': {str(e)}")
            self.status_var.set(f"Failed to load image '{os.path.basename(image_path)}'.")
            self.title(f"SAM2 Interactive Image Annotator - Load Failed")

    def display_image(self, image):
        """
        Displays the image on the canvas, applying confirmed masks,
        predicted masks, and interaction points.
        """
        self.display_img = image.copy()

        # Helper function to draw mask contours with overlay
        def draw_mask_contours(mask_to_draw, color=(0, 165, 255), alpha=0.5):
            if mask_to_draw is None or not np.any(mask_to_draw):
                return
            self.apply_mask(self.display_img, mask_to_draw, color, alpha)  # Apply translucent color overlay
            # Draw white contours for better visibility
            contours, _ = cv2.findContours(
                mask_to_draw.astype(np.uint8),
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )
            cv2.drawContours(self.display_img, contours, -1, (255, 255, 255), 1)

        # Draw all confirmed annotation masks
        for label, masks_list in self.annotation_masks.items():
            if label in self.available_labels:
                label_idx = self.available_labels.index(label)
            else:  # Dynamically add new labels to available list
                self.available_labels.append(label)
                self.label_combo['values'] = self.available_labels
                label_idx = len(self.available_labels) - 1
                if label_idx >= len(self.colors):  # Generate more colors if needed
                    self.colors = self.generate_colors(len(self.available_labels))

            color = self.colors[label_idx % len(self.colors)]  # Cycle colors if many labels
            combined_mask = np.zeros_like(masks_list[0], dtype=bool) if masks_list else None

            # Apply each mask for this label and combine for centroid calculation
            for mask in masks_list:
                alpha = 0.4  # Opacity for confirmed masks
                self.apply_mask(self.display_img, mask, color, alpha=alpha)
                if combined_mask is not None:
                    combined_mask = np.logical_or(combined_mask, mask)

            # Draw label text on the centroid of the combined mask
            if combined_mask is not None and np.any(combined_mask):
                y_indices, x_indices = np.where(combined_mask)
                if len(y_indices) > 0 and len(x_indices) > 0:
                    center_y = int(np.mean(y_indices))
                    center_x = int(np.mean(x_indices))
                    # Ensure text is within image boundaries
                    text_x = max(0, min(center_x, self.display_img.shape[1] - 10))
                    text_y = max(15, min(center_y, self.display_img.shape[0] - 5))
                    cv2.putText(self.display_img, label, (text_x, text_y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Draw the current predicted SAM mask (if any)
        if self.masks is not None and len(self.masks) > 0 and self.current_mask_idx < len(self.masks):
            mask = self.masks[self.current_mask_idx]
            draw_mask_contours(mask, color=(0, 165, 255))  # Orange-blue for predicted masks

        # Draw the currently selected mask (from SAM or polygon)
        if self.selected_mask is not None:
            draw_mask_contours(self.selected_mask, color=(0, 255, 255))  # Cyan for selected mask

        # Draw interaction points in SAM mode
        if self.mode_var.get() == "SAM Annotation":
            self.draw_points(self.display_img)

        # Draw bounding boxes for editable regions in edit mode
        if self.mode_var.get() == "Edit Labels":
            for i, region in enumerate(self.editable_regions):
                x, y, w, h = region['bbox']
                color = (255, 255, 255)  # Default white
                if i == self.selected_region_index:
                    color = (0, 255, 0)  # Green when selected
                elif i == self.hovered_region_index:
                    color = (255, 255, 0)  # Yellow when hovered
                cv2.rectangle(self.display_img, (x, y), (x + w, y + h), color, 2)  # Draw rectangle

        # Prepare image for Tkinter canvas display (zoom and pan)
        canvas_width = self.image_canvas.winfo_width()
        canvas_height = self.image_canvas.winfo_height()
        img_height, img_width = self.display_img.shape[:2]

        # Initial size fallback before canvas is properly configured
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = max(1, self.image_canvas.winfo_reqwidth())
            canvas_height = max(1, self.image_canvas.winfo_reqheight())
            if canvas_width <= 1: canvas_width = 800
            if canvas_height <= 1: canvas_height = 600

        # Calculate zoomed dimensions
        zoomed_width = int(img_width * self.zoom_factor)
        zoomed_height = int(img_height * self.zoom_factor)

        # Ensure dimensions are at least 1 pixel
        if zoomed_width < 1 or zoomed_height < 1:
            zoomed_width = max(1, zoomed_width)
            zoomed_height = max(1, zoomed_height)

        # Resize image for display
        image_at_zoom_level = cv2.resize(self.display_img, (zoomed_width, zoomed_height), interpolation=cv2.INTER_AREA)

        # Convert to PhotoImage for Tkinter
        image_pil = Image.fromarray(image_at_zoom_level)
        self.photo = ImageTk.PhotoImage(image_pil)
        self.image_canvas.delete("all")  # Clear previous drawings on canvas

        # Calculate position to draw image, with pan offset
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        draw_x = center_x - zoomed_width // 2 + self.pan_offset_x
        draw_y = center_y - zoomed_height // 2 + self.pan_offset_y

        self.image_canvas.create_image(
            draw_x, draw_y,
            image=self.photo,
            anchor="nw"  # Anchor to top-left
        )

        # Store current display scale and offset for coordinate conversion
        self.current_display_scale = self.zoom_factor
        self.canvas_offset_x = draw_x
        self.canvas_offset_y = draw_y

        # If in polygon mode, redraw polygon points/lines
        if self.mode_var.get() == "Polygon" and self.polygon_points:
            self.redraw_polygon()

    def redraw_polygon(self):
        """Redraws polygon points and lines on the canvas after zoom/pan."""
        self.image_canvas.delete("polygon_point")
        self.image_canvas.delete("polygon_line")
        self.image_canvas.delete("temp_line")  # Ensure temp line is also cleared/redrawn
        self.polygon_lines = []
        self.temp_polygon_line = None

        for i, (x, y) in enumerate(self.polygon_points):
            canvas_x, canvas_y = self._convert_image_to_canvas_coords(x, y)
            self.image_canvas.create_oval(
                canvas_x - 5, canvas_y - 5, canvas_x + 5, canvas_y + 5,
                fill="red", outline="white", tags="polygon_point"
            )
            if i > 0:
                prev_x_img, prev_y_img = self.polygon_points[i - 1]
                prev_x_canvas, prev_y_canvas = self._convert_image_to_canvas_coords(prev_x_img, prev_y_img)
                line_id = self.image_canvas.create_line(
                    prev_x_canvas, prev_y_canvas, canvas_x, canvas_y,
                    fill="yellow", width=2, tags="polygon_line"
                )
                self.polygon_lines.append(line_id)

        # Draw closing line if polygon is closed
        if self.closed_polygon and len(self.polygon_points) > 2:
            first_x_img, first_y_img = self.polygon_points[0]
            last_x_img, last_y_img = self.polygon_points[-1]
            first_x_canvas, first_y_canvas = self._convert_image_to_canvas_coords(first_x_img, first_y_img)
            last_x_canvas, last_y_canvas = self._convert_image_to_canvas_coords(last_x_img, last_y_img)

            line_id = self.image_canvas.create_line(
                last_x_canvas, last_y_canvas, first_x_canvas, first_y_canvas,
                fill="yellow", width=2, tags="polygon_line"
            )
            self.polygon_lines.append(line_id)

    def apply_mask(self, image, mask, color, alpha=0.5):
        """Applies a translucent colored mask overlay to an image."""
        mask = mask.astype(bool)  # Ensure mask is boolean
        colored_mask = np.zeros_like(image)
        colored_mask[mask] = color  # Apply color to masked regions
        cv2.addWeighted(colored_mask, alpha, image, 1.0, 0, image)  # Blend with original image
        return image

    def draw_points(self, image_to_draw_on):
        """Draws SAM interaction points on the image."""
        if self.image_np is None: return

        for i, (point_orig_coords, label) in enumerate(zip(self.points, self.labels)):
            y_orig, x_orig = point_orig_coords
            color = (0, 255, 0) if label == 1 else (0, 0, 255)  # Green for positive, Red for negative
            star_base_size = 10
            star_points = []
            # Generate star points
            for j in range(10):
                angle = np.pi / 5 * j - np.pi / 2
                radius = star_base_size if j % 2 == 0 else star_base_size * 0.4
                point_x = int(x_orig + radius * np.cos(angle))
                point_y = int(y_orig + radius * np.sin(angle))
                star_points.append([point_x, point_y])

            star_points_np = np.array(star_points, dtype=np.int32).reshape((-1, 1, 2))
            cv2.polylines(image_to_draw_on, [star_points_np], True, (255, 255, 255), 2)  # White outline
            cv2.fillPoly(image_to_draw_on, [star_points_np], color)  # Fill color

    def _convert_canvas_to_image_coords(self, canvas_x, canvas_y):
        """Converts canvas coordinates to original image coordinates."""
        if self.image_np is None or self.current_display_scale == 0:
            return canvas_x, canvas_y

        # Adjust for canvas pan and calculate position on the zoomed image
        x_on_zoomed_image = canvas_x - self.canvas_offset_x
        y_on_zoomed_image = canvas_y - self.canvas_offset_y

        # Scale back to original image dimensions
        original_x = x_on_zoomed_image / self.current_display_scale
        original_y = y_on_zoomed_image / self.current_display_scale

        # Clamp coordinates to be within image boundaries
        img_height, img_width = self.image_np.shape[:2]
        original_x = max(0, min(original_x, img_width - 1))
        original_y = max(0, min(original_y, img_height - 1))

        return int(original_x), int(original_y)

    def _convert_image_to_canvas_coords(self, image_x, image_y):
        """Converts original image coordinates to canvas coordinates."""
        if self.image_np is None:
            return image_x, image_y

        # Scale to zoomed image dimensions
        x_on_zoomed_image = image_x * self.current_display_scale
        y_on_zoomed_image = image_y * self.current_display_scale

        # Adjust for canvas pan
        canvas_x = x_on_zoomed_image + self.canvas_offset_x
        canvas_y = y_on_zoomed_image + self.canvas_offset_y

        return int(canvas_x), int(canvas_y)

    def on_left_click(self, event):
        """Handles left click (positive point) in SAM mode."""
        if self.image_np is None: return
        x, y = self._convert_canvas_to_image_coords(event.x, event.y)
        self.add_point(x, y, is_positive=True)
        self.display_image(self.image_np)

    def on_right_click(self, event):
        """Handles right click (negative point) in SAM mode."""
        if self.image_np is None: return
        x, y = self._convert_canvas_to_image_coords(event.x, event.y)
        self.add_point(x, y, is_positive=False)
        self.display_image(self.image_np)

    def on_middle_click(self, event):
        """Handles middle click (erase region) in SAM mode."""
        if self.image_np is None: return
        x, y = self._convert_canvas_to_image_coords(event.x, event.y)
        self.remove_mask_region(x, y)  # Attempt to remove region from any visible mask
        self.display_image(self.image_np)

    def on_edit_mode_motion(self, event):
        """Handles mouse motion in edit mode to highlight regions."""
        if self.image_np is None: return
        x, y = self._convert_canvas_to_image_coords(event.x, event.y)

        current_hover = None
        for i, region in enumerate(self.editable_regions):
            rx, ry, rw, rh = region['bbox']  # Bounding box in original image coordinates
            if rx <= x < rx + rw and ry <= y < ry + rh:
                # Check if the pixel under cursor is actually part of the mask
                if region['mask'][y, x]:
                    current_hover = i
                    break

        # Redraw only if hover state changed to avoid unnecessary updates
        if current_hover != self.hovered_region_index:
            self.hovered_region_index = current_hover
            self.display_image(self.image_np)

    def on_edit_mode_click(self, event):
        """Handles click in edit mode to select a region for label update."""
        # Must be hovering over a region to select
        if self.hovered_region_index is not None:
            self.selected_region_index = self.hovered_region_index
            selected_label = self.editable_regions[self.selected_region_index]['label']
            self.label_var.set(selected_label)  # Set the label combobox to the selected region's label
            self.update_label_button.config(state=tk.NORMAL)  # Enable update button
            self.status_var.set(f"Region selected, label '{selected_label}'. Choose new label and click 'Update Label'.")
        else:
            self._clear_selection_state()  # Clicked on empty space, deselect
            self.status_var.set("Deselected.")

        self.display_image(self.image_np)  # Refresh display to show selection highlight

    def remove_mask_region(self, x, y, radius=20):
        """
        Removes a circular region from the current predicted mask, selected mask,
        or any confirmed annotation masks.
        """
        modified = False
        if self.image_np is None: return False

        # Create a circular erase mask
        erase_mask = np.zeros(self.image_np.shape[:2], dtype=np.uint8)
        cv2.circle(erase_mask, (x, y), radius, 1, -1)  # Fill circle with 1
        erase_mask_bool = erase_mask.astype(bool)

        # 1. Try to remove from the current predicted mask (if visible)
        if self.masks is not None and self.current_mask_idx < len(self.masks) and \
                self.masks[self.current_mask_idx] is not None:
            current_pred_mask = self.masks[self.current_mask_idx]
            if np.any(current_pred_mask[erase_mask_bool]):  # Check for overlap before modifying
                self.save_to_history()
                self.masks[self.current_mask_idx] = np.logical_and(current_pred_mask, ~erase_mask_bool)
                self.is_modified = True
                modified = True
                self.status_var.set(f"Region removed from predicted mask.")

        # 2. If not modified, try to remove from the current selected mask
        if not modified and self.selected_mask is not None:
            if np.any(self.selected_mask[erase_mask_bool]):
                self.save_to_history()
                self.selected_mask = np.logical_and(self.selected_mask, ~erase_mask_bool)
                self.is_modified = True
                modified = True
                self.status_var.set(f"Region removed from selected mask.")

        # 3. If still not modified, try to remove from any confirmed annotation mask
        if not modified:
            for label, masks_list in self.annotation_masks.items():
                for i, mask in enumerate(masks_list):
                    if np.any(mask[erase_mask_bool]):
                        self.save_to_history()
                        self.annotation_masks[label][i] = np.logical_and(mask, ~erase_mask_bool)
                        self.is_modified = True
                        modified = True
                        self.status_var.set(f"Region removed from mask with label '{label}'.")
                        break  # Modify only one mask per label list per click
                if modified:
                    break  # Stop iterating labels if a mask was modified

        if not modified:
            self.status_var.set("No mask found to erase at clicked position.")
        else:
            self.display_image(self.image_np)  # Refresh display if changes occurred
        return modified

    def reset_annotation(self):
        """Resets all temporary and current annotation state for the current image."""
        self.points = []
        self.labels = []
        self.masks = None
        self.scores = None
        self.current_mask_idx = 0
        self.selected_mask = None
        self.annotation_complete = False
        self.is_modified = False
        self.history = []  # Clear undo history

        self.clear_polygon()  # Clear any polygon drawing
        self._clear_selection_state()  # Clear edit mode selection

        # If currently in edit mode, re-prepare edit mode state
        if self.image_np is not None:
            current_mode = self.mode_var.get()
            if current_mode == "Edit Labels":
                self._prepare_for_editing()  # Re-calculate bounding boxes for existing annotations
            self.display_image(self.image_np)

    def save_to_history(self):
        """Saves the current annotation state to history for undo functionality."""
        state = {
            'points': self.points.copy(),
            'labels': self.labels.copy(),
            'masks': self.masks.copy() if self.masks is not None else None,
            'scores': self.scores.copy() if self.scores is not None else None,
            'current_mask_idx': self.current_mask_idx,
            'selected_mask': self.selected_mask.copy() if self.selected_mask is not None else None,
            # Deep copy annotation_masks to avoid sharing references
            'annotation_masks': {k: [m.copy() for m in v] for k, v in self.annotation_masks.items()},
            'is_modified': self.is_modified,
            'polygon_points': self.polygon_points.copy(),
            'closed_polygon': self.closed_polygon,
        }
        self.history.append(state)

    def undo(self):
        """Reverts the application to the previous state in history."""
        if not self.history:
            messagebox.showinfo("Info", "No operations to undo.")
            return
        state = self.history.pop()  # Get the last saved state
        # Restore all state variables
        self.points = state['points']
        self.labels = state['labels']
        self.masks = state['masks']
        self.scores = state['scores']
        self.current_mask_idx = state['current_mask_idx']
        self.selected_mask = state['selected_mask']
        self.annotation_masks = state['annotation_masks']
        self.is_modified = state['is_modified']
        self.polygon_points = state['polygon_points']
        self.closed_polygon = state['closed_polygon']

        if self.image_np is not None:
            # Update edit mode state after undo
            if self.mode_var.get() == "Edit Labels":
                self._prepare_for_editing()  # Recalculate editable regions
                self._clear_selection_state()  # Clear any active selection
            self.display_image(self.image_np)
            if self.is_polygon_mode:
                self.redraw_polygon()  # Ensure polygon drawing is redrawn correctly
        messagebox.showinfo("Info", "Undid last operation.")

    def add_point(self, x, y, is_positive=True):
        """
        Adds an interactive point for SAM prediction.
        Now includes a check to prevent adding points within locked (already annotated) regions.
        """
        if self.image_np is None: return False

        # Get the combined mask of all confirmed annotation regions
        locked_mask = self._get_locked_mask()
        if locked_mask is not None and locked_mask[y, x]:  # Check if clicked point (y,x) is inside a locked region
            messagebox.showwarning("Warning", "This point is within an already annotated area. Please click in unannotated regions.")
            self.status_var.set(f"Cannot add point in annotated area: ({x}, {y})")
            return False  # Prevent adding the point

        self.save_to_history()  # Save current state to history before adding point
        label = 1 if is_positive else 0
        self.points.append([y, x])  # SAM expects points in (y, x) format
        self.labels.append(label)
        self.is_modified = True
        point_type = "positive" if is_positive else "negative"
        self.status_var.set(f"Added {point_type} point: ({x}, {y}), Total points: {len(self.points)}")
        return True  # Point added successfully

    def _get_locked_mask(self):
        """
        Creates a boolean mask that combines all currently confirmed annotation regions.
        This mask represents "locked" areas where new annotations should not overlap.

        Returns:
            np.ndarray (dtype=bool): A boolean mask where True indicates an annotated pixel,
                                      or None if no annotations exist.
        """
        if not self.annotation_masks or self.image_np is None:
            return None

        h, w = self.image_np.shape[:2]
        locked_mask = np.zeros((h, w), dtype=bool)

        for _, masks_list in self.annotation_masks.items():
            for mask in masks_list:
                # Use logical OR to combine all masks into a single locked region mask
                # Ensure masks are boolean before ORing
                locked_mask = np.logical_or(locked_mask, mask.astype(bool))

        return locked_mask

    def predict_masks(self):
        """
        Triggers SAM to predict masks based on current points.
        Crucially, it provides SAM with a masked image and post-processes results
        to ensure predicted masks do not overlap with confirmed regions.
        """
        if self.image_np is None:
            messagebox.showwarning("Warning", "No image loaded.")
            return
        if len(self.points) == 0:
            messagebox.showwarning("Warning", "Please add at least one point first.")
            return
        if self.predictor is None:  # Ensure predictor is initialized
            messagebox.showerror("Error", "SAM predictor not initialized. Please reload the image.")
            return

        self.status_var.set("Predicting masks...")
        self.update_idletasks()  # Force UI update

        # Create a masked image for SAM prediction
        # Annotated regions will be filled with black so SAM "doesn't see" them.
        # This step is done before each prediction to ensure the latest locked_mask is used.
        masked_image_for_sam = self.image_np.copy()
        locked_mask = self._get_locked_mask()
        if locked_mask is not None:
            masked_image_for_sam[locked_mask] = 0  # Set locked region pixels to black

        # Set the masked image to the predictor. This forces SAM to recompute image embeddings.
        self.predictor.set_image(masked_image_for_sam)

        points_for_sam = np.array([[p[1], p[0]] for p in self.points])
        labels_array = np.array(self.labels)

        start_time = time.time()
        try:
            masks, scores, logits = self.predictor.predict(
                point_coords=points_for_sam,
                point_labels=labels_array,
                multimask_output=True
            )
        except Exception as e:
            print(f"Mask prediction failed: {e}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Mask prediction failed: {str(e)}")
            return
        end_time = time.time()

        # After prediction, we still need to do a final check to ensure SAM didn't predict
        # on blacked-out areas (though using masked input should minimize this).
        # This post-processing here is a double safeguard.
        if locked_mask is not None:
            unlocked_area = ~locked_mask  # Unlocked area is the complement of locked area
            masks = [np.logical_and(m, unlocked_area) for m in masks]  # Logical AND each predicted mask with unlocked area

        valid_masks = []
        valid_scores = []
        for mask, score in zip(masks, scores):
            if np.any(mask):  # Check if the mask still has any non-zero pixels (i.e., is not empty)
                valid_masks.append(mask)
                valid_scores.append(score)

        if not valid_masks:
            messagebox.showwarning("Warning", "Predicted masks were all empty or entirely within annotated areas. Try adjusting your clicks in unannotated regions.")
            self.masks = None
            self.scores = None
            self.current_mask_idx = 0
            self.display_image(self.image_np)
            return

        sorted_ind = np.argsort(valid_scores)[::-1]
        self.masks = np.array(valid_masks)[sorted_ind][:3]  # Get top 3 masks by score
        self.scores = np.array(valid_scores)[sorted_ind][:3]
        self.current_mask_idx = 0
        self.is_modified = True
        self.save_to_history()
        messagebox.showinfo("Info", f"Prediction complete in {end_time - start_time:.2f}s. Found {len(self.masks)} valid new masks.")
        self.display_image(self.image_np)

    def next_mask(self):
        """Displays the next predicted mask from SAM output."""
        if self.masks is None or len(self.masks) <= 1:
            messagebox.showinfo("Info", "No more masks available.")
            return
        self.current_mask_idx = (self.current_mask_idx + 1) % len(self.masks)  # Cycle through masks
        self.status_var.set(
            f"Current Mask: {self.current_mask_idx + 1}/{len(self.masks)}, Score: {self.scores[self.current_mask_idx]:.3f}")
        if self.image_np is not None: self.display_image(self.image_np)

    def select_mask(self):
        """Selects the currently displayed predicted mask for confirmation."""
        if self.masks is None or len(self.masks) == 0 or self.current_mask_idx >= len(self.masks):
            messagebox.showwarning("Warning", "No mask available to select.")
            return
        self.save_to_history()  # Save state before selecting
        self.selected_mask = self.masks[self.current_mask_idx].copy()  # Deep copy to avoid modification issues
        self.is_modified = True
        messagebox.showinfo("Info", f"Mask {self.current_mask_idx + 1}/{len(self.masks)} selected. Please assign a label.")
        if self.image_np is not None: self.display_image(self.image_np)

    def on_label_change(self, event=None):
        """Handles changes in the label combobox, adding new labels if typed."""
        new_label = self.label_var.get()
        if new_label and new_label not in self.available_labels:
            self.available_labels.append(new_label)
            self.label_combo['values'] = self.available_labels  # Update combobox options
            if len(self.available_labels) > len(self.colors):
                self.colors = self.generate_colors(len(self.available_labels))  # Generate more colors
        self.current_label = new_label

    def confirm_label(self):
        """
        Confirms the `selected_mask` with the `current_label` and adds it to `annotation_masks`.
        This method assumes `selected_mask` has already been processed to exclude overlaps.
        """
        if self.selected_mask is None:
            messagebox.showwarning("Warning", "Please select a mask first (via SAM prediction or polygon drawing).")
            return
        label = self.current_label
        if not label or label == "" or label == DEFAULT_LABELS[0]:
            messagebox.showwarning("Warning", "Please select a valid label (not background).")
            return
        if not np.any(self.selected_mask):
            messagebox.showwarning("Warning", "The selected region is empty and cannot be confirmed.")
            self.selected_mask = None  # Clear invalid selection
            self.display_image(self.image_np)
            return

        self.save_to_history()  # Save state before confirming

        if label not in self.annotation_masks:
            self.annotation_masks[label] = []
        self.annotation_masks[label].append(self.selected_mask.copy())  # Add a copy of the mask
        action = "Added" if len(self.annotation_masks[label]) == 1 else "Overlayed"  # Simplified message

        self.is_modified = True
        self.selected_mask = None  # Clear selected mask after confirmation

        # Reset state for the next annotation task
        self.points = []
        self.labels = []
        self.masks = None
        self.scores = None
        self.current_mask_idx = 0
        self.clear_polygon()  # Clear any remaining polygon elements

        messagebox.showinfo("Info", f"Region {action} and locked with label '{label}'.")

        # Reset label selection to background to prompt for new label for next region
        self.label_var.set(DEFAULT_LABELS[0])
        self.current_label = DEFAULT_LABELS[0]

        if self.image_np is not None: self.display_image(self.image_np)

    def _prepare_for_editing(self):
        """
        Prepares data for edit mode by calculating bounding boxes for each confirmed annotation mask.
        """
        self.editable_regions = []
        if self.image_np is None:
            return

        # Iterate through all confirmed masks and calculate their bounding boxes
        for label, masks_list in self.annotation_masks.items():
            for mask in masks_list:
                if not np.any(mask):  # Skip empty masks
                    continue
                # Find contours to get bounding box.
                # Use RETR_EXTERNAL to get only external contours if mask has holes.
                contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if not contours:
                    continue
                # Combine all contours for a given mask to get a single overall bounding box
                all_points = np.concatenate(contours)
                x, y, w, h = cv2.boundingRect(all_points)
                # Store original mask reference along with its label/bbox for editing
                self.editable_regions.append({'mask': mask, 'label': label, 'bbox': (x, y, w, h)})

    def _clear_selection_state(self):
        """Clears all selection and hover states in edit mode."""
        self.selected_region_index = None
        self.hovered_region_index = None
        self.update_label_button.config(state=tk.DISABLED)  # Disable update button
        self.label_var.set(DEFAULT_LABELS[0])  # Reset label combobox
        self.current_label = DEFAULT_LABELS[0]
        # self.editable_regions = [] # State might have changed, so clear prepared regions - handled in prepare_for_editing

    def update_selected_label(self):
        """Updates the label of the currently selected annotated region."""
        if self.selected_region_index is None:
            messagebox.showwarning("Warning", "No region selected to update.")
            return

        new_label = self.label_var.get()
        if not new_label or new_label == DEFAULT_LABELS[0]:
            messagebox.showwarning("Warning", "Please select a valid new label.")
            return

        region_to_update = self.editable_regions[self.selected_region_index]
        old_label = region_to_update['label']
        mask_to_move = region_to_update['mask']  # Get a reference to the actual mask object

        if new_label == old_label:
            messagebox.showinfo("Info", "New and old labels are the same. No change made.")
            return

        self.save_to_history()  # Save state before modifying

        # Remove the mask from its old label's list
        # Use 'is' to compare object identity to ensure the exact mask object is removed
        if old_label in self.annotation_masks:
            self.annotation_masks[old_label] = [m for m in self.annotation_masks[old_label] if m is not mask_to_move]
            if not self.annotation_masks[old_label]:  # If old label's list becomes empty, remove the key
                del self.annotation_masks[old_label]

        # Add the mask to its new label's list
        if new_label not in self.annotation_masks:
            self.annotation_masks[new_label] = []
        self.annotation_masks[new_label].append(mask_to_move)  # Add the same mask object

        self.is_modified = True
        messagebox.showinfo("Success", f"Region label updated from '{old_label}' to '{new_label}'.")

        # Reset selection state and re-prepare for editing to reflect changes
        self._clear_selection_state()
        self._prepare_for_editing()
        self.display_image(self.image_np)

    def complete_annotation(self):
        """
        Saves all current annotations for the image to a JSON file (LabelMe format)
        and saves a copy of the image.
        Then, moves to the next image.
        """
        if not self.annotation_masks:
            if not messagebox.askyesno("Prompt", "The current image has no annotations. Are you sure you want to complete and skip to the next?"):
                return
        if self.image_name == "" or self.image_np is None:
            messagebox.showerror("Error", "No image loaded, cannot save.")
            return

        try:
            base_name = self.image_name.rsplit('.', 1)[0]
            json_file = os.path.join(self.jsons_path, base_name + '.json')

            # Save a copy of the original image
            jpg_file_name = base_name + '.jpg'
            jpg_file_path = os.path.join(self.jpgs_path, jpg_file_name)

            img_pil = Image.fromarray(self.image_np)
            img_pil.save(jpg_file_path, "JPEG")

            height, width = self.image_np.shape[:2]
            # Initialize LabelMe JSON structure
            data = {
                "version": "5.0.1",
                "flags": {},
                "shapes": [],
                "imagePath": jpg_file_name,
                "imageData": None,
                "imageHeight": height,
                "imageWidth": width
            }

            # Convert all confirmed masks to polygon shapes for JSON
            for label, masks_list in self.annotation_masks.items():
                for mask_item in masks_list:
                    if not np.any(mask_item):  # Skip empty masks
                        continue
                    contours, _ = cv2.findContours(
                        mask_item.astype(np.uint8),
                        cv2.RETR_EXTERNAL,
                        cv2.CHAIN_APPROX_SIMPLE
                    )
                    for contour in contours:
                        if contour.shape[0] < 3:  # A polygon needs at least 3 points
                            continue
                        points = contour.reshape(-1, 2).tolist()  # Reshape to [[x,y], [x,y], ...]
                        shape = {
                            "label": label,
                            "points": points,
                            "group_id": None,
                            "shape_type": "polygon",
                            "flags": {}
                        }
                        data["shapes"].append(shape)

            # Save an empty JSON file even if no annotations to mark as "processed"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # Update cache and reset flags
            self.previous_annotations[self.image_name] = self.annotation_masks.copy()
            self.is_modified = False
            self.annotation_complete = True

            if data["shapes"]:
                messagebox.showinfo("Info", f"Annotations saved to {json_file}\nImage copy saved to {jpg_file_path}.")
            else:
                messagebox.showinfo("Info", f"Empty annotations saved to {json_file}, indicating no annotations needed for this image.")

            self._save_last_session_info()  # Save session state
            self.next_image()  # Automatically move to the next image

        except Exception as e:
            print(f"Failed to save annotations: {e}")
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to save annotations: {str(e)}")


def main():
    """Main function to run the SAM2 annotator application."""
    # Determine if running from PyInstaller bundle
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        try:
            application_path = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            application_path = os.getcwd()  # Fallback for interactive environments

    default_model_path = os.path.join(application_path, "weights", "sam2_hiera_large.pt")
    default_config_path = os.path.join(application_path, "configs", "sam2", "sam2_hiera_l.yaml")
    default_output_dir = os.path.join(application_path, "annotations_output")

    # --- USER: Please confirm these paths ---
    # !! IMPORTANT: Please modify the paths below to the correct paths on your computer !!
    # User-defined model, config, output, and image paths.
    # IMPORTANT: Please update these paths to your actual file locations.
    model_path_to_use = r"D:\python-deeplearning\CVlearn\SAM2\sam2-main\weights\sam2_hiera_large.pt"
    config_path_to_use = r"D:\python-deeplearning\CVlearn\SAM2\sam2-main\configs\sam2\sam2_hiera_l.yaml"
    output_dir_to_use = r"./annotations_sam2_tool"  # Output directory for generated annotations
    image_dir_to_use = r"D:\python-deeplearning\CVlearn\SAM2\sam2-main\VOCdevkit\VOC2007\JPEGImages_test_small"  # Directory containing images to annotate

    # Fallback to default paths if user-provided paths are not found
    if not os.path.exists(model_path_to_use) and os.path.exists(default_model_path):
        print(f"Warning: Provided model path not found. Using default path: {default_model_path}")
        model_path_to_use = default_model_path
    if config_path_to_use and not os.path.exists(config_path_to_use) and os.path.exists(default_config_path):
        print(f"Warning: Provided config file path not found. Using default path: {default_config_path}")
        config_path_to_use = default_config_path

    # Critical check: Ensure model path exists
    if not os.path.exists(model_path_to_use):
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Startup Error",
                             f"SAM2 model file not found: {model_path_to_use}\nPlease set the correct 'model_path_to_use' in the main() function.")
        sys.exit(1)
    # Warning for missing config, as it might still work with defaults
    if config_path_to_use and not os.path.exists(config_path_to_use):
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning("Startup Warning",
                               f"SAM2 config file not found: {config_path_to_use}\nWill attempt to use internal or SAM2 library default config.")

    # Create and run the application
    app = InteractiveSAM2Annotator(
        model_path=model_path_to_use,
        config_path=config_path_to_use,
        output_dir=output_dir_to_use,
        image_dir=image_dir_to_use
    )
    app.mainloop()


if __name__ == "__main__":
    main()