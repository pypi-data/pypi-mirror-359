# ksuit

    uv venv --python 3.12
    source .venv/bin/activate
    uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
    uv pip install pynvml
    uv pip install wandb
    uv pip install hydra-core
    uv pip install tqdm
    uv pip install einops

# pre-commit

    pre-commit install
    pre-commit run --all-files

# torchrun
    
    torchrun --nproc-per-node=3 main_train.py



# resume

    +resume.id=RUN_ID