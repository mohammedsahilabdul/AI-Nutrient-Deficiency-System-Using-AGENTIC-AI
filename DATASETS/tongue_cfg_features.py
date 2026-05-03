import os
import numpy as np

def extract_tongue_cfg_features(cfg_root):
    """
    Converts tongue CFG dataset structure into numeric features
    """

    folders = [
        "fiss",
        "fissure",
        "thick_coating",
        "tooth_mark",
        "yellow_coating"
    ]

    features = []

    for folder in folders:
        path = os.path.join(cfg_root, folder)
        features.append(1 if os.path.exists(path) else 0)

    fissure_area_path = os.path.join(cfg_root, "Total area of fissures")
    area_value = (
        len(os.listdir(fissure_area_path))
        if os.path.exists(fissure_area_path)
        else 0
    )

    features.append(area_value)

    return np.array(features, dtype=np.float32)
