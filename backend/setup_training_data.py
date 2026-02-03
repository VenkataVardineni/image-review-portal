"""
Helper script to create training data directory structure
"""
import os

CLASSES = [
    "safe_animal",
    "safe_landscape",
    "safe_portrait",
    "safe_food",
    "safe_object",
    "violence_weapon",
    "inappropriate",
    "violence_blood",
]

def create_structure():
    """Create the training data directory structure"""
    base_dir = "./data"
    
    for split in ["train", "validation"]:
        for class_name in CLASSES:
            dir_path = os.path.join(base_dir, split, class_name)
            os.makedirs(dir_path, exist_ok=True)
            print(f"Created: {dir_path}")
    
    # Create models directory
    os.makedirs("./models", exist_ok=True)
    print("Created: ./models")
    
    print("\nDirectory structure created!")
    print("Now add your training images to:")
    print("  - data/train/{class_name}/")
    print("  - data/validation/{class_name}/")
    print("\nExample:")
    print("  - data/train/safe_animal/dog1.jpg")
    print("  - data/train/violence_weapon/gun1.jpg")

if __name__ == "__main__":
    create_structure()

