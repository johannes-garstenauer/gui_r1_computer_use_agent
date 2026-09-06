# GUI-R1 Computer Use Agent

A lightweight Python execution loop for the **GUI-R1** vision-language model. 

This repository provides a direct bridge between the GUI-R1 model and your operating system. At its core, it runs a continuous chat loop that captures your screen, feeds the state to the model for reasoning, and executes the resulting GUI actions (clicks, typing, scrolling) to complete user-defined tasks.

---

## 🚀 Quickstart

Clone the repository and set up your environment:

```bash
git clone [https://github.com/johannes-garstenauer/gui_r1_computer_use_agent.git](https://github.com/johannes-garstenauer/gui_r1_computer_use_agent.git)
cd gui_r1_computer_use_agent

# Set up your virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

---

## ⚙️ Configuration

Copy the example environment file and configure it to point to your API endpoint (e.g., vLLM, Ollama, or an OpenAI-compatible server):

```bash
cp .env.example .env
```

```env
MODEL_BASE_URL="http://localhost:8000/v1"
MODEL_NAME="gui-r1-7b"
API_KEY="sk-..."
```

---

## 💻 Usage

Start the agent by passing your instruction to the main script:

```bash
python main.py --instruction "Open the browser, go to YouTube, and search for guitar tutorials."
```

**⚠️ Safety Failsafe:** Because this script allows the model to actively control your mouse and keyboard, a standard PyAutoGUI failsafe is active. Move your physical mouse to any of the four corners of your screen to immediately abort execution, or press `Ctrl+C` in the terminal.

---

## 📚 Original Paper

This project serves as an interface for the GUI-R1 model. For full details on the underlying model architecture, multimodal grounding, and reinforcement fine-tuning methodology, refer to the original publication:

> **GUI-R1: A Generalist R1-Style Vision-Language Action Model For GUI Agents**  
> Run Luo, Lu Wang, Wanwei He, Longze Chen, Jiaming Li, Xiaobo Xia (2025)  
> 🔗 [arXiv:2504.10458](https://arxiv.org/abs/2504.10458)

---

## 📄 License

Distributed under the [MIT License](LICENSE).
