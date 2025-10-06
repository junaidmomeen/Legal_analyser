import os
import requests
import logging
from openai import OpenAI
from typing import List, Optional
from models.analysis_models import AnalysisResult, KeyClause
import json
import asyncio

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """Service for AI-powered legal document analysis using OpenRouter with retry and fallback logic"""

    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            logger.critical("CRITICAL: OPENROUTER_API_KEY not found. The application cannot start without it.")
            exit("OPENROUTER_API_KEY not set.")
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "Legal Analyser"
            }
        )
        self.model = "openai/gpt-4o-mini"
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delay = int(os.getenv("RETRY_DELAY", "2"))  # seconds
        self.fallback_chunk_size = 8000  # characters for fallback mode

    def save_debug_output(self, raw_output: str, filename: str = None, status: str = "success") -> None:
        """Save raw AI output for debugging purposes"""
        # This function is no longer needed as debug_outputs directory is removed
        pass

    def clean_json_response(self, raw_text: str) -> str:
        """Clean and extract JSON from AI response"""
        if not raw_text or not raw_text.strip():
            raise ValueError("Empty response from AI")
        
        # Remove markdown code blocks
        if "```json" in raw_text:
            start = raw_text.find("```json") + 7
            end = raw_text.find("```", start)
            if end != -1:
                raw_text = raw_text[start:end].strip()
        elif "```" in raw_text:
            # Handle cases where it's just ``` without json
            start = raw_text.find("```") + 3
            end = raw_text.find("```", start)
            if end != -1:
                raw_text = raw_text[start:end].strip()
        
        # Find the JSON object boundaries
        json_start = raw_text.find('{')
        json_end = raw_text.rfind('}') + 1
        
        if json_start != -1 and json_end != 0:
            raw_text = raw_text[json_start:json_end]
        
        return raw_text.strip()

    def create_analysis_prompt(self, text: str, is_fallback: bool = False) -> str:
        """Create the analysis prompt with optional fallback mode"""
        base_prompt = """
        You are an AI trained to analyze **legal documents**.
        Read the following text and return a structured JSON object with:

        {
          "summary": "A detailed, easy-to-understand summary of the document's purpose, key obligations, and potential risks. Write in simple terms for a non-lawyer to understand.",
          "key_clauses": [
            {
              "type": "Clause type (e.g., Payment Terms, Termination, Confidentiality)",
              "content": "Full text of the clause (first 200 chars if too long)",
              "importance": "high | medium | low",
              "classification": "Contractual | Compliance | Financial | Termination | Confidentiality | Miscellaneous",
              "risk_score": "A score from 1 to 10, where 10 is the highest risk",
              "page": "Estimated page number (if possible, else null)"
            }
          ],
          "document_type": "Type of document (contract/agreement/policy/etc)",
          "confidence": "Number between 0.5 and 0.98"
        }

        IMPORTANT: 
        - ONLY return valid JSON
        - Do not include explanations or markdown
        - If text is truncated, focus on the most important clauses
        - Ensure all JSON keys are present
        """
        
        if is_fallback:
            base_prompt += "\n\nNOTE: This is a partial document analysis due to size limits."
        
        return base_prompt + f"\n\nDocument text:\n{text}"

    def create_fallback_result(self, document_type: str, error_msg: str) -> AnalysisResult:
        """Create a fallback result when AI analysis completely fails"""
        return AnalysisResult(
            summary=f"Analysis failed: {error_msg}. Please try uploading a smaller document or contact support.",
            key_clauses=[
                KeyClause(
                    type="Error",
                    content="Could not analyze document due to processing error.",
                    importance="high",
                    classification="Miscellaneous",
                    risk_score=10.0,
                    page=None,
                    confidence=0.0
                )
            ],
            document_type=document_type or "Unknown Document",
            confidence=0.0
        )

    def analyze_with_openrouter(self, prompt: str, attempt: int = 1) -> str:
        """Make API call to OpenRouter with error handling"""
        try:
            logger.info(f"Making OpenRouter API call (attempt {attempt}/{self.max_retries})")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )
            
            if not response or not response.choices:
                raise ValueError("Empty response from OpenRouter")
            
            return response.choices[0].message.content.strip()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenRouter API request failed: {e}")
            raise Exception("API request failed. Please try again later.")
        
        except Exception as e:
            logger.error(f"OpenRouter API error (attempt {attempt}): {str(e)}")
            raise

    async def analyze_document(
        self,
        text: str,
        document_type: str,
        filename: str
    ) -> AnalysisResult:
        """
        Analyze the document using OpenRouter AI with retry and fallback logic.
        Extracts summary + key clauses into structured format.
        """
        logger.info(f"Starting analysis for document: {filename} ({len(text)} chars)")
        
        # Truncate text if too long for primary analysis
        analysis_text = text[:12000] if len(text) > 12000 else text
        
        for attempt in range(1, self.max_retries + 1):
            try:
                prompt = self.create_analysis_prompt(analysis_text)
                raw_output = self.analyze_with_openrouter(prompt, attempt)
                
                # Save successful output for debugging
                # self.save_debug_output(raw_output, f"success_{filename}_{attempt}.json", "success")
                
                # Clean and parse JSON
                clean_json = self.clean_json_response(raw_output)
                data = json.loads(clean_json)
                
                # Validate required fields
                required_fields = ["summary", "key_clauses", "document_type", "confidence"]
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    raise ValueError(f"Missing required fields: {missing_fields}")
                
                # Transform into AnalysisResult
                key_clauses: List[KeyClause] = []
                for clause in data.get("key_clauses", []):
                    key_clauses.append(
                        KeyClause(
                            type=clause.get("type", "Unknown"),
                            content=clause.get("content", "")[:500],  # Limit content length
                            importance=clause.get("importance", "low"),
                            classification=clause.get("classification", "Miscellaneous"),
                            risk_score=float(clause.get("risk_score", 0.0)),
                            page=clause.get("page"),
                            confidence=0.9
                        )
                    )
                
                result = AnalysisResult(
                    summary=data.get("summary", "No summary provided."),
                    key_clauses=key_clauses,
                    document_type=data.get("document_type", document_type or "Legal Document"),
                    confidence=min(float(data.get("confidence", 0.8)), 0.98)
                )
                
                logger.info(f"Analysis completed successfully for {filename} (attempt {attempt})")
                return result
                
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parsing failed (attempt {attempt}): {e}")
                # Save failed output for debugging
                # if 'raw_output' in locals():
                #     self.save_debug_output(raw_output, f"json_error_{filename}_{attempt}.json", "json_error")
                
                if attempt == self.max_retries:
                    # Try fallback with smaller chunks
                    logger.info("Attempting fallback analysis with smaller chunks...")
                    return self.fallback_analysis(text, document_type, filename)
                else:
                    await asyncio.sleep(self.retry_delay)
                    continue
            
            except Exception as e:
                logger.error(f"Analysis attempt {attempt} failed: {str(e)}")
                # Save failed output for debugging
                # if 'raw_output' in locals():
                #     self.save_debug_output(raw_output, f"error_{filename}_{attempt}.json", "error")
                
                if attempt == self.max_retries:
                    # Final fallback
                    return self.create_fallback_result(document_type, str(e))
                else:
                    await asyncio.sleep(self.retry_delay * attempt)  # Exponential backoff
        
        # Should not reach here, but just in case
        return self.create_fallback_result(document_type, "Maximum retries exceeded")

    def fallback_analysis(
        self, 
        text: str, 
        document_type: str, 
        filename: str
    ) -> AnalysisResult:
        """Fallback analysis with smaller chunks when main analysis fails"""
        try:
            logger.info(f"Starting fallback analysis for {filename}")
            
            # Use smaller chunk for fallback
            fallback_text = text[:self.fallback_chunk_size]
            prompt = self.create_analysis_prompt(fallback_text, is_fallback=True)
            
            raw_output = self.analyze_with_openrouter(prompt)
            # self.save_debug_output(raw_output, f"fallback_{filename}.json", "fallback")
            
            # Simple parsing for fallback
            try:
                clean_json = self.clean_json_response(raw_output)
                data = json.loads(clean_json)
            except:
                # Ultra-fallback: create minimal result
                return AnalysisResult(
                    summary="Document processed with limited analysis due to processing constraints.",
                    key_clauses=[
                        KeyClause(
                            type="General Content",
                            content=fallback_text[:200] + "..." if len(fallback_text) > 200 else fallback_text,
                            importance="medium",
                            classification="Miscellaneous",
                            risk_score=5.0,
                            page=1,
                            confidence=0.5
                        )
                    ],
                    document_type=document_type or "Legal Document",
                    confidence=0.5
                )
            
            # Build result from fallback data
            key_clauses = []
            for clause in data.get("key_clauses", []):
                key_clauses.append(
                    KeyClause(
                        type=clause.get("type", "Unknown"),
                        content=clause.get("content", "")[:200],
                        importance=clause.get("importance", "low"),
                        classification=clause.get("classification", "Miscellaneous"),
                        risk_score=float(clause.get("risk_score", 0.0)),
                        page=clause.get("page"),
                        confidence=0.6  # Lower confidence for fallback
                    )
                )
            
            result = AnalysisResult(
                summary=f"[Partial Analysis] {data.get('summary', 'Limited analysis completed.')}",
                key_clauses=key_clauses,
                document_type=data.get("document_type", document_type),
                confidence=min(float(data.get("confidence", 0.6)), 0.7)  # Cap fallback confidence
            )
            
            logger.info(f"Fallback analysis completed for {filename}")
            return result
            
        except Exception as e:
            logger.error(f"Fallback analysis also failed: {str(e)}")
            return self.create_fallback_result(document_type, f"Fallback failed: {str(e)}")
