"""
SmartEdge AgriGuardian - Knowledge Base Matcher
=================================================
Yeh module farmer ke query (text) ko knowledge_base.json se match karta hai.
Agar match mil jaye -> structured solution return karta hai.
Agar match na mile -> fallback signal deta hai (Gemini API call ke liye).
"""

import json
import os

# ---------------------------------------------------
# Step 1: Knowledge Base Load Karo
# ---------------------------------------------------

def load_knowledge_base(file_path="knowledge-base/knowledge_base.json"):
    """
    knowledge_base.json file ko load karke Python dictionary mein convert karta hai.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Knowledge base file nahi mili: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


# ---------------------------------------------------
# Step 2: Matching Function (Core Logic)
# ---------------------------------------------------

def find_best_match(user_query, knowledge_base, crop_hint=None):
    """
    User ke query ko knowledge base ke keywords se match karta hai.

    Args:
        user_query (str): Farmer ka sawal, jaise "aaloo pe safed daag hai"
        knowledge_base (dict): Loaded JSON data
        crop_hint (str, optional): Agar pehle se pata hai konsi crop hai (jaise "aaloo")

    Returns:
        dict: Matched problem ka poora data, ya None agar kuch match nahi mila
    """

    query_lower = user_query.lower().strip()
    problems = knowledge_base.get("problems", [])

    best_match = None
    best_score = 0

    for problem in problems:
        score = 0
        keywords = problem.get("keywords", [])
        crops = problem.get("crops", [])

        # Keyword matching - kitne keywords query mein mile
        for keyword in keywords:
            if keyword.lower() in query_lower:
                score += 1

        # Agar crop hint diya hai aur match karta hai, extra weight do
        if crop_hint:
            crop_hint_lower = crop_hint.lower()
            if crop_hint_lower in [c.lower() for c in crops] or "all" in crops:
                score += 0.5

        # Best match track karo
        if score > best_score:
            best_score = score
            best_match = problem

    # Minimum threshold - agar koi keyword match nahi hua toh None return karo
    if best_score == 0:
        return None

    return best_match


# ---------------------------------------------------
# Step 3: Response Builder (Farmer-Friendly Format)
# ---------------------------------------------------

def build_response(matched_problem):
    """
    Matched problem ke data ko ek clean, readable response mein convert karta hai.
    """
    if matched_problem is None:
        return None

    name = matched_problem.get("name", "Unknown Issue")
    solution = matched_problem.get("solution", {})
    prevention = matched_problem.get("prevention", "")
    severity = matched_problem.get("severity", "unknown")

    response_lines = [f"Detected Issue: {name} (Severity: {severity})", ""]

    # Solution ke saare parts add karo (organic, chemical, water, other, action, etc.)
    for key, value in solution.items():
        label = key.replace("_", " ").capitalize()
        response_lines.append(f"{label}: {value}")

    if prevention:
        response_lines.append("")
        response_lines.append(f"Prevention Tip: {prevention}")

    return "\n".join(response_lines)


# ---------------------------------------------------
# Step 4: Main Handler Function (Yeh sabse important hai)
# ---------------------------------------------------

def get_advisory_response(user_query, crop_hint=None, kb_path="../knowledge-base/knowledge_base.json"):
    """
    Yeh main function hai jo poora flow handle karta hai:
    1. Knowledge base load karo
    2. Best match dhoondo
    3. Match mila -> structured response do
    4. Match nahi mila -> fallback signal do (Gemini call trigger karne ke liye)

    Returns:
        dict: {
            "source": "knowledge_base" ya "fallback_needed",
            "response": str ya None,
            "matched_id": str ya None
        }
    """

    kb = load_knowledge_base(kb_path)
    match = find_best_match(user_query, kb, crop_hint)

    if match:
        response_text = build_response(match)
        return {
            "source": "knowledge_base",
            "response": response_text,
            "matched_id": match.get("id")
        }
    else:
        # Match nahi mila -> Gemini API ko call karna hoga (yeh signal hai)
        fallback_msg = kb.get("fallback", {}).get("message", "Match nahi mila.")
        return {
            "source": "fallback_needed",
            "response": None,
            "matched_id": None,
            "note": fallback_msg
        }


# ---------------------------------------------------
# Step 5: Test Karne Ke Liye (Yeh section run karke check karo)
# ---------------------------------------------------

if __name__ == "__main__":
    # Test queries
    test_queries = [
        ("Aaloo ki fasal mein safed daag aa rahe hain", "aaloo"),
        ("Meri mitti sukh gayi hai", None),
        ("Mera plant achha lag raha hai", None),
        ("Bilkul random alag query jo kahin match nahi hogi", None),
    ]

    print("=" * 50)
    print("TESTING KNOWLEDGE BASE MATCHER")
    print("=" * 50)

    for query, crop in test_queries:
        print(f"\nQuery: '{query}' (Crop hint: {crop})")
        print("-" * 50)
        result = get_advisory_response(query, crop_hint=crop)

        if result["source"] == "knowledge_base":
            print(f"[MATCHED - ID: {result['matched_id']}]")
            print(result["response"])
        else:
            print(f"[NO MATCH - Fallback needed]")
            print(result["note"])