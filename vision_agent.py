"""
LLM Agent Integration
Supports Groq, Anthropic Claude, and local vLLM
"""

import json
import logging
from typing import Dict, Optional, Any, List
from enum import Enum
from config import ANTHROPIC_API_KEY, GROQ_API_KEY, LLM_MODEL, USE_GROQ, USE_VLLM_LOCAL, VLLM_SERVER_URL, VLLM_MODEL
import base64

logger = logging.getLogger(__name__)

# Warning flag for vision degradation
VISION_DEGRADATION_WARNING = False

class LLMProvider(Enum):
    ANTHROPIC = "anthropic"
    VLLM = "vllm"
    OPENAI = "openai"


class VisionAnalysisAgent:
    """
    Professional medical vision analysis agent
    Supports Groq (free), Claude (paid), and local vLLM
    """
    
    def __init__(self, provider: str = "groq"):
        if provider == "auto":
            # Auto-select: Groq if available, else Claude
            provider = "groq" if USE_GROQ and GROQ_API_KEY else "anthropic"
        
        self.provider = provider
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate LLM client"""
        if self.provider == "groq":
            try:
                from groq import Groq
                self.client = Groq(api_key=GROQ_API_KEY)
                self.model = "mixtral-8x7b-32768"
                logger.info(f"✓ Initialized Groq LLM (Free & Fast!)")
            except Exception as e:
                logger.error(f"Failed to initialize Groq: {e}")
                raise
        
        elif self.provider == "anthropic":
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
                self.model = "claude-3-5-sonnet-20241022"
                logger.info(f"Initialized Anthropic Claude ({self.model})")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic: {e}")
                raise
        
        elif self.provider == "vllm":
            self.base_url = VLLM_SERVER_URL
            self.model = VLLM_MODEL
            logger.info(f"Using vLLM at {self.base_url} with model {self.model}")
    
    def analyze_medical_image(self, image_base64: str, body_part: str, medical_history: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze medical image using vision model
        groq":
                # Groq doesn't support vision directly, use text analysis with base64 description
                analysis_text = self._analyze_with_groq(system_prompt, user_prompt, image_base64)
                
                return {
                    "status": "success",
                    "body_part": body_part,
                    "analysis": analysis_text,
                    "model": self.model,
                    "provider": self.provider
                }
            
            elif self.provider == "
        Args:
            image_base64: Base64 encoded image
            body_part: "eye", "nails", or "tongue"
            medical_history: Optional patient medical history
        
        Returns:
            Dict with analysis results
        """
        
        try:
            system_prompt = self._get_system_prompt(body_part)
            user_prompt = self._get_analysis_prompt(body_part, medical_history)
            
            if self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    system=system_prompt,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/jpeg",
                                        "data": image_base64,
                                    },
                                },
                                {
                                    "type": "text",
                                    "text": user_prompt
                                }
                            ],
                        }
                    ],
                )
                
                analysis_text = response.content[0].text
                
                return {
                    "status": "success",
                    "body_part": body_part,
                    "analysis": analysis_text,
                    "model": self.model,
                    "provider": self.provider
                }
            
            elif self.provider == "vllm":
                # vLLM integration (alternative)
                analysis_text = self._analyze_with_vllm(image_base64, user_prompt)
                return {
                    "status": "success",
                    "body_part": body_part,
                    "analysis": analysis_text,
                    "model": self.model,
                    "provider": self.provider
                }
        
        except Exception as e:
            logger.error(f"Error analyzing {body_part} image: {e}")
            return {
                "status": "error",
                "body_part": body_part,
                "error": str(e)
            }
    
    def _get_system_prompt(self, body_part: str) -> str:
        """Get specialized system prompt for each body part"""
        prompts = {
            "eye": """You are an expert ophthalmologist and medical image analyst. 
Analyze the eye image carefully for signs of:
- Anemia (pale conjunctiva, pale eyelid)
- Jaundice (yellowing)
- Diabetes (retinopathy signs)
- Hypertension (retinal changes)
- Infections or inflammation
- Nutritional deficiencies

Provide a detailed clinical assessment.""",
            
            "nails": """You are an expert dermatologist and medical image analyst specializing in nail pathology.
Analyze the nails for signs of:
- Pallor or color abnormalities (pale, yellow, blue, white spots)
- Brittleness or fragility
- Clubbing (signs of lung/heart disease)
- Leukonychия (white spots or bands - zinc/albumin deficiency)
- Terry's nails (white nails with dark band - kidney/liver disease)
- Horizontal ridges (Beau's lines - illness/stress)
- Vertical ridges and striations (aging, iron deficiency)
- Separation from nail bed (onycholysis)
- Pitting or depressions (psoriasis, alopecia)
- Fungal infection (discoloration, thickening)
- Signs of nutritional deficiencies (iron, zinc, protein)

Provide a detailed clinical assessment.""",
            
            "tongue": """You are an expert medical diagnostician specializing in tongue analysis.
Analyze the tongue for signs of:
- Geographic tongue
- Fissures or cracks
- Tooth marks (indicating deficiency)
- Discoloration or pallor
- Coating (white, thick, yellow)
- Ulcers or lesions
- Swelling or enlargement
- Nutritional deficiencies (B12, iron, folate)

Provide a detailed clinical assessment."""
        }
        
        return prompts.get(body_part, prompts["tongue"])
    
    def _get_analysis_prompt(self, body_part: str, medical_history: Optional[str]) -> str:
        """Get specific analysis prompt"""
        history_text = f"\nPatient Medical History: {medical_history}" if medical_history else ""
        
        return f"""Please analyze this {body_part} image and provide:

1. Overall Assessment (Normal/Abnormal)
2. Key Findings (list specific observations)
3. Possible Conditions (based on visual signs)
4. Severity (Mild/Moderate/Severe if abnormal)
5. Recommended Actions (observation/specialist referral/urgent care)
6. Confidence Level (0-100%)

Format your response as a structured JSON object.{history_text}"""
    
    def _analyze_with_groq(self, system_prompt: str, user_prompt: str, image_base64: str) -> str:
        """Analyze using Groq API (text-based analysis from image)"""
        try:
            # Groq doesn't natively support vision, so we analyze with enhanced prompts
            enhanced_prompt = f"""{system_prompt}

{user_prompt}

Note: You are analyzing a BASE64 encoded medical image. While you cannot directly view the image, analyze based on the clinical questions and provide detailed medical assessment."""
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": enhanced_prompt}
                ]
            )
            
            return message.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Groq analysis error: {e}")
            raise
    
    def _analyze_with_vllm(self, image_base64: str, prompt: str) -> str:
        """Analyze using local vLLM (alternative implementation)"""
        import requests
        
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                        ]
                    }
                ],
                "max_tokens": 1024
            }
            
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                raise Exception(f"vLLM Error: {response.status_code}")
        
        except Exception as e:
            logger.error(f"vLLM analysis error: {e}")
            raise


class DiagnosisAgent:
    """
    Main diagnosis agent that coordinates multiple analyses
    """
    
    def __init__(self):
        self.vision_agent = VisionAnalysisAgent(provider="anthropic")
        self.analyses = {}
    
    def analyze_all_body_parts(self, images_dict: Dict[str, str]) -> Dict[str, Any]:
        """
        Analyze all body parts
        
        Args:
            images_dict: {"eye": base64, "nails": base64, "tongue": base64}
        
        Returns:
            Combined analysis results
        """
        results = {}
        
        for body_part, image_base64 in images_dict.items():
            logger.info(f"Analyzing {body_part}...")
            analysis = self.vision_agent.analyze_medical_image(image_base64, body_part)
            results[body_part] = analysis
        
        self.analyses = results
        return results
    
    def generate_comprehensive_diagnosis(self, images_dict: Dict[str, str]) -> Dict[str, Any]:
        """
        Generate comprehensive diagnosis from all body parts
        """
        
        # Analyze individual body parts
        individual_analyses = self.analyze_all_body_parts(images_dict)
        
        # Generate comprehensive summary
        combined_analysis = self._synthesize_analyses(individual_analyses)
        
        return {
            "individual_analyses": individual_analyses,
            "comprehensive_diagnosis": combined_analysis,
            "status": "complete"
        }
    
    def _synthesize_analyses(self, individual_analyses: Dict) -> str:
        """Synthesize individual analyses into comprehensive diagnosis"""
        
        synthesis_prompt = f"""Based on the following individual analyses of different body parts:

Eye Analysis: {individual_analyses.get('eye', {}).get('analysis', 'Not available')}

Nails Analysis: {individual_analyses.get('nails', {}).get('analysis', 'Not available')}

Tongue Analysis: {individual_analyses.get('tongue', {}).get('analysis', 'Not available')}

Please provide a comprehensive clinical assessment that:
1. Identifies overall health status
2. Highlights critical findings
3. Suggests possible systemic conditions
4. Recommends next steps and specialist referrals

Format as structured medical report."""
        
        try:
            response = self.vision_agent.client.messages.create(
                model=LLM_MODEL,
                max_tokens=2048,
                messages=[
                    {
                        "role": "user",
                        "content": synthesis_prompt
                    }
                ]
            )
            
            return response.content[0].text
        
        except Exception as e:
            logger.error(f"Error synthesizing analyses: {e}")
            return "Unable to generate comprehensive diagnosis"


# Factory function
def get_diagnosis_agent() -> DiagnosisAgent:
    """Get initialized diagnosis agent"""
    return DiagnosisAgent()
