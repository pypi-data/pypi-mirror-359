# Omniformer

**Omniformer** is a context-aware Transformer architecture enhanced with per-sample **HyperNetworks**, built to classify gravitational-wave triggers (e.g., LIGO Omicron events) in noisy, multi-channel time-series data. Each Transformer's weights are dynamically generated based on channel-specific context, enabling improved detection accuracy and robustness.

---

# 🧠 Meta-Optimized Omniformer

## Hyperparameter Tuning for the OMICRON Pipeline (LIGO O3a)

This project proposes a **meta-learning** approach to automate and optimize hyperparameter tuning for the [OMICRON pipeline](https://gw-openscience.org/omicron/), which detects non-Gaussian noise transients in gravitational-wave data.

---

## 🚀 Motivation

OMICRON relies on manually tuned parameters like frequency thresholds, SNR cutoffs, Q-ranges, and PSD lengths—making the process subjective and labor-intensive.
We propose a **meta-learning-based automation** using deep learning to improve detection accuracy and reproducibility.

---

## 🔍 Key Contributions

* 📁 Built a dataset from OMICRON runs with varying hyperparameters
* 🧠 Trained ML classifiers (Random Forest, KarooGP) on transient outputs
* ♻️ Developed **Omniformer**: a transformer model with dynamic weights from a HyperNet
* ⚖️ Integrated a **Meta-Optimizer** for weight tuning through feedback
* ♻️ Designed a 3-stage optimization pipeline:

  1. Transformer-based modeling
  2. HyperNet-based parameter control
  3. Meta-optimization with feedback learning

---

## 🧪 Methodology

1. **Data Generation**
   Run OMICRON with varied hyperparameters to generate `.hdf5`, `.csv`, `.root` outputs.

2. **Classification**
   Label triggers using Random Forests or KarooGP.

3. **Omniformer Training**
   Train the context-aware Transformer on these classification results.

4. **HyperNetwork Tuning**
   Dynamically generate QKV and FFN weights from channel-specific context.

5. **Meta-Learning Optimization**
   A meta-optimizer refines model weights via feedback.

---

## 🤖 Why Meta-Learning?

Meta-learning ("learning to learn") enables:

* Generalization across runs and detectors
* Better adaptation to non-Gaussian noise
* Reduced reliance on expert-crafted hyperparameters

---

## 📊 Research Highlights

* Per-sample dynamic weight generation for attention and feedforward layers
* Gated residual connections for improved deep Transformer training
* Supports streaming from large CSVs (100s of GB)
* Automatic batch size reduction on GPU OOM

---

## 📄 Project Structure

```txt
omniformer/                  # Core package
├── __init__.py              # Expose Omniformer, Dataset, utils
├── model.py                 # Omniformer architecture + HyperNet
├── utils.py                 # Dataset, filtering, preprocessing
├── config.py                # Global hyperparameters & paths
├── train.py                 # CLI training script
├── inference.py             # CLI batch inference
└── app.py                   # Streamlit web UI
README.md                    # This documentation
setup.py                     # Packaging metadata
requirements.txt             # Dependencies
```

---

## 🛠️ Installation

Install from PyPI:

```bash
pip install omniformer
```

Development version:

```bash
git clone https://github.com/yourusername/omniformer.git
cd omniformer
pip install -e .
```

---

## 📚 Quickstart

### 1. Training

```bash
omniformer-train \
  --csv path/to/labeled.csv \
  --batch_size 32 \
  --epochs 20 \
  --lr 1e-4 \
  --export model_scripted.pt
```

Input CSV must contain: `time, frequency, tstart, tend, fstart, fend, snr, q, amplitude, phase, Channel Name, Label`

### 2. Batch Inference

```bash
omniformer-infer \
  --checkpoint path/to/checkpoint.pt \
  --input_csv path/to/unlabeled.csv \
  --output_csv predictions.csv
```

### 3. Web App

```bash
streamlit run app.py
```

---

## 📲 Python API Example

```python
from omniformer import Omniformer, OmniformerCSVDataset
from torch.utils.data import DataLoader
import torch

dataset = OmniformerCSVDataset("data/labeled.csv")
loader = DataLoader(dataset, batch_size=32, shuffle=True)

model = Omniformer(
    input_dim=10,
    context_dim=dataset.context_dim,
    model_dim=128,
    num_layers=6,
    num_heads=4,
    seq_len=100,
    enable_logging=True,
    device="cuda"
).to("cuda")

optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
criterion = torch.nn.BCEWithLogitsLoss()

for x, ctx, y in loader:
    x, ctx, y = x.to("cuda"), ctx.to("cuda"), y.to("cuda")
    optimizer.zero_grad()
    logits = model(x, ctx).squeeze(1)
    loss = criterion(logits, y)
    loss.backward()
    optimizer.step()
```

---

## 📑 Citation

> Parmar, S. *"Omniformer: Context-aware HyperTransformer for Gravitational-Wave Trigger Classification,"* preprint, 2025.

---

## 📅 License

MIT License. See [LICENSE](LICENSE) for details.

---

## 🔗 Resources

* GitHub: [https://github.com/yourusername/omniformer](https://github.com/yourusername/omniformer)
* PyPI: [https://pypi.org/project/omniformer](https://pypi.org/project/omniformer)

---

## 🙏 Acknowledgements

* **LIGO Open Science Center (GWOSC)**
* **OMICRON Developers**
* **Gravitational Wave Research Community**
* **Meta-Learning & Transformer Researchers**
* **Academic Mentors and Collaborators**
