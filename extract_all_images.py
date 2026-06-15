import os
import shutil
from pathlib import Path
from src.rag.indexer import extract_images_from_pdf

chapters_dir = Path("/home/aditya/DEV/MCA/data/processed/chapters")
images_dir = Path("/home/aditya/DEV/MCA/data/processed/images")

if images_dir.exists():
    print("Deleting old images directory...")
    shutil.rmtree(images_dir)

images_dir.mkdir(parents=True, exist_ok=True)

total_images = 0
for subject_dir in chapters_dir.iterdir():
    if not subject_dir.is_dir():
        continue
    
    print(f"\nProcessing Subject: {subject_dir.name}")
    for pdf_path in subject_dir.glob("*.pdf"):
        unit_name = pdf_path.stem
        out_dir = images_dir / subject_dir.name / unit_name
        
        extracted = extract_images_from_pdf(pdf_path, out_dir)
        total_images += len(extracted)
        if extracted:
            print(f"  {unit_name}: {len(extracted)} images")

print(f"\nDone! Extracted a total of {total_images} unique images across all units.")
