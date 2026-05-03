"""
Agent 1: Medical Report & Diet Plan Generator
Generates detailed medical reports and personalized diet plans based on diagnosis
"""

import json
import logging
from typing import Dict, Optional, Any, List
from datetime import datetime
from config import LLM_MODEL, ANTHROPIC_API_KEY, GROQ_API_KEY, USE_GROQ, DIET_PLAN_CATEGORIES

logger = logging.getLogger(__name__)

try:
    import anthropic
except ImportError:
    anthropic = None


class ReportGenerator:
    """Generate professional medical reports"""
    
    def __init__(self):
        if USE_GROQ:
            try:
                from groq import Groq
                self.client = Groq(api_key=GROQ_API_KEY)
                self.model = "mixtral-8x7b-32768"
                logger.info("✓ Report Generator using Groq (Free)")
            except Exception as e:
                logger.error(f"Failed to init Groq for reports: {e}")
                self.client = None
        else:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
                self.model = LLM_MODEL
                logger.info("Report Generator using Anthropic Claude")
            except Exception as e:
                logger.error(f"Failed to init Anthropic for reports: {e}")
                self.client = None
    
    def generate_medical_report(
        self,
        diagnosis: str,
        analyses: Dict[str, str],
        confidence: float = 0.85,
        patient_info: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive medical report
        
        Args:
            diagnosis: Main diagnosis summary
            analyses: Individual body part analyses
            confidence: Confidence level of diagnosis
            patient_info: Optional patient information (age, sex, allergies, etc.)
        
        Returns:
            Structured medical report
        """
        
        patient_context = ""
        if patient_info:
            patient_context = f"""
Patient Information:
- Age: {patient_info.get('age', 'Unknown')}
- Sex: {patient_info.get('sex', 'Unknown')}
- Medical History: {patient_info.get('history', 'None')}
"""
        
        report_prompt = f"""Generate a professional medical report with EXACTLY the following structure:

{patient_context}

PRIMARY DIAGNOSIS: {diagnosis}

INDIVIDUAL ASSESSMENTS:
- Eye: {analyses.get('eye', 'Not available')}
- Nails: {analyses.get('nails', 'Not available')}  
- Tongue: {analyses.get('tongue', 'Not available')}

Report Structure (FILL IN EACH SECTION):

# MEDICAL REPORT

**Report Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Clinical Summary
Write 2-3 sentences summarizing the key medical findings from the diagnosis and assessments.

## Detailed Findings
Provide a comprehensive assessment of all observations from eye, nails, and tongue analysis.

## Assessment
- **Overall Status:** State if patient is Healthy, At Risk, or Abnormal
- **Severity Level:** None, Mild, Moderate, or Severe
- **Confidence Score:** {confidence * 100:.0f}%

## Key Findings
- List key finding 1 from analysis
- List key finding 2 from analysis
- List key finding 3 from analysis

## Recommendations
- Recommendation 1 based on diagnosis
- Recommendation 2 based on diagnosis
- Recommendation 3 based on diagnosis

## Follow-up Required
Specify if specialist consultation is needed and which specialty.

## Clinical Notes
Any additional clinical observations and professional notes.
"""
        
        try:
            if not self.client:
                logger.warning("No LLM client available, using auto-generated report")
                return self._auto_generate_report(diagnosis, analyses, confidence, patient_info)
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                messages=[
                    {
                        "role": "user",
                        "content": report_prompt
                    }
                ]
            )
            
            # Handle both Anthropic and Groq response formats
            if hasattr(response, 'content'):  # Anthropic
                report_text = response.content[0].text
            elif hasattr(response, 'choices'):  # Groq
                report_text = response.choices[0].message.content
            else:
                report_text = str(response)
            
            logger.info("✅ Medical report generated successfully")
            
            return {
                "status": "success",
                "report": report_text,
                "generated_at": datetime.now().isoformat(),
                "confidence": confidence
            }
        
        except Exception as e:
            logger.warning(f"LLM report generation failed: {e}, using fallback")
            return self._auto_generate_report(diagnosis, analyses, confidence, patient_info)
    
    def _auto_generate_report(self, diagnosis: str, analyses: Dict[str, str], 
                             confidence: float, patient_info: Optional[Dict]) -> Dict[str, Any]:
        """Fallback: Auto-generate professional report without LLM"""
        
        report = f"""# MEDICAL REPORT

**Report Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Clinical Summary
The patient has been diagnosed with {diagnosis}. Based on comprehensive multi-modal analysis including eye, nails, and tongue assessments, clinical findings show variations consistent with the primary diagnosis. Further evaluation and specialist consultation are recommended for definitive treatment planning.

## Detailed Findings

### Eye Analysis
{analyses.get('eye', 'Visual inspection completed. No abnormalities noted in preliminary screening.')}

### Nails Assessment
{analyses.get('nails', 'Nail bed examination completed. Findings consistent with general health status assessment.')}

### Tongue Examination
{analyses.get('tongue', 'Oral mucosa and lingual findings examined. Results recorded for clinical correlation.')}

## Assessment
- **Overall Status:** At Risk
- **Severity Level:** Moderate
- **Confidence Score:** {confidence * 100:.0f}%

## Key Findings
- Primary diagnosis: {diagnosis}
- Multi-modal imaging analysis completed
- Clinical correlation needed with patient history

## Recommendations
- Consultant evaluation by appropriate medical specialist
- Follow-up laboratory tests as indicated
- Lifestyle modifications based on diagnosis
- Regular monitoring of clinical status

## Follow-up Required
Yes - Specialist consultation recommended. Specific specialty will be determined based on diagnosis category.

## Clinical Notes
This report is generated by AI Medical Diagnostic System. All findings should be reviewed and confirmed by licensed medical professionals before treatment decisions. Patient education and preventive care guidance recommended.
"""
        
        logger.info("✅ Auto-generated fallback report created")
        return {
            "status": "success",
            "report": report,
            "generated_at": datetime.now().isoformat(),
            "confidence": confidence,
            "auto_generated": True
        }
    
    def save_report(self, report: Dict, filename: Optional[str] = None) -> str:
        """Save report to file"""
        try:
            if filename is None:
                filename = f"reports/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            
            with open(filename, 'w') as f:
                f.write(report.get('report', ''))
            
            logger.info(f"Report saved to {filename}")
            return filename
        
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            return ""


class DietPlanGenerator:
    """Generate personalized diet plans based on diagnosis"""
    
    def __init__(self):
        if USE_GROQ:
            try:
                from groq import Groq
                self.client = Groq(api_key=GROQ_API_KEY)
                self.model = "mixtral-8x7b-32768"
                logger.info("✓ Diet Generator using Groq (Free)")
            except Exception as e:
                logger.error(f"Failed to init Groq for diet: {e}")
                self.client = None
        else:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
                self.model = LLM_MODEL
                logger.info("Diet Generator using Anthropic Claude")
            except Exception as e:
                logger.error(f"Failed to init Anthropic for diet: {e}")
                self.client = None
    
    def generate_diet_plan(
        self,
        diagnosis: str,
        condition_severity: str = "moderate",
        duration_days: int = 30,
        dietary_restrictions: Optional[List[str]] = None,
        patient_info: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate personalized diet plan
        
        Args:
            diagnosis: Medical diagnosis
            condition_severity: mild, moderate, or severe
            duration_days: Duration of diet plan
            dietary_restrictions: Foods to avoid
            patient_info: Patient demographics and preferences
        
        Returns:
            Detailed diet plan
        """
        
        restrictions_text = ""
        if dietary_restrictions:
            restrictions_text = f"Dietary Restrictions: {', '.join(dietary_restrictions)}\n"
        
        patient_context = ""
        if patient_info:
            patient_context = f"""
Patient Profile:
- Age: {patient_info.get('age', 'Adult')}
- Preferences: {patient_info.get('dietary_preferences', 'No specific preference')}
- Allergies: {patient_info.get('allergies', 'None')}
- Budget: {patient_info.get('budget', 'Standard')}
"""
        
        diet_prompt = f"""Generate a comprehensive {duration_days}-day personalized diet plan for a patient with the following condition:

DIAGNOSIS: {diagnosis}
SEVERITY: {condition_severity}
{restrictions_text}{patient_context}

Create a detailed diet plan with:

# PERSONALIZED DIET PLAN
**Duration:** {duration_days} days
**Severity Level:** {condition_severity.capitalize()}
**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}

## Executive Summary
[Brief overview of the diet plan and its objectives]

## Nutritional Goals
- Micronutrient Focus: [Key vitamins/minerals to include]
- Macronutrient Balance: [Protein/Fat/Carb recommendations]
- Daily Caloric Target: [Estimated calories]

## Foods to Prioritize
### Vitamins & Minerals
- Food 1 (benefits)
- Food 2 (benefits)
- Food 3 (benefits)

### Proteins
- Food 1 (benefits)
- Food 2 (benefits)

### Carbohydrates
- Food 1 (benefits)
- Food 2 (benefits)

### Healthy Fats
- Food 1 (benefits)
- Food 2 (benefits)

### Hydration
- Recommended: [Amount and type]

## Foods to Avoid
- Food 1 (reason)
- Food 2 (reason)
- Food 3 (reason)

## Weekly Meal Suggestions

### Week 1
**Monday:** Breakfast | Lunch | Dinner | Snacks
[Specific meals with recipes]

**Tuesday-Sunday:** [Similar structure]

## Recipes
### Recipe 1: [Name]
**Ingredients:**
[Ingredient list]

**Instructions:**
[Step-by-step]

**Nutritional Info:**
[Calories, protein, etc.]

### Recipe 2, 3, etc...

## Supplements (if needed)
- Supplement 1: [Dosage, timing, purpose]
- Supplement 2: [Dosage, timing, purpose]

## Lifestyle Tips
- Tip 1
- Tip 2
- Tip 3

## Progress Tracking
- Week 1: [Expected improvements]
- Week 2: [Expected improvements]
- Week 3-4: [Expected improvements]

## When to Adjust
- If experiencing: [symptoms] → [adjust this way]

## Important Notes
- Consult with healthcare provider before starting
- Individual results may vary
- Adjust portions based on appetite and activity level
"""
        
        try:
            if not self.client:
                logger.warning("No LLM client available, using auto-generated diet plan")
                return self._auto_generate_diet_plan(diagnosis, condition_severity, patient_info)
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                messages=[
                    {
                        "role": "user",
                        "content": diet_prompt
                    }
                ]
            )
            
            # Handle both Anthropic and Groq response formats
            if hasattr(response, 'content'):  # Anthropic
                diet_plan = response.content[0].text
            elif hasattr(response, 'choices'):  # Groq
                diet_plan = response.choices[0].message.content
            else:
                diet_plan = str(response)
            
            logger.info("✅ Diet plan generated successfully")
            
            return {
                "status": "success",
                "diet_plan": diet_plan,
                "generated_at": datetime.now().isoformat(),
                "duration": duration_days,
                "severity": condition_severity
            }
        
        except Exception as e:
            logger.warning(f"LLM diet plan generation failed: {e}, using fallback")
            return self._auto_generate_diet_plan(diagnosis, condition_severity, patient_info)
    
    def _auto_generate_diet_plan(self, diagnosis: str, condition_severity: str,
                                patient_info: Optional[Dict] = None) -> Dict[str, Any]:
        """Fallback: Auto-generate professional diet plan without LLM"""
        
        diet_plan = f"""# PERSONALIZED 30-DAY DIET PLAN

**Diagnosis:** {diagnosis}
**Severity Level:** {condition_severity.capitalize()}
**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}

## Dietary Guidelines
- Daily calorie target: 2000-2500 calories (adjust based on gender, age, activity level)
- Protein: 50-60g daily for tissue repair and muscle maintenance
- Fruits & Vegetables: 5+ servings daily for essential vitamins and minerals
- Healthy Fats: 25-30g daily from unsaturated sources
- Water: 8-10 glasses daily (more if exercise level is high)

## Recommended Foods

### Proteins (Daily: 50-60g)
- Lean chicken breast (skinless)
- Fresh fish (salmon, tuna, cod)
- Eggs (up to 6-7 per week)
- Legumes (lentils, chickpeas, black beans)
- Low-fat Greek yogurt

### Carbohydrates (Complex Priority)
- Brown rice (portion: ~1 cup cooked)
- Oatmeal and whole-grain cereals
- Sweet potatoes with skin
- Whole wheat bread and pasta
- Legumes (beans, peas)

### Vegetables (5+ servings daily)
- Leafy greens (spinach, kale, lettuce)
- Cruciferous vegetables (broccoli, cauliflower, cabbage)
- Root vegetables (carrots, beets, parsnips)
- Bell peppers (all colors)
- Tomatoes and cucumber

### Fruits (2-3 servings daily)
- Apples and berries (fresh)
- Bananas (high in potassium)
- Oranges and citrus
- Grapes and watermelon
- Avoid: high-sugar dried fruits

### Healthy Fats
- Olive oil (1-2 tbsp daily)
- Nuts (almonds, walnuts): 1 ounce serving
- Seeds (flax, chia, sunflower)
- Avocado (½ per day)
- Fish oils (omega-3 rich)

### Dairy
- Low-fat or fat-free milk
- Greek yogurt (plain, unsweetened)
- Low-fat cheese (1 ounce portions)
- Cottage cheese (low-fat)

## Foods to Avoid / Limit
- Deep-fried foods and fast food
- Sugary beverages (soft drinks, energy drinks, commercial juices)
- Processed meats (bacon, sausage, deli meats)
- Refined carbohydrates (white bread, pastries)
- Trans fats (margarine, certain baked goods)
- Excess sodium (>2300mg daily)
- Alcohol (minimize or avoid)
- High-sugar snacks and desserts
- Coffee/caffeine (limit to 1-2 cups daily)

## Sample Daily Meal Pattern

### Breakfast (7-8 AM)
- Whole grain: 1 cup oatmeal
- Protein: 1-2 eggs OR Greek yogurt
- Fruit: 1 medium apple or banana
- Beverage: Water, tea, or low-fat milk

### Mid-Morning Snack (10-11 AM)
- Option 1: Apple with 1 tbsp almond butter
- Option 2: Handful of unsalted almonds
- Option 3: Plain Greek yogurt (6 oz)

### Lunch (12-1 PM)
- Protein: 3-4 oz grilled chicken or fish
- Carbs: 1 cup brown rice or sweet potato
- Vegetables: 1-2 cups steamed/raw vegetables
- Oil: 1 tsp olive oil for cooking
- Beverage: Water or herbal tea

### Afternoon Snack (3-4 PM)
- Carrot sticks with hummus (2 tbsp)
- OR String cheese (1 oz)
- OR Fresh fruit

### Dinner (6-7 PM)
- Protein: 3-4 oz lean meat or fish
- Carbs: 1 cup brown rice or sweet potato
- Vegetables: 2 cups steamed broccoli, spinach, or mixed
- Oil: 1 tsp olive oil
- Beverage: Water or herbal tea

### Evening (8 PM)
- Optional: 1 cup low-fat milk or herbal tea

## Daily Hydration Schedule
- **6-8 AM:** 2 glasses of water upon waking
- **9-10 AM:** 1 glass with mid-morning snack
- **12 PM:** 2 glasses with lunch
- **2-3 PM:** 1 glass mid-afternoon
- **6-7 PM:** 2 glasses with dinner
- **8-9 PM:** 1 glass (stop hydration 2-3 hours before bed)

**Total Daily Water Intake:** 8-10 glasses (64-80 oz)

## Nutritional Targets Per Day
- **Calories:** 2200-2400 (adjust ±200 based on response)
- **Protein:** 15-20% of total calories (50-60g)
- **Carbohydrates:** 50-55% of total calories (275-325g)
- **Fats:** 25-30% of total calories (60-75g)

## Weekly Shopping Checklist

### Proteins
- Chicken breast: 2-3 lbs
- Fish (salmon or cod): 1-2 lbs
- Eggs: 1-2 dozen
- Legumes (dried or canned): 2-3 types

### Vegetables
- Leafy greens: Spinach, lettuce (2 packs)
- Cruciferous: Broccoli, cauliflower (2-3 heads)
- Root vegetables: Carrots, sweet potatoes (3-4 lbs)
- Tomatoes, peppers, onions (variety)

### Fruits
- Apples: 4-6 medium
- Bananas: 1 bunch
- Berries: 1 lb (fresh or frozen)
- Oranges or citrus: 6-8

### Grains & Starches
- Brown rice: 2-3 lbs
- Oatmeal (rolled oats): 2 lb container
- Whole wheat bread: 1 loaf
- Sweet potatoes: 4-6 medium

### Dairy
- Low-fat milk: 1 gallon
- Greek yogurt: 32 oz
- Low-fat cheese: 8 oz

### Pantry/Oils
- Extra virgin olive oil
- Almonds or mixed nuts (unsalted)
- Honey, spices, salt-free seasonings

## Meal Preparation Tips
- **Weekend Prep (Sunday):** Batch cook brown rice and proteins
- **Storage:** Use containers with lids; refrigerate for 3-4 days
- **Freezing:** Cooked portions freeze well for up to 3 months
- **Seasoning:** Use spices, lemon, garlic - minimize salt
- **Reheating:** Microwave or stovetop at medium heat
- **Portions:** Use standard plates as visual guides (½ plate vegetables, ¼ protein, ¼ carbs)

## Recipes to Try

### Simple Grilled Chicken with Steamed Vegetables
**Time:** 20 minutes | **Servings:** 2
- 2 chicken breasts (4 oz each)
- 2 cups mixed vegetables (broccoli, carrots, peppers)
- 1 tbsp olive oil, salt, pepper, garlic powder
**Method:** Season chicken, grill 6-8 min each side; steam vegetables separately

### Brown Rice & Bean Bowl
**Time:** 30 minutes | **Servings:** 3
- 1 cup dry brown rice
- 1 can black beans, drained
- 1 cup corn, 1 bell pepper (diced)
- 1 tbsp olive oil, cumin, lime juice
**Method:** Cook rice, sauté vegetables, combine with beans and seasonings

### Baked Salmon with Sweet Potato
**Time:** 25 minutes | **Servings:** 1
- 4 oz salmon fillet
- 1 medium sweet potato
- 1 cup broccoli, 1 tsp olive oil
**Method:** Bake salmon and sweet potato at 400°F for 20 min; steam broccoli

## Progress Tracking

### Week 1-2: Adjustment Phase
- Expect energy adjustment as body adapts
- Potential initial hunger - this normalizes in 3-4 days
- Take notes on energy, digestion, mood
- Maintain consistent meal times

### Week 2-3: Stabilization Phase
- Energy levels should improve significantly
- Sleep quality may improve
- Weight changes begin (varies individually)
- Continue meal consistency

### Week 3-4: Optimization Phase
- Full adaptation to new eating patterns
- Peak energy levels
- Measurable improvements in specific areas
- Ready for any plan adjustments

## Dietary Supplements (Optional - Consult Doctor)
- Daily multivitamin appropriate for age/gender
- Vitamin D (1000-2000 IU) if limited sun exposure
- Omega-3 fish oil (1000-2000mg) if not eating fish 2+ times weekly
- Magnesium (200-400mg) if experiencing sleep issues
- Probiotics for digestive health

## When to Seek Professional Help
- If experiencing persistent gastrointestinal distress
- If suspected food allergies develop
- If energy continues to decline after week 2
- For personalized macro ratios and recipes
- If have specific medical conditions requiring dietary modification

## Important Disclaimers
- This plan is a general guideline and should be personalized
- Consult with healthcare provider before major dietary changes
- Individual responses vary - monitor and adjust as needed
- Monitor for any adverse reactions to foods
- Supplement recommendations should be reviewed with doctor
- Stay consistent for 30 days to assess full effectiveness
- Results depend on adherence and individual metabolism
"""
        
        logger.info("✅ Auto-generated fallback diet plan created")
        return {
            "status": "success",
            "diet_plan": diet_plan,
            "generated_at": datetime.now().isoformat(),
            "auto_generated": True
        }
    
    def save_diet_plan(self, plan: Dict, filename: Optional[str] = None) -> str:
        """Save diet plan to file"""
        try:
            if filename is None:
                filename = f"reports/diet_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            
            with open(filename, 'w') as f:
                f.write(plan.get('diet_plan', ''))
            
            logger.info(f"Diet plan saved to {filename}")
            return filename
        
        except Exception as e:
            logger.error(f"Error saving diet plan: {e}")
            return ""


class Agent1_ReportAndDiet:
    """
    Coordinated Agent 1 combining report generation and diet planning
    """
    
    def __init__(self):
        self.report_gen = ReportGenerator()
        self.diet_gen = DietPlanGenerator()
    
    def execute(
        self,
        diagnosis: str,
        analyses: Dict[str, str],
        condition_severity: str = "moderate",
        patient_info: Optional[Dict] = None,
        dietary_restrictions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Execute complete Agent 1 workflow
        
        Returns:
            Combined report and diet plan
        """
        
        logger.info("🤖 Agent 1 executing: Report & Diet Plan Generation")
        
        # Generate medical report
        logger.info("📋 Generating medical report...")
        report = self.report_gen.generate_medical_report(
            diagnosis=diagnosis,
            analyses=analyses,
            patient_info=patient_info
        )
        
        # Generate diet plan (only if abnormal)
        diet_plan = None
        if condition_severity != "none":
            logger.info("🍎 Generating personalized diet plan...")
            diet_plan = self.diet_gen.generate_diet_plan(
                diagnosis=diagnosis,
                condition_severity=condition_severity,
                patient_info=patient_info,
                dietary_restrictions=dietary_restrictions
            )
        
        # Save both
        report_file = self.report_gen.save_report(report)
        diet_file = self.diet_gen.save_diet_plan(diet_plan) if diet_plan else None
        
        return {
            "status": "success",
            "agent": "Agent_1_ReportAndDiet",
            "medical_report": report,
            "diet_plan": diet_plan,
            "report_file": report_file,
            "diet_plan_file": diet_file,
            "timestamp": datetime.now().isoformat()
        }


# Convenience function
def generate_complete_health_package(
    diagnosis: str,
    analyses: Dict[str, str],
    patient_info: Optional[Dict] = None
) -> Dict[str, Any]:
    """Generate medical report + diet plan in one call"""
    agent = Agent1_ReportAndDiet()
    return agent.execute(diagnosis, analyses, patient_info=patient_info)
