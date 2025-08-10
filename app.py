import streamlit as st
import tempfile
import os

import numpy as np
from PIL import Image as PILImage

from main import load_image, generate_height_map, create_3d_mesh, apply_style, apply_texture, save_obj

# Configure Streamlit page
st.set_page_config(page_title="mharender - 2D to 3D Converter", layout="centered")

st.title("mharender: 2D to 3D Model Converter")

st.markdown(
    "Upload a 2D drawing (JPEG, PNG) and choose a style to generate a simple 3D model.\n"
    "This is a prototype web interface using Streamlit."
)

# File upload for input image
uploaded_file = st.file_uploader(
    "Upload your 2D drawing", type=["jpg", "jpeg", "png"],
    help="Accepted formats: .jpg, .jpeg, .png"
)

# Style selection
style = st.selectbox("Select a style template", ["modern", "classic", "nostalgic"], index=0)

# Optional texture image
texture_file = st.file_uploader(
    "Optional: upload a texture image", type=["jpg", "jpeg", "png"],
    help="Apply a texture image to the generated model (optional)"
)

# Optional custom description (not used in current prototype)
custom_description = st.text_input(
    "Optional: describe your desired style (not yet implemented)", ""
)

# Conversion button
if st.button("Convert"):
    if uploaded_file is None:
        st.error("Please upload a valid image file.")
    else:
        # Save uploaded file to a temporary location
        suffix = os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.read())
            input_path = tmp.name

        try:
            # Load image using main.py utility
            img = load_image(input_path)
        except Exception as e:
            st.error(f"Error loading image: {e}")
            os.unlink(input_path)
        else:
            # Convert loaded image to numpy array if it's a PIL Image
            if isinstance(img, PILImage):
                img_np = np.array(img)
            else:
                img_np = img
            
            # Generate height map and mesh
            height_map = generate_height_map(img_np)
            vertices, faces = create_3d_mesh(height_map)
            
            # Apply selected style
            vertices_styled = apply_style(vertices, style)
            
            # Apply texture if provided
            if texture_file is not None:
                tex_suffix = os.path.splitext(texture_file.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=tex_suffix) as tex_tmp:
                    tex_tmp.write(texture_file.read())
                    tex_path = tex_tmp.name
                try:
                    texture_img = load_image(tex_path)
                    if texture_img is not None:
                        vertices_styled = apply_texture(vertices_styled, texture_img)
                except Exception as e:
                    st.warning(f"Texture could not be applied: {e}")
                finally:
                    os.unlink(tex_path)
            
            # Save the resulting mesh to an OBJ file
            output_path = os.path.join(tempfile.gettempdir(), "output.obj")
            save_obj(output_path, vertices_styled, faces)
            
            # Provide download link for the generated model
            with open(output_path, "rb") as obj_file:
                st.download_button(
                    label="Download 3D Model (.obj)",
                    data=obj_file,
                    file_name="mharender_output.obj",
                    mime="text/plain"
                )
            st.success("Conversion complete! Download your model above.")
        finally:
            # Clean up temporary input file
            if os.path.exists(input_path):
                os.unlink(input_path)
