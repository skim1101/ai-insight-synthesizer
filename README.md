# AI Customer Insight Synthesizer

A lightweight AI-powered tool that transforms raw customer feedback into **actionable product insights** and **roadmap-ready outputs**.

This project demonstrates how generative AI can be applied pragmatically to a core product leadership problem: synthesizing fragmented qualitative feedback into clear themes, risks, and recommended actions with traceability back to source data.

---

## Why This Exists

In many B2B SaaS organizations, customer insight lives in silos:
- Support tickets
- Sales call notes
- NPS verbatims
- Ad-hoc interview transcripts

Manually synthesizing this data is time-consuming, subjective, and hard to operationalize.

This tool shows how a product leader can:
- Reduce synthesis time from hours to minutes
- Improve consistency and clarity of insights
- Maintain transparency by citing source evidence
- Turn qualitative data into decision-ready artifacts

---

## What It Does

1. **Ingests customer feedback** from a CSV file  
   (e.g. support tickets, NPS comments, sales notes)

2. **Clusters feedback into themes** using an LLM
   - Theme name
   - Clear summary
   - Estimated frequency and severity
   - Concrete recommended action

3. **Maintains traceability**
   - Every insight includes citations back to specific source rows

4. **Exports results**
   - Downloadable Markdown report suitable for exec reviews or roadmap discussions

---

## Example Use Cases

- Product leaders preparing roadmap discussions
- PMs synthesizing interview or NPS data
- Leadership teams aligning on top customer pain points
- Early discovery and opportunity sizing

---

## Tech Stack

- **Python 3**
- **Streamlit** for the UI
- **OpenAI API** for language modeling
- **pandas** for data handling
- **pydantic** for structured output validation

The architecture is intentionally simple and transparent, favoring clarity over over-engineering.

---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/skim1101/ai-insight-synthesizer.git
cd ai-insight-synthesizer