import numpy as np
from stl import mesh
import freetype
import os

def create_text_stl(text, output_file="output.stl", font_size=150, extrusion_depth=10, letter_spacing=50):
    """
    Create an STL file from input text.

    Args:
        text (str): The text to convert to STL
        output_file (str): Name of the output STL file
        font_size (int): Size of the font
        extrusion_depth (float): Depth of the 3D extrusion
        letter_spacing (int): Additional spacing between letters in pixels
    """
    # Load a default font (using system font)
    face = freetype.Face("/System/Library/Fonts/Helvetica.ttc")
    face.set_char_size(font_size * 64)

    # Process each character separately
    char_meshes = []
    current_x = 0

    for char in text:
        # Skip spaces
        if char == ' ':
            current_x += font_size
            continue

        # Load the character and get metrics before processing bitmap
        face.load_char(char)
        advance_x = face.glyph.advance.x >> 6
        bitmap = face.glyph.bitmap

        if bitmap.rows == 0 or bitmap.width == 0:
            current_x += advance_x
            continue

        # Convert bitmap to numpy array
        char_bitmap = np.array(bitmap.buffer, dtype=np.uint8).reshape(bitmap.rows, bitmap.width)
        char_bitmap = char_bitmap > 0

        # Create vertices and faces for this character
        vertices = []
        faces = []

        # Create front and back faces
        for y in range(char_bitmap.shape[0]):
            for x in range(char_bitmap.shape[1]):
                if char_bitmap[y, x]:
                    # Calculate actual position
                    pos_x = current_x + x
                    pos_y = y

                    # Front face vertices
                    v1 = [pos_x, pos_y, extrusion_depth]
                    v2 = [pos_x + 1, pos_y, extrusion_depth]
                    v3 = [pos_x, pos_y + 1, extrusion_depth]
                    v4 = [pos_x + 1, pos_y + 1, extrusion_depth]

                    # Back face vertices
                    v5 = [pos_x, pos_y, 0]
                    v6 = [pos_x + 1, pos_y, 0]
                    v7 = [pos_x, pos_y + 1, 0]
                    v8 = [pos_x + 1, pos_y + 1, 0]

                    # Add vertices
                    current_len = len(vertices)
                    vertices.extend([v1, v2, v3, v4, v5, v6, v7, v8])

                    # Add faces (triangles)
                    faces.extend([
                        # Front face
                        [current_len, current_len+1, current_len+2],
                        [current_len+1, current_len+3, current_len+2],
                        # Back face
                        [current_len+4, current_len+6, current_len+5],
                        [current_len+5, current_len+6, current_len+7],
                        # Side faces
                        [current_len, current_len+2, current_len+4],
                        [current_len+2, current_len+6, current_len+4],
                        [current_len+1, current_len+5, current_len+3],
                        [current_len+3, current_len+5, current_len+7],
                        [current_len, current_len+4, current_len+1],
                        [current_len+1, current_len+4, current_len+5],
                        [current_len+2, current_len+3, current_len+6],
                        [current_len+3, current_len+7, current_len+6]
                    ])

        if vertices:
            vertices = np.array(vertices)
            faces = np.array(faces)
            char_mesh = mesh.Mesh(np.zeros(len(faces), dtype=mesh.Mesh.dtype))
            for i, f in enumerate(faces):
                for j in range(3):
                    char_mesh.vectors[i][j] = vertices[f[j]]
            char_meshes.append(char_mesh)

        # Move to next character position with additional spacing
        current_x += advance_x
        current_x += letter_spacing

    # Combine all character meshes
    if char_meshes:
        combined_mesh = mesh.Mesh(np.concatenate([m.data for m in char_meshes]))

        # Rotate the mesh to stand upright (90 degrees around X axis)
        combined_mesh.rotate([1, 0, 0], np.pi/2)

        # Center the text
        combined_mesh.translate([-np.mean(combined_mesh.vectors[:, :, 0]),
                              -np.min(combined_mesh.vectors[:, :, 1]),
                              -np.mean(combined_mesh.vectors[:, :, 2])])

        # Scale the final mesh to a reasonable size
        scale_factor = 0.1  # Adjust this value to change the overall size
        combined_mesh.vectors *= scale_factor

        # Save the mesh to STL file
        combined_mesh.save(output_file)
        print(f"STL file has been created: {output_file}")
    else:
        print("No valid characters to create mesh")

if __name__ == "__main__":
    text = input("Enter the text to convert to STL: ")
    output_file = "text_3d.stl"
    create_text_stl(text, output_file, font_size=150, extrusion_depth=10, letter_spacing=50)
