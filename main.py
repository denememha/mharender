import argparse
import os

try:
    import cv2
except ImportError:
    cv2 = None

import numpy as np
from PIL import Image


def load_image(file_path: str):
    """Load a 2D image from common formats. Supports JPEG, PNG. PDF and DWG are placeholders."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        raise NotImplementedError("PDF input handling not yet implemented.")
    if ext == ".dwg":
        raise NotImplementedError("DWG input handling not yet implemented.")
    if cv2 is None:
        raise ImportError("OpenCV is required for image loading. Please install opencv-python.")
    img = cv2.imread(file_path)
    if img is None:
        raise FileNotFoundError(f"Unable to read image: {file_path}")
    return img


def generate_height_map(image: np.ndarray) -> np.ndarray:
    """Generate a simple height map from the grayscale image."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    height_map = gray.astype(np.float32) / 255.0
    return height_map


def create_3d_mesh(height_map: np.ndarray):
    """Create a very simple 3D mesh from the height map.

    This function returns vertices and faces lists. Faces generation is left as a
    placeholder because full triangulation is non-trivial.
    """
    vertices = []
    faces = []
    h, w = height_map.shape
    for y in range(h):
        for x in range(w):
            z = height_map[y, x]
            vertices.append([float(x), float(y), float(z)])
    # Faces would be defined here.
    return vertices, faces


def apply_style(vertices, style: str):
    """Apply simple style transformations to vertices based on style."""
    if style == "classic":
        # Example: scale z-axis down for classic style
        return [[v[0], v[1], v[2] * 0.5] for v in vertices]
    elif style == "nostalgic":
        # Example: exaggerate z-axis for nostalgic style
        return [[v[0], v[1], v[2] * 1.5] for v in vertices]
    # modern style: return as-is
    return vertices


def apply_texture(vertices, texture_image: np.ndarray):
    """Placeholder for texture mapping."""
    # In a real implementation, you would compute UV coordinates and map
    # texture pixels onto the mesh. This is beyond the scope of this skeleton.
    return vertices


def save_obj(vertices, faces, output_path: str):
    """Save vertices and faces to a simple OBJ file."""
    with open(output_path, "w") as f:
        for v in vertices:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        for face in faces:
            # OBJ format uses 1-based indexing
            f.write("f " + " ".join(str(idx + 1) for idx in face) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Convert 2D drawings to 3D models with customizable styles and textures.")
    parser.add_argument("input_file", help="Path to the input 2D file (DWG, JPEG, PNG, PDF)")
    parser.add_argument("--style", choices=["modern", "classic", "nostalgic"], default="modern",
                        help="Base style for the 3D model")
    parser.add_argument("--texture", help="Optional path to an image file to use as a texture")
    parser.add_argument("--output", default="output.obj", help="Path for the output OBJ file")
    args = parser.parse_args()

    # Load 2D image
    image = load_image(args.input_file)

    # Generate height map and mesh
    height_map = generate_height_map(image)
    vertices, faces = create_3d_mesh(height_map)

    # Apply style
    vertices = apply_style(vertices, args.style)

    # Apply texture if provided
    if args.texture:
        texture_img = load_image(args.texture)
        vertices = apply_texture(vertices, texture_img)

    # Save OBJ
    save_obj(vertices, faces, args.output)
    print(f"Model saved to {args.output}")


if __name__ == "__main__":
    main()
