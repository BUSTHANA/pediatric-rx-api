import json
import google.generativeai as genai
from typing import Optional
from app.config import get_settings
from app.exceptions.handlers import (
    AIRateLimitError,
    AIResponseError,
    AIServiceUnavailableError,
)


class AIService:

    def __init__(self):
        settings = get_settings()
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    async def calculate_dosage(
        self,
        medicine_name: str,
        child_weight_kg: float,
        child_age_years: float,
        condition: Optional[str] = None,
    ) -> dict:

        condition_context = (
            f"The child has the following condition/symptom: {condition}. "
            f"Tailor the dosage recommendation for this specific condition."
            if condition
            else "No specific condition was mentioned. Provide the most common pediatric dosage."
        )

        prompt = f"""
ROLE: You are a board-certified pediatric pharmacologist calculating medicine dosages
for children. You are precise, safety-conscious, and always err on the side of caution.

MEDICINE: {medicine_name}
CHILD'S WEIGHT: {child_weight_kg} kg
CHILD'S AGE: {child_age_years} years
CONDITION: {condition_context}

TASK: Calculate the exact dosage for each available form of this medicine. 

For each form (syrup, tablet, capsule, etc.) provide:
- The form name with concentration (e.g., "Syrup (120mg/5mL)")
- The single dose in mg (a single numeric value, calculated for this child's weight)
- For liquids: the dose in mL (a single numeric value, rounded to nearest 0.5 mL)
- For tablets/capsules: how many to give per dose (a single numeric value)
- How often to give (e.g., "Every 4-6 hours")
- Maximum doses per day (a single integer)

Also provide:
- Maximum daily dose in mg (a single numeric value)
- 2-3 short safety notes relevant to this medicine and age

RULES:
- All dose values must be SINGLE NUMBERS, not ranges
- Use the MIDDLE of the recommended range for calculations
- Round mL to nearest 0.5, tablets to nearest 0.5
- Only include forms appropriate for this child's age
- If this medicine is NOT suitable for this age/weight, return empty forms array

Respond ONLY with valid JSON in this exact format, no extra text or markdown:
{{
    "forms": [
        {{
            "form": "Syrup (120mg/5mL)",
            "dose_mg": 225.0,
            "dose_ml": 9.5,
            "frequency": "Every 4-6 hours",
            "max_doses_per_day": 4
        }},
        {{
            "form": "Tablet (250mg)",
            "dose_mg": 225.0,
            "dose_count": 1.0,
            "frequency": "Every 4-6 hours",
            "max_doses_per_day": 4
        }}
    ],
    "max_daily_dose_mg": 900.0,
    "notes": ["Give with or after food", "Use the measuring syringe provided"]
}}
"""

        try:
            response = self.model.generate_content(prompt)
        except google_exceptions.ResourceExhausted:
            raise AIRateLimitError()
        except google_exceptions.GoogleAPIError:
            raise AIServiceUnavailableError()
        except Exception:
            raise AIServiceUnavailableError()

        try:
            response_text = response.text.strip()

            if response_text.startswith("```"):
                response_text = response_text.split("\n", 1)[1]
                response_text = response_text.rsplit("```", 1)[0].strip()

            result = json.loads(response_text)
        except (json.JSONDecodeError, ValueError, AttributeError):
            raise AIResponseError()

        return {
            "forms": result.get("forms", []),
            "max_daily_dose_mg": result.get("max_daily_dose_mg", 0),
            "notes": result.get("notes", []),
        }

    async def get_medicine_info(self, medicine_name: str, child_age_years: Optional[float] = None) -> dict:

        age_context = (
            f"The child is {child_age_years} years old. Tailor all information "
            f"(dosage forms, risks, and recommendations) specifically for this age group."
            if child_age_years
            else "No age was specified. Provide general pediatric information suitable for children aged 0–15 years."
        )

        prompt = f"""
ROLE: You are a board-certified pediatric pharmacologist providing evidence-based
medicine information to parents. You are thorough, accurate, and safety-conscious.

MEDICINE: {medicine_name}
PATIENT CONTEXT: {age_context}

TASK: Analyze this medicine for pediatric use and provide:

1. ADVANTAGES (4–6 points) — Include:
   - Primary therapeutic benefits and what symptoms/conditions it treats
   - Child-friendly formulations available (e.g., liquid, chewable, dissolvable)
   - Speed of action and duration of relief
   - Safety profile and track record in pediatric use
   - Availability (over-the-counter vs. prescription)

2. DISADVANTAGES (4–6 points) — Include:
   - Common side effects specific to children
   - Serious but rare risks parents should watch for
   - Drug interactions or contraindications
   - Taste, administration difficulties, or compliance challenges
   - Age or weight restrictions and overdose risks

3. SUMMARY — A 2–3 sentence parent-friendly overview that includes:
   - What the medicine is primarily used for in children
   - The most important safety consideration
   - A reminder to consult their pediatrician

RULES:
- Use simple, non-medical language a parent can easily understand
- Be factual and balanced — do not exaggerate benefits or downplay risks
- If the medicine is NOT recommended for pediatric use, clearly state that
- Do NOT include dosage amounts — only a doctor should determine dosing

Respond ONLY with valid JSON in this exact format, no extra text or markdown:
{{
    "advantages": ["point 1", "point 2", "point 3", "point 4"],
    "disadvantages": ["point 1", "point 2", "point 3", "point 4"],
    "summary": "Your 2-3 sentence summary here."
}}
"""

        # Call Gemini API with error handling
        try:
            response = self.model.generate_content(prompt)
        except google_exceptions.ResourceExhausted:
            raise AIRateLimitError()
        except google_exceptions.GoogleAPIError:
            raise AIServiceUnavailableError()
        except Exception:
            raise AIServiceUnavailableError()

        # Parse the response with error handling
        try:
            response_text = response.text.strip()

            if response_text.startswith("```"):
                response_text = response_text.split("\n", 1)[1]
                response_text = response_text.rsplit("```", 1)[0].strip()

            result = json.loads(response_text)
        except (json.JSONDecodeError, ValueError, AttributeError):
            raise AIResponseError()

        return {
            "advantages": result.get("advantages", []),
            "disadvantages": result.get("disadvantages", []),
            "summary": result.get("summary", "No summary available."),
        }

    async def get_warning_signs(self, medicine_name: str, child_age_years: Optional[float] = None) -> dict:

        age_context = (
            f"The child is {child_age_years} years old. Focus on warning signs specific to this age group."
            if child_age_years
            else "No age specified. Cover warning signs for children aged 0–15 years."
        )

        prompt = f"""
ROLE: You are a pediatric emergency medicine specialist helping parents recognize
dangerous signs when their child is taking medication.

MEDICINE: {medicine_name}
PATIENT CONTEXT: {age_context}

TASK: Provide safety information a parent MUST know:

1. WARNING SIGNS (4–6 points) — Common side effects that parents should monitor:
   - Physical symptoms to watch for (rash, swelling, breathing changes, etc.)
   - Behavioral changes (drowsiness, irritability, loss of appetite)
   - Digestive issues (vomiting, diarrhea, stomach pain)
   - Signs the medicine isn't working or is making things worse

2. CALL DOCTOR IMMEDIATELY (3–5 points) — Serious red flags that need URGENT medical attention:
   - Allergic reaction signs (difficulty breathing, face/throat swelling, severe rash)
   - Organ-specific danger signs (yellowing skin, dark urine, unusual bleeding)
   - Neurological concerns (seizures, confusion, extreme drowsiness)
   - Any life-threatening symptoms

3. STOP MEDICATION IF (3–5 points) — Conditions where the parent should STOP giving the medicine:
   - Specific reactions that mean the child cannot tolerate this medicine
   - Signs of overdose or toxicity
   - Situations where continuing could cause harm

RULES:
- Use simple, clear language that a worried parent can quickly understand
- Be specific — say "swelling of the face or lips" not just "allergic reaction"
- Prioritize by severity — list the most dangerous signs first
- Do NOT include dosage information

Respond ONLY with valid JSON in this exact format, no extra text or markdown:
{{
    "warning_signs": ["sign 1", "sign 2", "sign 3", "sign 4"],
    "call_doctor_immediately": ["sign 1", "sign 2", "sign 3"],
    "stop_medication_if": ["condition 1", "condition 2", "condition 3"]
}}
"""

        try:
            response = self.model.generate_content(prompt)
        except google_exceptions.ResourceExhausted:
            raise AIRateLimitError()
        except google_exceptions.GoogleAPIError:
            raise AIServiceUnavailableError()
        except Exception:
            raise AIServiceUnavailableError()

        try:
            response_text = response.text.strip()

            if response_text.startswith("```"):
                response_text = response_text.split("\n", 1)[1]
                response_text = response_text.rsplit("```", 1)[0].strip()

            result = json.loads(response_text)
        except (json.JSONDecodeError, ValueError, AttributeError):
            raise AIResponseError()

        return {
            "warning_signs": result.get("warning_signs", []),
            "call_doctor_immediately": result.get("call_doctor_immediately", []),
            "stop_medication_if": result.get("stop_medication_if", []),
        }

    async def get_emergency_info(self, medicine_name: str, child_age_years: Optional[float] = None, child_weight_kg: Optional[float] = None) -> dict:

        age_context = (
            f"The child is {child_age_years} years old."
            if child_age_years
            else "Age not specified."
        )
        weight_context = (
            f"The child weighs {child_weight_kg} kg."
            if child_weight_kg
            else "Weight not specified."
        )

        prompt = f"""
ROLE: You are a pediatric emergency medicine specialist and poison control advisor
providing urgent guidance to a worried parent.

MEDICINE: {medicine_name}
PATIENT CONTEXT: {age_context} {weight_context}

TASK: Provide emergency/overdose information that could save a child's life:

1. OVERDOSE SIGNS (4–6 points) — How a parent can recognize an overdose:
   - Early symptoms that appear within the first hours
   - Physical signs (vomiting, pale skin, excessive sweating, etc.)
   - Behavioral signs (extreme drowsiness, confusion, unresponsiveness)
   - Delayed symptoms that may appear hours or days later
   - Signs specific to this particular medicine's toxicity

2. IMMEDIATE STEPS (4–6 points) — What the parent should do RIGHT NOW:
   - First action to take (call poison control / emergency services)
   - What information to have ready for the doctor
   - What to do and NOT do while waiting for help (e.g., do NOT induce vomiting)
   - How to keep the child safe and comfortable
   - When to drive to the ER vs call an ambulance

3. EMERGENCY CONTACTS — Provide these key contacts:
   - "poison_control": the national poison control number
   - "emergency": emergency services number
   - "advice": general advice line for parents

RULES:
- Write as if you are talking to a panicking parent — be calm, clear, and direct
- Use numbered steps for immediate_steps so they can follow them in order
- Be specific to this medicine — generic advice is not helpful in emergencies
- Do NOT include dosage calculations

Respond ONLY with valid JSON in this exact format, no extra text or markdown:
{{
    "overdose_signs": ["sign 1", "sign 2", "sign 3", "sign 4"],
    "immediate_steps": ["1. First do this", "2. Then do this", "3. Then do this"],
    "emergency_contacts": {{
        "poison_control": "1-800-222-1222 (US) or your local poison control center",
        "emergency": "911 (US) or your local emergency number",
        "advice": "Contact your pediatrician's after-hours line"
    }}
}}
"""

        try:
            response = self.model.generate_content(prompt)
        except google_exceptions.ResourceExhausted:
            raise AIRateLimitError()
        except google_exceptions.GoogleAPIError:
            raise AIServiceUnavailableError()
        except Exception:
            raise AIServiceUnavailableError()

        try:
            response_text = response.text.strip()

            if response_text.startswith("```"):
                response_text = response_text.split("\n", 1)[1]
                response_text = response_text.rsplit("```", 1)[0].strip()

            result = json.loads(response_text)
        except (json.JSONDecodeError, ValueError, AttributeError):
            raise AIResponseError()

        return {
            "overdose_signs": result.get("overdose_signs", []),
            "immediate_steps": result.get("immediate_steps", []),
            "emergency_contacts": result.get("emergency_contacts", {}),
        }

    async def check_interactions(self, medicines: list[str], child_age_years: Optional[float] = None) -> dict:

        medicine_list = ", ".join(medicines)
        age_context = (
            f"The child is {child_age_years} years old."
            if child_age_years
            else "No age specified. Provide general pediatric interaction info."
        )

        prompt = f"""
ROLE: You are a pediatric clinical pharmacist specializing in drug interactions,
helping a parent understand if multiple medicines are safe to give together.

MEDICINES: {medicine_list}
PATIENT CONTEXT: {age_context}

TASK: Analyze whether these medicines can be safely taken together by a child:

1. CAN TAKE TOGETHER (true/false) — A clear yes or no answer:
   - true = generally safe to take together with precautions
   - false = should NOT be taken together, or only under strict medical supervision

2. EXPLANATION — A 2–3 sentence parent-friendly explanation of:
   - Why these medicines do or don't interact
   - What happens in the body when they're combined
   - How common or serious the interaction is

3. PRECAUTIONS (3–5 points) — Safety tips if taking together:
   - Timing recommendations (e.g., "give at least 2 hours apart")
   - Symptoms to watch for when combining
   - Maximum duration for combined use
   - Which medicine to prioritize if only one can be given

4. ALTERNATIVE TIMING — A specific timing schedule suggestion:
   - Example: "Give Paracetamol first, then Ibuprofen 3 hours later if fever persists"
   - If they should NOT be combined, suggest an alternative approach

RULES:
- Be conservative — when in doubt, say they should NOT be combined
- Use simple language a worried parent can understand
- Be specific about timing (hours, not "space them out")
- Always recommend consulting a pediatrician for combined use
- Do NOT include dosage amounts

Respond ONLY with valid JSON in this exact format, no extra text or markdown:
{{
    "can_take_together": true,
    "explanation": "Clear explanation here.",
    "precautions": ["precaution 1", "precaution 2", "precaution 3"],
    "alternative_timing": "Specific timing suggestion here."
}}
"""

        try:
            response = self.model.generate_content(prompt)
        except google_exceptions.ResourceExhausted:
            raise AIRateLimitError()
        except google_exceptions.GoogleAPIError:
            raise AIServiceUnavailableError()
        except Exception:
            raise AIServiceUnavailableError()

        try:
            response_text = response.text.strip()

            if response_text.startswith("```"):
                response_text = response_text.split("\n", 1)[1]
                response_text = response_text.rsplit("```", 1)[0].strip()

            result = json.loads(response_text)
        except (json.JSONDecodeError, ValueError, AttributeError):
            raise AIResponseError()

        return {
            "can_take_together": result.get("can_take_together", False),
            "explanation": result.get("explanation", ""),
            "precautions": result.get("precautions", []),
            "alternative_timing": result.get("alternative_timing", ""),
        }
