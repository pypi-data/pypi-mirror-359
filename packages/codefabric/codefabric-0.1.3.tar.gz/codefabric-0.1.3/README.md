# 🚀 CodeFabric: AI Code Generation Package

Welcome to **CodeFabric**, your AI-powered coding assistant that generates full projects from plain English! Feed it your idea, and it crafts clean code like a digital artisan 🧙‍♂️—powered by LangGraph for agentic reasoning and execution.

> ⚠️ **Before You Start:**
> If you are using CLI version, you **must set your OpenAI API key** in your environment variables or `.env` file as:
> `OPENAI_API_KEY=your_openai_api_key_here`

---

## Features 🌟

* 🧑‍💻 **Interactive CLI** with beautiful UI (Rich-based) to generate projects quickly
* 🔁 **Programmatic API** for power users and automation
* 🧠 **LLM-driven reasoning**, powered by LangGraph
* ⚙️ **Supports multiple technologies** via the `Technologies` enum
* 🧩 **Pluggable LLM** support (use OpenAI or your custom one)
* 📦 **Auto setup** with logging and task breakdowns

---

## Prerequisites 🛠️

* Python 3.8+
* `pip` installed
* Project-specific tools (Node.js for JS projects, etc.)
* Set `OPENAI_API_KEY` in your environment or `.env` file

---

## 📦 Installation

```bash
pip install codefabric
```

---

## 🖥️ Option 1: CLI (Recommended)

Launch the interactive CLI to generate a full-stack project with guided input:

```bash
codefabric
```

You'll be prompted to:

* 📝 Enter project name
* 💡 Describe what the project does
* 💻 Choose a technology stack (e.g., Python, Node.js, etc.)
* ✅ Confirm creation

Once confirmed, CodeFabric will automatically generate your full project folder based on your inputs using LangGraph-powered AI agents.

> Example CLI Output:

```
📝 Project Name: portfolio-app
💡 Description: A personal portfolio site with blog and contact form
💻 Technology: Next.js
```

Your project will be generated and saved into `portfolio-app-any/`. Logs are printed during generation.

---

## 🧠 Option 2: Programmatic API Usage

You can use CodeFabric inside your own Python script for advanced or automated workflows:

```python
from codefabric.graph.developer_agent import DeveloperAgent
from codefabric.types.models import Requirements
from codefabric.types.enums import Technologies

process_id = "leetcode-agent"
project_description = """Build a python AI agent that takes LeetCode DSA questions, identifies patterns, explains how to solve, and builds a Streamlit app."""

dev_agent = DeveloperAgent(
    process_id=process_id,
    requirements=Requirements(
        project_name="leetcode-agent",
        project_description=project_description,
        packages=[],
        technology=Technologies.PYTHON.value,
    ),
)

dev_agent.run()
```

Run it:

```bash
python run_agent.py
```

---

## 🔑 Setting Up API Key

To use OpenAI models, add your key to a `.env` file:

```
OPENAI_API_KEY=your_openai_api_key_here
```

Or set it in your shell:

```bash
export OPENAI_API_KEY=your_openai_api_key_here
```

---

## 🗺️ Project Flow

Here’s how CodeFabric works internally:

1. Parses your idea into structured requirements
2. Constructs LangGraph agent flow
3. Generates folder structure, code files, and dependencies
4. Final project is ready-to-run 🚀

![CodeFabric Flow](developer_graph.png)

---

## 🐞 Troubleshooting

* `ModuleNotFoundError`? → Run `pip install codefabric`
* `OPENAI_API_KEY` error? → Set it in your environment or `.env`
* Still stuck? → Check terminal logs

---

## 🤝 Contributing

Pull requests welcome! Fork the repo, make your changes, and help improve CodeFabric.

---

## 📜 License

MIT License.
Use freely, build responsibly. Don’t unleash rogue AI without giving us a high-five. 🤖✋

---

Happy coding!
✨ May your agents be smart, and your bugs be few.
