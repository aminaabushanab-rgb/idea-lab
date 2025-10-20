from src.config import CONFIG, OPENAI_API_KEY

print("✅ Config loaded:", CONFIG)
print("✅ Project name:", CONFIG.get("project_name"))
print("✅ LLM model:", CONFIG.get("llm_model"))
print("✅ Embed model:", CONFIG.get("embed_model"))
print("✅ API key present?:", bool(OPENAI_API_KEY))

