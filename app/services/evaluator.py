import google.generativeai as genai
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.database import Essay
from app.config import API_KEY, AI_MODEL

# Configure Gemini API
genai.configure(api_key=API_KEY)

class EssayEvaluator:
    def __init__(self):
        self.model = genai.GenerativeModel(AI_MODEL)
    
    async def evaluate_essay(self, db: Session, essay_title: str, essay_content: str):
        """
        Evaluate an IELTS essay using the Gemini API with RAG approach
        """
        # Retrieve similar high-scoring reference essays for context
        reference_essays = self._get_reference_essays(db, essay_content)
        
        # Create evaluation prompt with context
        prompt = self._create_evaluation_prompt(essay_title, essay_content, reference_essays)
        
        # Generate evaluation using Gemini
        evaluation_text = await self._generate_evaluation(prompt)
        
        # Parse evaluation response
        evaluation = self._parse_evaluation_response(evaluation_text)
        
        return evaluation
    
    def _get_reference_essays(self, db: Session, essay_content: str, limit=3):
        """
        Get reference essays from the database
        In a production app, you'd use vector similarity or keyword matching
        Here we'll just get random high-scoring essays
        """
        reference_essays = db.query(Essay).filter(
            Essay.band_score >= 7.0
        ).order_by(func.random()).limit(limit).all()
        
        return reference_essays
    
    def _create_evaluation_prompt(self, essay_title: str, essay_content: str, reference_essays):
        """Create prompt with examples for few-shot learning"""
        
        # Base prompt
        prompt = """You are an expert IELTS Writing examiner. Your task is to evaluate IELTS Writing Task 2 essays according to the official IELTS marking criteria.

The IELTS Writing Task 2 is marked on four criteria:
1. Task Achievement (0-9): How well the essay addresses all parts of the task with a fully developed position and supporting ideas.
2. Coherence and Cohesion (0-9): How well the essay is organized, with clear progression, appropriate paragraphing, and effective use of cohesive devices.
3. Lexical Resource (0-9): The range, accuracy, and appropriateness of vocabulary use.
4. Grammatical Range and Accuracy (0-9): The range and accuracy of grammar structures.

I'll provide some examples of high-scoring essays (bands 7-9) for your reference, followed by the essay to evaluate.

"""
        
        # Add reference essays
        prompt += "--- REFERENCE ESSAYS (HIGH-SCORING EXAMPLES) ---\n\n"
        for i, ref_essay in enumerate(reference_essays):
            prompt += f"REFERENCE ESSAY {i+1} (Band score: {ref_essay.band_score}):\n"
            prompt += f"Title: {ref_essay.title}\n"
            prompt += f"Prompt: {ref_essay.prompt}\n"
            prompt += f"Essay: {ref_essay.content}\n\n"
        
        # Add the essay to evaluate
        prompt += "--- ESSAY TO EVALUATE ---\n\n"
        prompt += f"Title: {essay_title}\n"
        prompt += f"Essay: {essay_content}\n\n"
        
        # Add output instructions
        prompt += """Please evaluate this essay and provide scores for each criterion. The overall score should be the average of the four criteria, rounded to the nearest 0.5.

Format your response exactly as follows:
Task Achievement: [score]
Coherence and Cohesion: [score]
Lexical Resource: [score]
Grammatical Range and Accuracy: [score]
Overall Score: [score]
Feedback: [detailed feedback with specific examples from the essay, mentioning strengths and areas for improvement]"""
        
        return prompt
    
    async def _generate_evaluation(self, prompt):
        """Send prompt to Gemini API and get response"""
        response = await self.model.generate_content_async(prompt)
        return response.text
    
    def _parse_evaluation_response(self, response_text):
        """Parse the response to extract scores and feedback"""
        try:
            lines = response_text.strip().split('\n')
            scores = {}
            feedback = ""
            
            in_feedback = False
            
            for line in lines:
                if "Task Achievement:" in line:
                    scores["task_achievement"] = float(line.split(":")[1].strip())
                elif "Coherence and Cohesion:" in line:
                    scores["coherence_cohesion"] = float(line.split(":")[1].strip())
                elif "Lexical Resource:" in line:
                    scores["lexical_resource"] = float(line.split(":")[1].strip())
                elif "Grammatical Range:" in line or "Grammatical Range and Accuracy:" in line:
                    scores["grammatical_range"] = float(line.split(":")[1].strip())
                elif "Overall Score:" in line:
                    scores["overall_score"] = float(line.split(":")[1].strip())
                elif "Feedback:" in line:
                    in_feedback = True
                    feedback = line.replace("Feedback:", "").strip()
                elif in_feedback:
                    feedback += " " + line.strip()
            
            scores["feedback"] = feedback
            
            return scores
        except Exception as e:
            print(f"Error parsing model response: {e}")
            print(f"Raw response: {response_text}")
            raise ValueError("Failed to parse evaluation results")