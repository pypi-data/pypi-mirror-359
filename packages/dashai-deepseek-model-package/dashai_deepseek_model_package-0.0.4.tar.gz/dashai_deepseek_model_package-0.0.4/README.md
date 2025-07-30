# DeepSeek LLM model for DashAI

This plugin integrates the **DeepSeek LLM 7B Chat** model into the DashAI framework using the `llama.cpp` backend. It enables text generation tasks via a lightweight and efficient inference engine with support for quantized GGUF models.

## Components

### DeepSeekModel

- Based on the `llama.cpp` backend using the GGUF quantized format
- Loads the model from HuggingFace: [`TheBloke/deepseek-llm-7B-chat-GGUF`](https://huggingface.co/TheBloke/deepseek-llm-7B-chat-GGUF)
- Uses the `deepseek-llm-7b-chat.Q5_K_M.gguf` quantized file
- Compatible with CPU and GPU inference
- Implements the `TextToTextGenerationTaskModel` interface of DashAI

## Features

- Text generation with the following configurable parameters:
  - **`max_tokens`**: Number of tokens to generate
  - **`temperature`**: Controls randomness of output
  - **`frequency_penalty`**: Reduces repetition in output
  - **`n_ctx`**: Context window size
  - **`device`**: Inference device (`"cpu"` or `"gpu"`)
- Efficient memory usage via quantized GGUF format
- Automatic truncation of overly long prompts
- Custom stop sequence (`["Q:"]`) for cleaner outputs

## Model Parameters

| Parameter           | Description                                      | Default              |
| ------------------- | ------------------------------------------------ | -------------------- |
| `max_tokens`        | Maximum number of tokens to generate             | 100                  |
| `temperature`       | Sampling temperature (higher = more random)      | 0.7                  |
| `frequency_penalty` | Penalizes repeated tokens to encourage diversity | 0.1                  |
| `n_ctx`             | Maximum context window (tokens in prompt)        | 4096                 |
| `device`            | Device for inference (`"gpu"` or `"cpu"`)        | `"gpu"` if available |

## Requirements

- `DashAI`
- `llama-cpp-python`
- Model files from HuggingFace:
  - [`TheBloke/deepseek-llm-7B-chat-GGUF`](https://huggingface.co/TheBloke/deepseek-llm-7B-chat-GGUF)
  - Use the quantized file `deepseek-llm-7b-chat.Q5_K_M.gguf`

## Notes

This plugin uses the **GGUF** format, introduced by the `llama.cpp` team in August 2023.  
GGUF replaces the older **GGML** format, which is no longer supported by `llama.cpp`.

GGUF models are optimized for fast inference and lower memory consumption, especially in CPU/GPU-constrained environments.

The file `deepseek-llm-7b-chat.Q5_K_M.gguf` is a quantized version of the original **DeepSeek LLM 7B Chat** model.  
The **Q5_K_M** quantization offers a good trade-off between model size and quality, making it suitable for real-time or resource-limited applications.

The model used in this plugin is a **pretrained chat-oriented version** and is **not designed for fine-tuning**. It is intended for **inference only**.
