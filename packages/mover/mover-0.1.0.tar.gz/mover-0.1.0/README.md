# MoVer: Motion Verification for Motion Graphics Animations

[Jiaju Ma](https://majiaju.io) and
[Maneesh Agrawala](https://graphics.stanford.edu/~maneesh/)
<br />
In ACM Transactions on Graphics (SIGGRAPH), 44(4), August 2025. To Appear.
<br />

[[arXiv](https://arxiv.org/abs/2502.13372)]  [[project page](https://mover-dsl.github.io/)]


## Dataset
The test prompt dataset used in the paper can be found in `mover_dataset`


## Setup

### JavaScript animation to MoVer data format converter
1. (Optional) We support rendering to video with OpenCV, but the video produced might have limited compatibility. If you optionally install `ffmpeg`, our converter will automatically use it to convert rendered videos.

### MoVer
1. Set up a virtual environment with your favorite tool. It is recommended to use `uv` because it is very fast.
2. Make sure you have `pytorch` installed
3. Install [Jacinle](https://github.com/vacancy/Jacinle).
```bash
  git clone https://github.com/vacancy/Jacinle --recursive
  cd Jacinle
  pip install -e . # or uv pip install -e . or follow the instructions on the Jacinle GitHub page
```

4. Install [Concepts](https://github.com/concepts-ai/concepts).
```bash
  git clone https://github.com/concepts-ai/Concepts.git
  cd Concepts
  pip install -e . # or uv pip install -e .
```

5. Run `pip install -r requirements.txt` or `uv pip install -r requirements.txt` to install the remaining dependencies
    - This list includes APIs to interface with OpenAI, Gemini (via OpenAI), and Groq

6. Store your API keys as environment variables (e.g., `OPENAI_API_KEY`, `GEMINI_API_KEY`, `GROQ_API_KEY`).

7. If you plan to run locally-hosted models, install the following dependencies:
    - Install `ollama` if you plan to use ollama with `ollama-python`
    - Install `vLLM` if you plan to use vLLM


## Usage
Check out the `tutorial.ipynb` for a tutorial of the motion graphics animation generation with MoVer verification pipeline.


## Release Checklist
- [x] MoVer DSL and verifier
- [x] JavaScript animation to MoVer data format converter
- [x] LLM-based animation synthesizer
- [x] LLM-based MoVer synthesizer
- [x] Scripts to run the full pipeline
- [ ] Web app for creating animations with MoVer
- [ ] Scripts for generating animation prompts
