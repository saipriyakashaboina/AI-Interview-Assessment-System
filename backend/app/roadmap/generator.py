def generate_week(week, focus, tasks):
    return {
        "week": week,
        "focus": focus,
        "daily_tasks": tasks,
        "resources": [
            {
                "title": "Practice on HackerRank",
                "url": "https://www.hackerrank.com/",
                "type": "practice"
            },
            {
                "title": "Practice on GeeksforGeeks",
                "url": "https://www.geeksforgeeks.org/",
                "type": "article"
            }
        ]
    }


async def generate_roadmap(
    role: str,
    weak_areas: list[str],
    missing_skills: list[str],
    score: int,
) -> dict:

    role_lower = role.lower()

    if "backend" in role_lower:
        focus1 = "Backend fundamentals and programming"
        focus2 = "Databases and APIs"
        focus3 = "System design and testing"
        focus4 = "Interview preparation and projects"
    elif "frontend" in role_lower:
        focus1 = "Frontend fundamentals"
        focus2 = "JavaScript and React"
        focus3 = "APIs and application development"
        focus4 = "Interview preparation and projects"
    elif "data" in role_lower or "machine" in role_lower:
        focus1 = "Python and data structures"
        focus2 = "Data analysis and machine learning"
        focus3 = "Model evaluation and projects"
        focus4 = "Interview preparation and projects"
    else:
        focus1 = "Programming and computer science fundamentals"
        focus2 = "Data structures, algorithms and databases"
        focus3 = "Software development and projects"
        focus4 = "Interview preparation and career readiness"

    weeks = [
        generate_week(
            1,
            focus1,
            [
                "Practice Python or Java programming",
                "Revise OOP concepts",
                "Practice basic problem solving",
                "Revise DBMS and operating system fundamentals",
                "Solve 2 coding problems",
                "Review mistakes and improve weak areas",
                "Take a short technical practice test"
            ]
        ),
        generate_week(
            2,
            focus2,
            [
                "Revise SQL basics",
                "Practice database queries",
                "Learn REST API fundamentals",
                "Practice data structures",
                "Solve 3 coding problems",
                "Build or improve one API feature",
                "Review the week's concepts"
            ]
        ),
        generate_week(
            3,
            focus3,
            [
                "Revise software engineering concepts",
                "Practice debugging techniques",
                "Learn basic system design concepts",
                "Improve one project feature",
                "Practice Git and GitHub",
                "Solve 3 interview coding problems",
                "Review project architecture"
            ]
        ),
        generate_week(
            4,
            focus4,
            [
                "Practice common technical interview questions",
                "Prepare project explanations",
                "Practice behavioral interview questions",
                "Improve communication and answer structure",
                "Take a mock coding test",
                "Review strengths and weak areas",
                "Complete a final mock interview"
            ]
        )
    ]

    weaknesses = weak_areas[:5] if weak_areas else [
        "Improve technical fundamentals",
        "Improve problem solving",
        "Improve communication"
    ]

    return {
        "summary": (
            f"Your current interview score is {score}/100. "
            f"This 30-day roadmap is designed to improve your "
            f"{role} skills through technical practice, projects, "
            f"problem solving and interview preparation."
        ),
        "weeks": weeks,
        "quick_wins": [
            "Practice coding for at least 30 minutes every day.",
            "Revise one core computer science topic every day.",
            "Explain your projects clearly using simple examples.",
            "Practice answering interview questions aloud.",
            "Review and improve your weak areas regularly."
        ]
    }