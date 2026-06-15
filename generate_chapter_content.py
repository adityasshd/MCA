import os
import sys
from pathlib import Path
import json
import asyncio
import websockets

from src.rag.indexer import extract_text_from_pdf
from src.core.prompt_manager import PromptManager

async def process_chapters():
    chapters_dir = Path("/home/aditya/DEV/MCA/data/processed/chapters")
    output_base_dir = Path("/home/aditya/DEV/MCA/data/processed/chapter_content")
    
    subjects_to_process = [
        "ANALYTICAL_SKILLS-I",
        "DATA_COMMUNICATION_AND_NETWORKING"
    ]
    
    api_base_url = """
https://sister-prozac-revisions-worldwide.trycloudflare.com
""".strip()

    # Convert https:// to wss:// for WebSocket connection
    ws_url = api_base_url.replace("http://", "ws://").replace("https://", "wss://") + "/generate_ws"
    
    print(f"\n🌍 Connecting to WebSocket: {ws_url}")
    try:
        # The websockets library automatically sends keep-alive pings in the background
        # This completely bypasses the 100-second Cloudflare timeout limit!
        async with websockets.connect(ws_url, ping_interval=20, ping_timeout=120, max_size=None) as websocket:
            print("✅ WebSocket connected successfully!")
            
            for subject in subjects_to_process:
                subject_dir = chapters_dir / subject
                if not subject_dir.exists() or not subject_dir.is_dir():
                    continue
                    
                out_subject_dir = output_base_dir / subject
                out_subject_dir.mkdir(parents=True, exist_ok=True)
                
                print(f"\nProcessing Subject: {subject}")
                
                for pdf_path in sorted(subject_dir.glob("*.pdf")):
                    unit_name = pdf_path.stem
                    out_file = out_subject_dir / f"{unit_name}.md"
                    
                    if out_file.exists():
                        print(f"  Skipping {unit_name}, already generated.")
                        continue
                        
                    print(f"  Extracting text from {unit_name}...")
                    try:
                        text, _ = extract_text_from_pdf(pdf_path)
                    except Exception as e:
                        print(f"    Failed to extract text: {e}")
                        continue
                        
                    if not text.strip():
                        print(f"    No text extracted. Skipping.")
                        continue
                        
                    # We can use massive chunks again because WebSockets don't timeout!
                    chunk_size = 12000
                    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
                    
                    print(f"    Sending requests to WS API (Total length: {len(text)} chars | Chunks: {len(chunks)})...")
                    
                    all_summaries = []
                    chunk_failed = False
                    
                    for i, chunk in enumerate(chunks):
                        print(f"      -> Processing chunk {i+1}/{len(chunks)}...")
                        prompt = PromptManager().get_prompt("chapter_content_summary", text=chunk)
                        
                        payload = {
                            "prompt": prompt,
                            "max_tokens": 4096,  # Restored to max length!
                            "temperature": 0.7
                        }
                        
                        await websocket.send(json.dumps(payload))
                        
                        try:
                            # Wait for status messages
                            while True:
                                response_str = await websocket.recv()
                                data = json.loads(response_str)
                                
                                if data.get("status") == "error" or "error" in data:
                                    print(f"      ❌ API Error on chunk {i+1}: {data.get('error')}")
                                    chunk_failed = True
                                    break
                                    
                                elif data.get("status") == "generation_started":
                                    print(f"      -> Generation started on server...")
                                    
                                elif data.get("status") == "completed":
                                    extracted_text = data.get("response", "")
                                    if extracted_text:
                                        all_summaries.append(extracted_text)
                                        print(f"      -> Chunk {i+1} completed successfully.")
                                    else:
                                        print(f"      ⚠️ Warning: Empty response from API for chunk {i+1}.")
                                    break
                                    
                        except Exception as e:
                            print(f"      ❌ WS Request failed on chunk {i+1}: {e}")
                            chunk_failed = True
                            break
                    
                    if not chunk_failed and all_summaries:
                        with open(out_file, "w", encoding="utf-8") as f:
                            f.write("\n\n---\n\n".join(all_summaries))
                        print(f"    ✅ Saved full chapter content to {out_file.name}")
                        print("    Waiting 3 seconds before next chapter...")
                        await asyncio.sleep(3)
                    elif chunk_failed:
                        print("    Skipping to next chapter due to failure...")
                        await asyncio.sleep(5)
                        
    except Exception as e:
        print(f"❌ Failed to connect or lost connection: {e}")

def main():
    asyncio.run(process_chapters())

if __name__ == "__main__":
    main()
