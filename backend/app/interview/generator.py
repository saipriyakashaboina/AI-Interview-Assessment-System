from ..ai_client import call_ai_json

SYSTEM_PROMPT = (
    "You are an experienced technical interviewer conducting a realistic mock interview. "
    "Your goal is to help students prepare for actual job interviews. "
    "Generate questions that are clear, specific, and directly relevant to the role and difficulty. "
    "Return JSON only. No markdown fences. No extra keys."
)

_TYPE_GUIDE = """
Question type definitions:
- technical_concept : Test core knowledge of the role's tools, languages, or frameworks.
- coding            : Ask the candidate to write, trace, or reason about a small piece of code.
- behavioral        : Past-experience questions using the STAR format.
- situational       : Hypothetical / problem-solving scenarios relevant to the role.
- system_design     : High-level architecture and design trade-off questions.
- hr                : Motivation, goals, and culture-fit questions.
"""

_MIX = {
    "1": ["technical_concept", "technical_concept", "coding", "behavioral", "situational", "hr"],
    "2": ["technical_concept", "technical_concept", "coding", "behavioral", "situational", "hr"],
    "3": ["technical_concept", "technical_concept", "coding", "system_design", "behavioral", "situational"],
    "4": ["technical_concept", "coding", "system_design", "system_design", "behavioral", "situational"],
    "5": ["technical_concept", "coding", "system_design", "system_design", "behavioral", "hr"],
}

_DIFFICULTY_LABELS = {
    "1": "Fresher — no industry experience, recently graduated or still studying",
    "2": "Junior — 0-1 years of experience, first or second job",
    "3": "Mid-Level — 1-3 years, works independently",
    "4": "Senior — 3-5 years, mentors others, owns features end-to-end",
    "5": "Lead / Principal — 5+ years, drives architecture and team decisions",
}

USER_TEMPLATE = """
You are generating exactly 7 interview questions for a mock interview session.

Candidate profile
-----------------
Role       : {role}
Difficulty : {difficulty}
Resume     : {resume_summary}

Question mix to follow (in this exact order)
--------------------------------------------
{mix_instructions}

{type_guide}

Rules
-----
1. Follow the mix order exactly.
2. Tailor difficulty, vocabulary, and depth to the level described above.
3. For coding questions at Fresher/Junior level, keep problems simple.
4. For behavioral and HR questions, make them natural and conversational.
5. If a resume is provided, personalize at least 2 questions around the candidate's skills or projects.
6. Each question must be self-contained.
7. expected_duration_seconds: hr/behavioral ≈ 120, coding ≈ 180, technical_concept ≈ 90, system_design ≈ 240.

Return this exact JSON:
{{
  "questions": [
    {{
      "id": <int 1–7>,
      "text": <the full question string>,
      "type": <one of the type strings above>,
      "focus_area": <short label>,
      "expected_duration_seconds": <int>
    }}
  ]
}}
"""

def fallback_questions(role: str, difficulty: str) -> list[dict]:
    role_name = role.strip() if role else "Software Developer"

    questions = [
        {
            "id": 1,
            "text": f"What are the most important technical skills you would use as a {role_name}?",
            "type": "technical_concept",
            "focus_area": "Core technical skills",
            "expected_duration_seconds": 90,
        },
        {
            "id": 2,
            "text": f"Explain one important concept that a {role_name} should know well.",
            "type": "technical_concept",
            "focus_area": "Technical fundamentals",
            "expected_duration_seconds": 90,
        },
        {
            "id": 3,
            "text": "Choose a programming problem involving arrays or strings. Explain your approach step by step and discuss its time complexity.",
            "type": "coding",
            "focus_area": "Problem solving",
            "expected_duration_seconds": 180,
        },
        {
            "id": 4,
            "text": "Tell me about a project you worked on. What was your role, what challenges did you face, and how did you solve them?",
            "type": "behavioral",
            "focus_area": "Project experience",
            "expected_duration_seconds": 120,
        },
        {
            "id": 5,
            "text": f"Imagine you are working as a {role_name} and your application suddenly starts giving incorrect results. How would you investigate and solve the problem?",
            "type": "situational",
            "focus_area": "Problem solving",
            "expected_duration_seconds": 120,
        },
        {
            "id": 6,
            "text": f"Why do you want to work as a {role_name}, and what skills do you want to develop in your first few years?",
            "type": "hr",
            "focus_area": "Career goals",
            "expected_duration_seconds": 120,
        },
        {
            "id": 7,
            "text": "What is one technical skill you are currently improving, and how are you practicing it?",
            "type": "behavioral",
            "focus_area": "Learning and growth",
            "expected_duration_seconds": 120,
        },
    ]

    return questions


async def generate_questions(
    role: str,
    difficulty: str,
    resume_summary: str = "No resume provided.",
) -> list[dict]:
    diff_key = str(difficulty)
    diff_label = _DIFFICULTY_LABELS.get(diff_key, difficulty)
    mix = _MIX.get(diff_key, _MIX["1"])

    mix_instructions = "\n".join(
        f"  Q{i+1}: {qtype}" for i, qtype in enumerate(mix)
    )

    prompt = USER_TEMPLATE.format(
        role=role,
        difficulty=diff_label,
        resume_summary=resume_summary[:2000],
        mix_instructions=mix_instructions,
        type_guide=_TYPE_GUIDE,
    )

    try:
        data = await call_ai_json(SYSTEM_PROMPT, prompt, max_tokens=3000)
        questions = data.get("questions", [])

        if len(questions) >= 7:
            return questions[:7]

    except Exception:
        pass

    return fallback_questions(role, difficulty)