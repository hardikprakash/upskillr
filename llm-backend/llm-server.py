from llama_cpp import Llama

llm = Llama.from_pretrained(
	repo_id="cognitivecomputations/Dolphin3.0-Llama3.1-8B-GGUF",
	filename="Dolphin3.0-Llama3.1-8B-Q4_K_M.gguf",
)
