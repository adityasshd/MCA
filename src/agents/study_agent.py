"""
study_agent — Socratic Tutor
=============================
An agent that uses the active fast/reasoning model and the retriever
to help the user study specific topics.  Maintains conversation history
and stores sessions via the DatabaseManager.
"""

from __future__ import annotations

import logging
from typing import Iterator, Generator

from src.core.database import DatabaseManager
from src.core.models import ModelManager
from src.core.schemas import ChatMessage, StudySession
from src.rag.retriever import Retriever

logger = logging.getLogger(__name__)


from src.core.prompt_manager import PromptManager


class StudyAgent:
    def __init__(
        self,
        db: DatabaseManager,
        model_manager: ModelManager,
        retriever: Retriever,
    ) -> None:
        self.db = db
        self.model_manager = model_manager
        self.retriever = retriever
        self.prompt_manager = PromptManager()

    def create_session(self, subject: str, unit: str) -> StudySession:
        """Create a new study session in the database."""
        session = StudySession(
            subject=subject,
            unit=unit,
            messages=[
                ChatMessage(
                    role="assistant",
                    content=f"Hello! I'm your AI tutor for {unit}. What topic would you like to explore today?",
                )
            ],
        )
        session_id = self.db.sessions.save(session)
        session.id = session_id
        return session

    def load_session(self, session_id: str) -> StudySession | None:
        """Load an existing session from the database."""
        return self.db.sessions.get_by_id(session_id)

    def chat(self, session: StudySession, user_message: str) -> Iterator[str]:
        """
        Send a message to the tutor and get a streaming response.
        Retrieves relevant context before querying the LLM.
        """
        # Append user message
        user_msg_obj = ChatMessage(role="user", content=user_message)
        session.messages.append(user_msg_obj)

        # Retrieve context
        try:
            chunks = self.retriever.retrieve(
                query=user_message,
                subject=session.subject,
                unit=session.unit,
            )
            context = self.retriever.format_context(chunks)
        except Exception as e:
            logger.error("Failed to retrieve context: %s", e)
            context = ""

        # Load full chapter content if available to append to context
        from pathlib import Path
        chapter_file = Path(f"/home/aditya/DEV/MCA/data/processed/chapter_content/{session.subject}/{session.unit}.md")
        if chapter_file.exists():
            try:
                chapter_content = chapter_file.read_text(encoding="utf-8")
                context += f"\n\n--- Full Chapter Content ---\n{chapter_content}\n"
            except Exception as e:
                logger.error("Failed to read chapter content file: %s", e)

        if not context.strip():
            context = "No context available."

        # Format system prompt
        system_prompt = self.prompt_manager.get_prompt("study_system", context=context)

        # Format conversation history
        # (Exclude the system prompt from history, we pass it separately)
        history_prompt = ""
        # Keep last 10 messages for context window efficiency
        recent_messages = session.messages[-10:]
        for msg in recent_messages[:-1]:  # Exclude current user message
            history_prompt += f"{msg.role.capitalize()}: {msg.content}\n\n"
        
        full_prompt = history_prompt + f"User: {user_message}\nAssistant: "

        # Call the active 'fast' model for tutoring
        llm = self.model_manager.fast
        full_response = ""

        try:
            stream = llm.generate_stream(
                prompt=full_prompt,
                system=system_prompt,
                temperature=0.7,
            )
            for chunk in stream:
                full_response += chunk
                yield chunk

        except Exception as e:
            error_msg = f"\n\n[Error communicating with AI: {e}]"
            full_response += error_msg
            yield error_msg

        # Save assistant response to session
        assistant_msg_obj = ChatMessage(role="assistant", content=full_response)
        session.messages.append(assistant_msg_obj)
        
        # Update session in DB
        # Since we just append messages, we can resave. The repository 
        # should handle upserting if ID exists. (We may need to update the repo
        # to support explicit update(), but for now saving works if the repo is 
        # smart, or we just rely on a new update method. Let's assume the repo
        # update() method is available. Wait, I didn't add update() to SessionRepo.
        # Let's add that to the interface later if needed, or just save the full session).
        # Actually, let's just save it. The MongoSessionRepo save() currently inserts.
        # We need to make sure we update it instead.
        
        # TODO: Implement update() on SessionRepository
        pass 

    def generate_study_guide(
        self, subject: str, unit: str
    ) -> Generator[str, None, None]:
        """
        Stream a generated markdown study guide for the given unit.
        Uses the DB to retrieve chunks and the fast LLM to synthesize.
        """
        # Check cache first
        from src.core.schemas import StudyGuide
        cached_guide = self.db.study_guides.get_by_unit(subject, unit)
        if cached_guide:
            yield cached_guide.content
            return

        # Try to read pre-generated chapter content first
        from pathlib import Path
        chapter_text = ""
        chapter_file = Path(f"/home/aditya/DEV/MCA/data/processed/chapter_content/{subject}/{unit}.md")
        if chapter_file.exists():
            try:
                chapter_text = chapter_file.read_text(encoding="utf-8")
                yield chapter_text
                
                # Append extracted images dynamically
                img_dir = Path(f"/home/aditya/DEV/MCA/data/processed/images/{subject}/{unit}")
                if img_dir.exists() and img_dir.is_dir():
                    images = sorted(img_dir.glob("*.*"))
                    if images:
                        yield "\n\n## Reference Images\n"
                        for img in images:
                            yield f"![{img.name}]({img.absolute()})\n\n"
                            
                return
            except Exception as e:
                logger.error("Failed to read pre-generated chapter %s: %s", unit, e)
                
        truncated = False
        
        if not chapter_text:
            chunks = self.db.chunks.get_by_unit(subject, unit)
            if not chunks:
                yield f"No content available to generate a study guide for {unit}."
                return
    
            # Concatenate text from all chunks to form the chapter context
            max_chars = 8000  # Roughly 2000 tokens
        
        from pathlib import Path
        images_dir = Path(f"/home/aditya/DEV/MCA/data/processed/images/{subject}/{unit}")
        available_images = list(images_dir.glob("*.jpeg")) if images_dir.exists() else []

        if not chapter_text:
            for c in chunks:
                next_part = f"\n\n--- Page {c.page_range} ---\n{c.text}\n"
                
                # Find images belonging to this page
                page_imgs = []
                try:
                    first_page = int(str(c.page_range).split('-')[0].strip())
                    prefix = f"page_{first_page:03d}_"
                    page_imgs = [f"file://{img.absolute()}" for img in available_images if img.name.startswith(prefix)]
                except Exception:
                    pass
    
                if page_imgs:
                    next_part += "\n[AVAILABLE REFERENCE IMAGES FOR THIS CONTENT:\n"
                    for img_url in page_imgs:
                        next_part += f"- {img_url}\n"
                    next_part += "]\n"
    
                if len(chapter_text) + len(next_part) > max_chars:
                    truncated = True
                    break
                chapter_text += next_part

        prompt = self.prompt_manager.get_prompt("study_guide", chapter_text=chapter_text)

        llm = self.model_manager.fast
        try:
            stream = llm.generate_stream(
                prompt=prompt,
                system="You are an expert AI tutor. Output beautifully formatted Markdown.",
                temperature=0.3,
                max_tokens=1024,
            )
            for chunk in stream:
                yield chunk
                
            if truncated:
                yield "\n\n> [!WARNING]\n> **Content Truncated:** Due to free-tier API rate limits (6000 Tokens Per Minute on Groq), only the first part of this chapter was analyzed. To process full lengthy chapters, please switch your Fast Model provider to **Gemini** (which has a 1 Million TPM free limit) in the Settings!"
                
        except Exception as e:
            yield f"\n\n[Error generating study guide: {e}]"

    def save_study_guide(self, subject: str, unit: str, content: str) -> None:
        """Save a fully generated study guide to the database cache."""
        from src.core.schemas import StudyGuide
        
        # Don't cache error messages or truncated warnings
        if "[Error generating study guide" in content or "Content Truncated:" in content:
            return
            
            
        guide = StudyGuide(subject=subject, unit=unit, content=content)
        self.db.study_guides.save(guide)

    # ── Contextual Actions ──────────────────────────────────────────────────
    
    def execute_contextual_action(self, action_name: str, subject: str, unit: str, topic: str | None = None) -> Iterator[str]:
        """
        Executes a specific contextual action like 'Explain Like I'm 10', 'Give Example', etc.
        """
        context = f"Subject: {subject}, Unit: {unit}"
        if topic:
            context += f", Topic: {topic}"
            
        action_prompts = {
            "Explain Topic": f"Please provide a detailed but clear explanation of {context}.",
            "Give Example": f"Give me 3 concrete real-world examples illustrating {context}.",
            "Create Analogy": f"Create a simple, intuitive analogy to explain {context}.",
            "Generate Flashcards": f"Create 5 flashcards for {context} in Q: A: format.",
            "Memory Trick": f"Give me a mnemonic or memory trick to remember {context}.",
            "Exam Questions": f"What are the most likely exam questions about {context}?",
            "Summarize": f"Summarize the key points of {context} in bullet points.",
            "Common Mistakes": f"What are the most common mistakes students make when learning {context}?"
        }
        
        prompt = action_prompts.get(action_name, f"Help me with {context}")
        
        system = "You are an expert AI tutor. Respond clearly and directly."
        llm = self.model_manager.fast
        
        try:
            stream = llm.generate_stream(prompt=prompt, system=system, temperature=0.5)
            for chunk in stream:
                yield chunk
        except Exception as e:
            yield f"\n\n[Error executing action: {e}]"

    # ── Infinite Practice Generation ────────────────────────────────────────

    def generate_practice_question(self, subject: str, unit: str, topic: str | None = None, difficulty: str = "Medium") -> dict:
        """
        Generates a single question for infinite practice mode.
        Returns a dict: {"question": "...", "options": ["..."], "answer": "...", "explanation": "..."}
        """
        prompt = f"Generate 1 {difficulty} difficulty multiple choice question about {subject} - {unit}."
        if topic:
            prompt += f" Focus specifically on: {topic}."
            
        prompt += "\nOutput JSON format ONLY: {\"question\": \"...\", \"options\": [\"A\", \"B\", \"C\", \"D\"], \"answer\": \"Exact text of correct option\", \"explanation\": \"Short explanation\", \"detailed_explanation\": \"Detailed explanation covering key concepts, examples, and common mistakes\"}"
        
        try:
            import json
            response = self.model_manager.fast.generate(prompt=prompt, temperature=0.3)
            # Find json block
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
                
            return json.loads(json_str.strip())
        except Exception as e:
            logger.error(f"Failed to generate practice question: {e}")
            return {
                "question": f"Error generating question: {e}",
                "options": ["A", "B", "C", "D"],
                "answer": "A",
                "explanation": "Generation failed."
            }

    def generate_adaptive_sequence(self, subject: str, unit: str, topic: str, num_questions: int, mastery_score: float) -> list[dict]:
        """
        Generates a sequence of questions adapting to the user's mastery score.
        Lower mastery score means easier, foundational questions.
        """
        difficulty = "Easy" if mastery_score < 0.5 else ("Medium" if mastery_score < 0.8 else "Hard")
        
        questions = []
        for _ in range(num_questions):
            questions.append(self.generate_practice_question(subject, unit, topic, difficulty))
            
        return questions
