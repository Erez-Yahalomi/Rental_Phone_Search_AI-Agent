 DEFAULT_QUESTIONS = [
    "Is the unit still available?",
    "What is the earliest move-in date?",
    "Are utilities included in the rent?",
    "Any application fees or broker fees?",
    "What is the lease term and renewal policy?",
    "Are pets allowed, and are there restrictions or fees?",
    "Is parking available and what are the costs?",
    "Have there been any recent updates or renovations?",
]

def build_question_set(user_questions):
    """
    Merge default questions and user questions, keeping order and removing duplicates.
    """
    seen, merged = set(), []
    for q in DEFAULT_QUESTIONS + (user_questions or []):
        if q not in seen:
            merged.append(q)
            seen.add(q)
    return merged
