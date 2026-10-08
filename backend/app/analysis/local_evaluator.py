import re


def evaluate_locally(question: str, transcript: str, role: str) -> dict:
    text = transcript.strip()
    words = re.findall(r"\b[\w+#.]+\b", text)
    word_count = len(words)

    if word_count == 0:
        return {
            "technical_score": 0,
            "structure_score": 0,
            "depth_score": 0,
            "overall_score": 0,
            "star_format_used": False,
            "strengths": [],
            "improvements": ["No speech was detected in the recording."],
            "model_answer_hint": "",
            "feedback_timestamps": [],
        }

    lower = text.lower()

    technical_terms = {
        "python", "java", "javascript", "sql", "database", "api",
        "algorithm", "data structure", "class", "object", "inheritance",
        "function", "variable", "array", "string", "loop", "exception",
        "backend", "frontend", "server", "client", "http", "rest",
        "cloud", "aws", "azure", "docker", "git", "machine learning",
        "artificial intelligence", "ai", "model", "testing", "debugging",
        "security", "network", "operating system", "computer",
        "software", "development", "framework"
    }

    matched_terms = sum(1 for term in technical_terms if term in lower)

    technical_score = min(95, 40 + matched_terms * 6)

    if word_count < 20:
        structure_score = 35
    elif word_count < 50:
        structure_score = 55
    elif word_count < 100:
        structure_score = 70
    elif word_count < 180:
        structure_score = 82
    else:
        structure_score = 90

    connectors = [
        "because", "therefore", "however", "for example",
        "for instance", "first", "second", "finally",
        "also", "then", "so"
    ]

    connector_count = sum(1 for word in connectors if word in lower)

    depth_score = min(
        95,
        45 + min(word_count // 10, 25) + connector_count * 5
    )

    star_words = [
        "situation", "task", "action", "result"
    ]

    star_count = sum(1 for word in star_words if word in lower)
    star_format_used = star_count >= 2

    if star_format_used:
        structure_score = min(100, structure_score + 10)
        depth_score = min(100, depth_score + 5)

    strengths = []
    improvements = []

    if word_count >= 50:
        strengths.append("Provided a reasonably detailed response.")
    else:
        improvements.append("Provide a more detailed answer with examples.")

    if matched_terms >= 3:
        strengths.append("Included relevant technical terminology.")
    else:
        improvements.append("Include more role-related technical concepts.")

    if connector_count >= 2:
        strengths.append("Used connecting ideas to explain the answer.")
    else:
        improvements.append("Explain the reasoning step by step.")

    if star_format_used:
        strengths.append("Used elements of the STAR response structure.")
    else:
        improvements.append("Use Situation, Task, Action, and Result when answering experience-based questions.")

    return {
        "technical_score": technical_score,
        "structure_score": structure_score,
        "depth_score": depth_score,
        "overall_score": 0,
        "star_format_used": star_format_used,
        "strengths": strengths,
        "improvements": improvements,
        "model_answer_hint": "Give a clear explanation with a relevant example and explain the result.",
        "feedback_timestamps": [],
    }