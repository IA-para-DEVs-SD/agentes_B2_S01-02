# 🤖 Customer Interaction Summarizer (Kiro Demo)

This project demonstrates the evolution from **Assistant → Workflow → Agent**, using a simple and realistic use case: summarizing customer interactions.

---

## 🎯 Objective

Automatically generate a structured summary (`summary.json`) from customer interactions (`interactions.txt`), using:

* Python script
* Environment variables (`.env`)
* Kiro hook for automation

---

## 🧱 Project Structure

```
.
├── .env
├── .gitignore
├── requirements.txt
├── summarize.py
├── interactions.txt
├── summary.json
├── .venv/
└── .kiro/
    └── hooks/
        └── update-summary.kiro.hook
```

---

## ⚙️ Setup

### 1. Create virtual environment

```bash
python -m venv .venv
```

Activate:

**Mac/Linux**

```bash
source .venv/bin/activate
```

**Windows**

```bash
.venv\Scripts\activate
```

---

### 2. Install dependencies

```bash
pip install python-dotenv
```


```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file:

```env
SUMMARY_MAX_POINTS=4
SUMMARY_SENTIMENT=true
SUMMARY_PRIORITY_RULES=true
```

These variables control the behavior of the summarization logic.

---

## ▶️ Run manually

```bash
python summarize.py
```

This will generate/update:

```
summary.json
```

---

## ⚡ Automation with Kiro Hook

The hook automatically runs the summarization when `interactions.txt` is saved.

### Hook location

```
.kiro/hooks/update-summary.kiro.hook
```

### Example

```json
{
  "name": "Update Summary On Save",
  "description": "Run summarize.py whenever interactions.txt is saved.",
  "version": "1",
  "when": {
    "type": "fileSaved",
    "patterns": ["interactions.txt"]
  },
  "then": {
    "type": "runCommand",
    "command": "python summarize.py"
  }
}
```

---

## 🧠 How This Demonstrates AI Systems

### 🟢 Assistant

Manual prompt:

> “Summarize interactions.txt”

* Reactive
* No structure
* No persistence

---

### 🟡 Workflow

Hook + script:

* Trigger: file save
* Deterministic steps
* Structured output (JSON)

---

### 🔴 Agent (Next Step)

To evolve into an agent:

* Compare previous vs new summary
* Decide whether to update
* Detect escalation
* Trigger additional actions

---

## 🧪 Example Input

```
Cliente: Meu pedido não chegou
Cliente: Já faz 5 dias
Cliente: Preciso de ajuda
Agente: Estamos verificando
Cliente: Ainda não resolveram
Cliente: Quero cancelar
```

---

## 📤 Example Output

```json
{
  "key_points": [
    "Meu pedido não chegou.",
    "Já faz 5 dias.",
    "Preciso de ajuda.",
    "Ainda não resolveram."
  ],
  "action_needed": "Verificar status do pedido e responder ao cliente.",
  "sentiment": "negative",
  "priority": "urgent"
}
```

---

## 🔁 Experiment

Change `.env`:

```env
SUMMARY_MAX_POINTS=2
```

Save `interactions.txt` again → observe output change.

---

## 💡 Key Takeaways

* AI alone ≠ system
* Workflows bring **structure and consistency**
* Agents add **decision and autonomy**
* Environment variables enable **configurable behavior**
* Hooks enable **automation triggered by events**

---

## 🚀 Next Steps

* Add memory (store previous summaries)
* Add validation layer
* Integrate external APIs
* Implement agent decision loop (ReAct / Planner)

---

## 📌 Notes

* `.env` should not be committed
* `.venv/` is local only
* `summary.json` is generated

---

## 🧠 Teaching Insight

This project is designed to show that:

> The same problem can evolve from a simple prompt to an intelligent system.
