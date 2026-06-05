from huggingface_hub import hf_hub_download
from llama_cpp import Llama

_model = None

def load_model():
    global _model

    if _model is not None:
        return _model

    model_path = hf_hub_download(
        repo_id="Abiray/MiniCPM5-1B-GGUF",
        filename="minicpm5-1b-Q4_K_M.gguf",
    )

    _model = Llama(
        model_path=model_path,
        n_ctx=4096,
        n_threads=4,
        verbose=False,
    )

    return _model