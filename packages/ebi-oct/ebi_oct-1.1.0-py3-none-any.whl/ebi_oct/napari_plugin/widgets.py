from magicgui import magicgui
import napari
from napari.utils.notifications import show_info
import numpy as np
from qtpy.QtWidgets import QFileDialog
from pathlib import Path

from ebi_oct.octools import processing_functions as ip

@magicgui(call_button="Load OCT")
def load_oct(viewer: napari.Viewer):
    filepath, _ = QFileDialog.getOpenFileName(None, 'Select OCT file', '', 'OCT files (*.oct)') # type: ignore
    if not filepath:
        show_info("No file selected.")
        return # Abbrechen
    
    stack, metadata = ip.load_oct(Path(filepath)) # type: ignore
    
    viewer.add_image(stack, name=metadata['filename'], colormap="magma", gamma=2.0, visible=False)
    
    stack_norm = (stack - stack.min()) / (stack.max() - stack.min())
    norm_layer = viewer.add_image(stack_norm, name='normalized', visible=True)
    norm_layer.metadata['oct_metadata'] = metadata # type: ignore

    show_info(f"Loaded {metadata['filename']}")

@magicgui(
            call_button="Apply Median Filter",
            filter_size={"widget_type": "SpinBox", "min": 1, "max": 101, "step": 2, "value": 3}
    )
def median_filter(filter_size, viewer: napari.Viewer):
    stack = viewer.layers['normalized'].data

    median_filtered = ip.median_blur(stack, filter_size)

    if 'median_filtered' in viewer.layers:
        viewer.layers['median_filtered'].data = median_filtered
    else:
        viewer.add_image(median_filtered, name="median_filtered", colormap="magma", gamma=2.0, visible=False)

@magicgui(call_button="Apply ROI 2D Filter",
            roi_size={"widget_type": "SpinBox", "min": 1, "max": 51, "step": 2, "value": 5}
)
def roi_filter_2D(roi_size, viewer: napari.Viewer):
    stack = viewer.layers['median_filtered'].data

    roi_filtered = ip.roi_filter_2D(stack, roi_size)

    if 'roi_filtered' in viewer.layers:
        viewer.layers['roi_filtered'].data = roi_filtered
    else:
        viewer.add_image(roi_filtered, name="roi_filtered", colormap="magma", gamma=2.0, visible=False)

@magicgui(call_button="Locate Window",
            ymin={"widget_type": "SpinBox", "min": 0, "max": 1000, "step": 1, "value": 0},
            ymax={"widget_type": "SpinBox", "min": 0, "max": 1000, "step": 1, "value": 100},
            y_offset={"widget_type": "SpinBox", "min": -100, "max": 100, "step": 1, "value": 0}
)
def locate_window(ymin, ymax, y_offset, viewer: napari.Viewer):
    stack = viewer.layers['roi_filtered'].data
    stack_norm = viewer.layers['normalized'].data

    window_coords = ip.locate_window(stack, ymin, ymax, y_offset)
    label_stack = viz_coords(stack_norm, window_coords, pixel_value=1)

    if 'window_coords' in viewer.layers:
        layer = viewer.layers['window_coords']
        layer.data = label_stack
    else:
        layer = viewer.add_labels(label_stack, name='window_coords', visible=True)
    
    layer.metadata['window_coords'] = window_coords

@magicgui(call_button="Zero Out Window")
def zero_out_window(viewer: napari.Viewer):
    window_coords = viewer.layers['window_coords'].metadata.get('window_coords')
    stack_norm = viewer.layers['normalized'].data

    no_window = ip.zero_out_window(stack_norm, window_coords) # type: ignore

    if 'no_window' in viewer.layers:
        viewer.layers['no_window'].data = no_window
    else:
        viewer.add_image(no_window, name="no_window", colormap="magma", gamma=2.0, visible=True)

@magicgui(call_button="Locate Substratum",
            ymin={"widget_type": "SpinBox", "min": 0, "max": 1000, "step": 1, "value": 200},
            ymax={"widget_type": "SpinBox", "min": 0, "max": 1000, "step": 1, "value": 1000},
            y_offset={"widget_type": "SpinBox", "min": -100, "max": 100, "step": 1, "value": 0}
)
def locate_substratum(ymin, ymax, y_offset, viewer: napari.Viewer):
    stack = viewer.layers['roi_filtered'].data
    stack_norm = viewer.layers['normalized'].data

    substratum_coords = ip.locate_substratum(stack, ymin, ymax, y_offset)
    label_stack = viz_coords(stack_norm, substratum_coords, pixel_value=2)

    if 'substratum_coords' in viewer.layers:
        layer = viewer.layers['substratum_coords']
        layer.data = label_stack
    else:
        layer = viewer.add_labels(label_stack, name="substratum_coords", visible=True)
    
    layer.metadata['substratum_coords'] = substratum_coords

@magicgui(call_button="Zero Out Substratum")
def zero_out_substratum(viewer: napari.Viewer):
    substratum_coords = viewer.layers['substratum_coords'].metadata.get('substratum_coords')
    stack_norm = (
        viewer.layers['no_window'].data if 'no_window' in viewer.layers
        else viewer.layers['normalized'].data
    )

    no_substratum = ip.zero_out_substratum(stack_norm, substratum_coords) # type: ignore

    if 'no_substratum' in viewer.layers:
        viewer.layers['no_substratum'].data = no_substratum
    else:
        layer = viewer.add_image(no_substratum, name="no_substratum", colormap="magma", gamma=2.0, visible=True)
    
    init_thresh = ip.get_threshold(no_substratum)
    binarize.threshold.value = init_thresh
    for lay in viewer.layers:
        lay.visible = False
    layer.visible = True # type: ignore

@magicgui(
    threshold={'widget_type': 'FloatSpinBox', 'min': 0.0, 'max': 1.0, 'step': 0.001},
    auto_call=True
)
def binarize(threshold, viewer: napari.Viewer):
    stack = viewer.layers['no_substratum'].data

    # finetuning threshold toggle nur auf aktuellem slice
    binary = (stack > threshold).astype(np.uint8)

    if 'binary' in viewer.layers:
        viewer.layers['binary'].data = binary
    else:
        viewer.add_labels(binary, name="binary", visible=True)

@magicgui(
        outlier_size={'widget_type': 'SpinBox', 'min': 0, 'max': 100, 'step': 1, 'value': 2},
        auto_call=True
)
def remove_outliers(outlier_size, viewer: napari.Viewer):
    stack = viewer.layers['binary'].data

    cleaned_binary = ip.rm_outliers(stack, outlier_size)

    viewer.layers['binary'].data = cleaned_binary

@magicgui(
        call_button='Save stack+mask_stack',
        output_directory={"widget_type": "FileEdit", "mode": "d", "value": str(Path.home())}
)
def save(output_directory, viewer: napari.Viewer):
    stack = viewer.layers['normalized'].data
    binary_stack = viewer.layers['binary'].data
    metadata = viewer.layers['normalized'].metadata.get('oct_metadata')

    ip.save(stack, metadata, binary_stack, output_directory) # type: ignore


# Helper functions
def viz_coords(stack, coord_array, pixel_value):
    z, x = coord_array.shape
    y = stack.shape[1]
    label_stack = np.zeros((z, y, x), dtype=np.uint8)
    z_idx, x_idx = np.meshgrid(np.arange(z), np.arange(x), indexing='ij')
    y_idx = coord_array
    mask = (y_idx >= 0) & (y_idx < y)  # ensure indices are within bounds
    label_stack[z_idx[mask], y_idx[mask], x_idx[mask]] = pixel_value

    return label_stack
