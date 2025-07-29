import numpy as np
from PIL import Image

INVALID_ID = 0
INVALID_COLOR = (0, 0, 0)


def load_semantic_color_mapping(filename: str = "colors_fps_5k.npz") -> np.ndarray:
    """Loads a precomputed colormap."""
    from wai import WAI_COLORMAP_PATH

    return np.load(WAI_COLORMAP_PATH / filename).get("arr_0")


def apply_id_to_color_mapping(
    data_id: np.ndarray | Image.Image,
    semantic_color_mapping: np.ndarray,
) -> tuple[np.ndarray, dict[int, tuple[int, int, int]]]:
    """Maps semantic class/instance IDs to RGB colors."""
    if isinstance(data_id, Image.Image):
        data_id = np.array(data_id)

    max_color_id = semantic_color_mapping.shape[0] - 1
    max_data_id = data_id.max()
    if max_data_id > max_color_id:
        raise ValueError("The provided color palette does not have enough colors!")

    # Create palette containing the id->color mappings of the input data IDs
    unique_indices = np.unique(data_id).tolist()
    color_palette = {
        index: semantic_color_mapping[index, :].tolist() for index in unique_indices
    }

    data_colors = semantic_color_mapping[data_id]

    return data_colors, color_palette
