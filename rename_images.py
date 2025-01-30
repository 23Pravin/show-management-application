import os
import shutil

def rename_images():
    image_dir = "images"
    
    # Get list of image files
    image_files = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    image_files.sort()  # Sort to ensure consistent ordering
    
    # Rename files
    for i, old_name in enumerate(image_files, 1):
        old_path = os.path.join(image_dir, old_name)
        new_name = f"image{i}.jpg"
        new_path = os.path.join(image_dir, new_name)
        
        # Create backup
        backup_path = os.path.join(image_dir, f"backup_{old_name}")
        shutil.copy2(old_path, backup_path)
        
        # Rename file
        os.rename(old_path, new_path)
        print(f"Renamed: {old_name} -> {new_name}")

if __name__ == "__main__":
    rename_images()
