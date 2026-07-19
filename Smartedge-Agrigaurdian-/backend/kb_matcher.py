"""
SmartEdge AgriGuardian - Knowledge Base Matcher
=================================================
Yeh module farmer ke query (text) ko knowledge_base.json se match karta hai.
Agar match mil jaye -> structured solution return karta hai.
Agar match na mile -> Ollama (local LLM) se fallback response generate hota hai.
"""

import json
import os
import requests

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
# Step 4: Ollama Fallback (Jab Knowledge Base Mein Match Na Mile)
# ---------------------------------------------------

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma2:2b"  # Same model jo tumne pull kiya hai


def call_ollama(user_query, crop_hint=None, sensor_context=None):
    """
    Ollama (local LLM) ko call karta hai jab knowledge base mein
    koi match nahi milta. Yeh poori tarah OFFLINE kaam karta hai
    (koi internet nahi chahiye - Ollama laptop/PC pe hi chal raha hota hai).

    Args:
        user_query (str): Farmer ka original sawal
        crop_hint (str, optional): Kis crop ke baare mein hai
        sensor_context (dict, optional): Jaise {"moisture": 28, "temperature": 32}

    Returns:
        str: Ollama se generated response, ya error message agar Ollama chal nahi raha
    """

    # Prompt banate hain - jitna context denge, utna behtar jawab milega
    context_parts = [f"Farmer ka sawal: {user_query}"]

    if crop_hint:
        context_parts.append(f"Crop: {crop_hint}")

    if sensor_context:
        sensor_str = ", ".join([f"{k}: {v}" for k, v in sensor_context.items()])
        context_parts.append(f"Sensor data: {sensor_str}")

    prompt = (
        "Tum ek agriculture advisor ho jo Indian farmers ko madad karta hai. "
        "Neeche diye gaye sawal ka practical, seedha aur farmer-friendly jawab do "
        "Hindi-English mix (Hinglish) mein. Jawab short aur actionable rakho "
        "(max 4-5 lines). Agar disease/pest ka zikar hai to organic aur chemical "
        "dono treatment suggest karo.\n\n"
        + "\n".join(context_parts)
    )

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip()

    except requests.exceptions.ConnectionError:
        return (
            "Ollama server nahi chal raha hai. Terminal mein 'ollama serve' "
            "chalao ya Ollama app open karo, phir try karo."
        )
    except requests.exceptions.Timeout:
        return "Ollama se response aane mein zyada time lag raha hai. Dobara try karo."
    except Exception as e:
        return f"Ollama call mein error aaya: {str(e)}"


# ---------------------------------------------------
# Step 5: Main Handler Function (Yeh sabse important hai)
# ---------------------------------------------------

def get_advisory_response(user_query, crop_hint=None, sensor_context=None,
                            kb_path="../knowledge-base/knowledge_base.json"):
    """
    Yeh main function hai jo poora flow handle karta hai:
    1. Knowledge base load karo
    2. Best match dhoondo
    3. Match mila -> structured response do (fast, offline, free)
    4. Match nahi mila -> Ollama (local LLM) se response generate karo (offline)

    Args:
        user_query (str): Farmer ka sawal
        crop_hint (str, optional): Konsi crop hai
        sensor_context (dict, optional): Live sensor data (moisture, temp, etc.)
        kb_path (str): knowledge_base.json ka path

    Returns:
        dict: {
            "source": "knowledge_base" ya "ollama_fallback",
            "response": str,
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
        # Match nahi mila -> Ollama ko call karo (yeh bhi offline hi chalta hai)
        ollama_response = call_ollama(user_query, crop_hint, sensor_context)
        return {
            "source": "ollama_fallback",
            "response": ollama_response,
            "matched_id": None
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
            print(f"[OLLAMA FALLBACK - No KB match found]")
            print(result["response"])