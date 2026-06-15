import os
from pathlib import Path
from src.rag.indexer import extract_text_from_pdf
from src.core.config import get_config
from src.core.models import ModelManager

def main():
    cfg = get_config()
    manager = ModelManager.from_config(cfg)
    
    subject = "DATA_COMMUNICATION_AND_NETWORKING"
    chapters_dir = Path(f"/home/aditya/DEV/MCA/data/processed/chapters/{subject}")
    content_dir = Path(f"/home/aditya/DEV/MCA/data/processed/chapter_content/{subject}")
    
    if not chapters_dir.exists() or not content_dir.exists():
        print("Directories not found.")
        return
        
    print(f"Verifying generated content for {subject} using {cfg.TIER2_MODEL}...\n")
    
    # We will verify just the first 3 files to save time
    count = 0
    for md_file in sorted(content_dir.glob("*.md")):
        if count >1:
            break
            
        unit_name = md_file.stem
        pdf_file = chapters_dir / f"{unit_name}.pdf"
        
        if not pdf_file.exists():
            print(f"[MISSING PDF] {pdf_file.name}")
            continue
            
        print(f"--- Verifying {unit_name} ---")
        try:
            pdf_text, _ = extract_text_from_pdf(pdf_file)
            
            with open(md_file, "r", encoding="utf-8") as f:
                md_text = f.read()
                
            # Sample first 1500 chars to avoid exceeding CPU memory/time limits for the small model
            pdf_sample = pdf_text[:1500]
            md_sample = md_text[:1500]
            print(f"Original PDF Text: {pdf_sample}")
            print(f"Generated Summary Text: {md_sample}")
            
            prompt = (
                f"Original PDF Text:\n{pdf_sample}\n\n"
                f"Generated Summary Text:\n{md_sample}\n\n"
                "Task: Verify if the 'Generated Summary Text' accurately corresponds to the 'Original PDF Text' "
                "without containing completely unrelated or hallucinated content. "
                "Answer starting with YES or NO, followed by a one-sentence reason."
            )
            
            result = manager.thinking.generate(prompt, max_tokens=100)
            print(f"Result: {result.strip()}\n")
            
        except Exception as e:
            print(f"Error during verification: {e}")
            
        count += 1

if __name__ == "__main__":
    main()
