from typing import Optional, List, Dict, Any
import os
import httpx
from fastapi import HTTPException
import re

class EssayEvaluator:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with OpenRouter API key for accessing DeepSeek-R1 model"""
        self.api_key = "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"
        if not self.api_key:
            raise ValueError("OpenRouter API key not found. Please provide an API key or set OPENROUTER_API_KEY environment variable.")
        
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "deepseek/deepseek-r1"  # Using DeepSeek-R1 model from OpenRouter
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": os.environ.get("HTTP_REFERER", "https://your-app-domain.com"),  # Required by OpenRouter
            "X-Title": os.environ.get("X_TITLE", "IELTS Essay Evaluator")  # Optional but recommended
        }
    
    async def evaluate_essay(
        self,
        essay_content: str,
        essay_prompt: str,
        similar_essays: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate an IELTS essay using the OpenRouter API with DeepSeek-R1 model
        """
        try:
            # Create evaluation prompt with RAG context
            prompt = self._create_evaluation_prompt(essay_prompt, essay_content, similar_essays)
            
            # Generate evaluation using OpenRouter
            evaluation_text = await self._generate_evaluation(prompt)
            
            if not evaluation_text or not evaluation_text.strip():
                raise ValueError("Empty response from model")
            
            # Parse evaluation response
            evaluation = self._parse_evaluation_response(evaluation_text)
            
            return evaluation
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Essay evaluation failed: {str(e)}"
            )
    
    def _create_evaluation_prompt(
        self,
        essay_prompt: str,
        essay_content: str,
        similar_essays: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Create prompt with RAG context for evaluation"""
        base_prompt = """You are an expert IELTS Writing examiner. Your task is to evaluate IELTS Writing Task 2 essays according to the official IELTS marking criteria.

The IELTS Writing Task 2 is marked on four criteria:
1. Task Achievement (0-9): How well the essay addresses all parts of the task with a fully developed position and supporting ideas.
2. Coherence and Cohesion (0-9): How well the essay is organized, with clear progression, appropriate paragraphing, and effective use of cohesive devices.
3. Lexical Resource (0-9): The range, accuracy, and appropriateness of vocabulary use.
4. Grammatical Range and Accuracy (0-9): The range and accuracy of grammar structures.

IMPORTANT INSTRUCTIONS:
1. You MUST provide scores for ALL criteria (Task Achievement, Coherence and Cohesion, Lexical Resource, Grammatical Range and Accuracy, and Overall Score)
2. Each score MUST be a number between 0 and 9, with one decimal place (e.g., 6.5, 7.0)
3. The Overall Score should be the average of the four criteria scores
4. Format your response EXACTLY as shown below, with no additional text before or after the scores
5. After the scores, provide detailed feedback in the format shown

Essay Prompt:
{prompt}

Essay to Evaluate:
{content}
"""
        
        # Add similar essays if available
        if similar_essays and len(similar_essays) > 0:
            base_prompt += "\n\nHere are some similar essays for reference:\n"
            for i, essay in enumerate(similar_essays, 1):
                base_prompt += f"\nReference Essay {i} (Similarity: {essay['distance']:.2f}):\n{essay['content']}\n"
        
        base_prompt += """
SCORES (format exactly as shown):
Task Achievement: [score]
Coherence and Cohesion: [score]
Lexical Resource: [score]
Grammatical Range and Accuracy: [score]
Overall Score: [score]

FEEDBACK:
[Provide detailed feedback with specific examples from the essay, mentioning strengths and areas for improvement]

IMPORTANT:
- Your response MUST include the 'FEEDBACK:' section exactly as shown above, even if you have already provided feedback elsewhere.
- Do NOT add any text before the SCORES section or after the FEEDBACK section.
- If you do not follow this format, your response will be considered invalid.
"""
        
        return base_prompt.format(prompt=essay_prompt, content=essay_content)
    
    async def _generate_evaluation(self, prompt: str) -> str:
        """Send prompt to OpenRouter API and get response"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are an expert IELTS Writing examiner."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,  # Low temperature for more consistent evaluation
                "max_tokens": 1000
            }
            
            response = await client.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    def _parse_evaluation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the response to extract scores and feedback"""
        try:
            if not response_text or not response_text.strip():
                raise ValueError("Empty response from model")

            # Split into sections
            sections = response_text.split("FEEDBACK:")
            if len(sections) != 2:
                raise ValueError("Response missing FEEDBACK section")

            scores_section = sections[0].strip()
            feedback_section = sections[1].strip()

            # Parse scores
            scores = {}
            score_pattern = r"([A-Za-z\s&]+):\s*([0-9]\.?[0-9]?)"
            
            for line in scores_section.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                match = re.search(score_pattern, line, re.IGNORECASE)
                if match:
                    key = match.group(1).strip().lower()
                    value = float(match.group(2))
                    
                    # Map keys to our schema
                    if "task achievement" in key:
                        scores["task_achievement"] = value
                    elif "coherence" in key and "cohesion" in key:
                        scores["coherence_cohesion"] = value
                    elif "lexical" in key:
                        scores["lexical_resource"] = value
                    elif "grammatical" in key:
                        scores["grammatical_range"] = value
                    elif "overall" in key:
                        scores["overall_score"] = value

            # Validate all required scores are present
            required_scores = [
                "task_achievement",
                "coherence_cohesion",
                "lexical_resource",
                "grammatical_range",
                "overall_score"
            ]
            
            missing_scores = [score for score in required_scores if score not in scores]
            if missing_scores:
                raise ValueError(f"Missing required scores: {', '.join(missing_scores)}")

            # Validate score ranges
            for score_name, score_value in scores.items():
                if not (0 <= score_value <= 9):
                    raise ValueError(f"Score out of range (0-9) for {score_name}: {score_value}")

            # Add feedback
            scores["feedback"] = feedback_section.strip()
            if not scores["feedback"]:
                raise ValueError("Empty feedback section")

            return scores

        except Exception as e:
            print(f"Error parsing model response: {e}")
            print(f"Raw response: {response_text}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse evaluation results: {str(e)}"
            )