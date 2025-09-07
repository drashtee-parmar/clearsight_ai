# import os, json
# from dotenv import load_dotenv
# from google import genai

# load_dotenv()

# # Prefer explicit API key wiring to avoid surprises
# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# SYSTEM_PROMPT = """
# You are an AI Compliance & Accessibility Editor.
# Return ONLY valid JSON. No prose, no markdown, no code fences.

# Given INPUT_TEXT (which may be plain text or HTML), do:
# 1) Accessibility (WCAG 2.2 AA subset): flag missing headings, vague links, missing/weak alt text, overly complex language (grade > 9), and any contrast hints if explicitly described.
# 2) Compliance: flag PII (emails, phones, full names), toxicity/bias, and policy-sensitive phrasing.
# 3) For each issue, include: category ("accessibility"|"compliance"), text_snippet, problem, why, suggestion.
# 4) Provide a clean_version with suggested fixes applied.

# Output schema:
# {
#   "issues": [
#     {
#       "category": "accessibility" | "compliance",
#       "text_snippet": "string",
#       "problem": "string",
#       "why": "string",
#       "suggestion": "string"
#     }
#   ],
#   "clean_version": "string"
# }
# """

# # Small, deterministic test input to verify pipeline
# INPUT_TEXT = """
# <h1>Welcome</h1>
# <p>Click here</p>
# <p>Contact John Doe at john@example.com for help.</p>
# <img src="banner.png">
# """

# def call_model(prompt: str, text: str) -> dict:
#     """Call Gemini and return parsed JSON with a minimal de-noising step."""
#     req = f"{prompt}\n\nINPUT_TEXT:\n{text}\n"
#     resp = client.models.generate_content(
#         model="gemini-2.5-flash",
#         contents=req
#     )
#     raw = (resp.text or "").strip()

#     # Some safety: if the model ever adds stray text, trim to the outermost JSON braces.
#     try:
#         start = raw.find("{")
#         end = raw.rfind("}") + 1
#         if start != -1 and end != -1:
#             raw = raw[start:end]
#         data = json.loads(raw)
#         assert isinstance(data.get("issues", []), list)
#         assert "clean_version" in data
#         return data
#     except Exception as e:
#         raise RuntimeError(f"Model did not return valid JSON. Raw output:\n{raw}\n\nError: {e}")

# def pretty_report(data: dict) -> None:
#     issues = data.get("issues", [])
#     print(f"\n✅ Parsed JSON. Issues found: {len(issues)}")
#     for i, item in enumerate(issues, 1):
#         cat = item.get("category")
#         prob = item.get("problem")
#         sugg = item.get("suggestion")
#         print(f"\n[{i}] {cat}: {prob}\n→ Fix: {sugg}")
#     print("\n--- Clean Version Preview ---")
#     print(data.get("clean_version", "")[:300], "...\n")

# # if __name__ == "__main__":
# #     result = call_model(SYSTEM_PROMPT, INPUT_TEXT)
# #     pretty_report(result)

# if __name__ == "__main__":
#     while True:
#         user_input = input("\nEnter text/HTML to check (or 'quit'): ").strip()
#         if user_input.lower() in {"quit", "exit"}:
#             break
#         try:
#             result = call_model(SYSTEM_PROMPT, user_input)
#             pretty_report(result)
#         except Exception as e:
#             print("Error:", e)