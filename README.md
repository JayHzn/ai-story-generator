# AI-Powered Text Generation for Writers

A modular platform built with **PyTorch** and the Hugging Face ecosystem, designed to assist authors—novelists, short-story writers, and video scriptwriters—in generating, revising, and enriching their texts.

## 📖 Description

This repository contains everything you need to:

1. **Collect** and organize an inspirational corpus  
2. **Clean** and **normalize** raw data (HTML tags, encoding issues, duplicates)  
3. **Tokenize** and **segment** text into units consumable by a Transformer model  
4. **Annotate** linguistically (POS tagging, lemmatization, NER, dependency parsing) with spaCy  
5. Prepare a **PyTorch Dataset** for fine-tuning  
6. Fine-tune an auto-regressive model (e.g., GPT-2, GPT-NeoX) using `AutoModelForCausalLM`  
7. **Evaluate** (perplexity, BLEU, semantic similarity) and validate generation quality  
8. Deploy an **inference API** (FastAPI + TorchServe/ONNX)  
9. Apply **post-processing** for style and final coherence  
10. Implement **monitoring** (Weights & Biases / TensorBoard)

## ⭐️ Features

- Auto-regressive text generation: stories, dialogues, and scripts  
- Fine-tuning of generation parameters (temperature, top-k, top-p)  
- End-to-end NLP pipeline in French: cleaning, tokenization, annotations  
- Simple HTTP interface to integrate text generation into any application  
- Logging and dashboards to track training and inference metrics

## 🗂️ Repository Structure

```
├── data/                   # Raw and cleaned corpora  
├── src/
│   ├── ingestion/
│   ├── cleaning/
│   ├── tokenization/
│   ├── annotation/
│   ├── dataset/
│   ├── training/
│   ├── evaluation/
│   └── api/
├── notebooks/
├── requirements.txt
└── README.md
```

## 🚀 Installation

```bash
git clone https://github.com/<your-org>/ai-text-gen.git
cd ai-text-gen
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## ▶️ Quick Start

1. **Clean** and **tokenize** a sample file:  
   ```bash
   python src/cleaning/clean_text.py \
     --input data/raw/example.txt \
     --output data/cleaned/example.txt

   python src/tokenization/tokenize.py \
     --model gpt2 \
     --input data/cleaned/example.txt \
     --output data/tokenized/example.pt
   ```

2. **Run** a mini fine-tuning on GPT-2 small:  
   ```bash
   python src/training/train.py \
     --model gpt2 \
     --data data/tokenized/example.pt \
     --output-dir outputs/gpt2-demo \
     --epochs 1
   ```

3. **Test** the inference API:  
   ```bash
   uvicorn src/api/app:app --reload
   ```
   Then open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.

## 🤝 Contributing

Contributions and ideas are welcome!

1. Fork the repository  
2. Create a branch (`feature/your-feature`)  
3. Open a pull request describing your changes

## 📄 License

MIT © 2025 – Empowering writers to unleash their creativity.
