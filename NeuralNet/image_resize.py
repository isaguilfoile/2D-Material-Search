#simple image resizer to create 1000x1000 images for use in training and scanning

from PIL import Image, ImageOps
import os

def normalize_image(img):
    """Normalize image to span the full range [0, 255] using autocontrast."""
    return ImageOps.autocontrast(img)

def crop_images_in_folder(input_folder, output_folder, normalize, original, tile_size=1000):
    """crop images in folder to a given x by x size, pass input and output folder as well as if you want them normalized"""
    os.makedirs(output_folder, exist_ok=True)
    tile_count_total = 0

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
            image_path = os.path.join(input_folder, filename)
            img = Image.open(image_path)
            width, height = img.size

            if width < tile_size or height < tile_size:
                print(f"Skipping {filename}: image smaller than tile size.")
                continue

            base_name = os.path.splitext(filename)[0]
            tile_count = 0

            for top in range(0, height - tile_size + 1, tile_size):
                for left in range(0, width - tile_size + 1, tile_size):
                    box = (left, top, left + tile_size, top + tile_size)
                    tile = img.crop(box)

                    if(original):
                        # Save original tile with '_orig' suffix
                        original_filename = os.path.join(output_folder, f"{base_name}_{tile_count}_orig.jpg")
                        tile.save(original_filename)

                    if(normalize):
                        # Normalize the tile and save with '_norm' suffix
                        norm_tile = normalize_image(tile)
                        normalized_filename = os.path.join(output_folder, f"{base_name}_{tile_count}_norm.jpg")
                        norm_tile.save(normalized_filename)

                    tile_count += 1

            print(f"{tile_count} tiles processed from '{filename}'")
            tile_count_total += tile_count

    print(f"Total of {tile_count_total} tiles processed (each saved as original and normalized) in '{output_folder}'")

# Example usage
input_directory = "C:\\Users\\Croix\\sdp\\Nanomaterial_DeepLearning\\fullTrain\\to_resizee"
output_directory = "C:\\Users\\Croix\\sdp\\Nanomaterial_DeepLearning\\fullTrain\\1k"
crop_images_in_folder(input_directory, output_directory, True, True)
