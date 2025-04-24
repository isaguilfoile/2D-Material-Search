import os

def rename_images_in_folder(folder_path):
    """rename all images in a folder to a better format"""
    # Normalize and print the folder path
    folder_path = os.path.abspath(folder_path)
    print(f"Looking in folder: {folder_path}")

    # Allowed image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}

    # List files with supported image extensions
    files = [f for f in os.listdir(folder_path)
             if os.path.isfile(os.path.join(folder_path, f)) and os.path.splitext(f)[1].lower() in image_extensions]

    if not files:
        print("No image files found.")
        return

    # Sort for consistent naming
    files.sort()

    # Rename each file
    for idx, filename in enumerate(files, start=1):
        ext = os.path.splitext(filename)[1]
        new_name = f"training_{idx:03}{ext}"
        old_path = os.path.join(folder_path, filename)
        new_path = os.path.join(folder_path, new_name)

        print(f"Renaming {old_path} to {new_path}")
        os.rename(old_path, new_path)

    print("Renaming complete.")

# Replace with your actual folder path
folder_path = "C:\\Users\\Croix\\sdp\\Nanomaterial_DeepLearning\\fullTrain\\to_resizee"
rename_images_in_folder(folder_path)
