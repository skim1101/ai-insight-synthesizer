import os
import json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("Missing OPENAI_API_KEY. Create a .env file with OPENAI_API_KEY=... and restart the app.")
    st.stop()

client = OpenAI(api_key=api_key)

st.set_page_config(page_title="AI Insight Synthesizer", layout="wide")
st.title("AI Customer Insight Synthesizer (MVP)")

st.write("Upload customer feedback (CSV). Get themes, severity, frequency, and recommended actions with citations.")

# ---------- Data models ----------
class Theme(BaseModel):
    theme: str = Field(description="Short theme name")
    summary: str = Field(description="1-2 sentence description of the theme")
    frequency: str = Field(description="Estimate: Low/Medium/High")
    severity: str = Field(description="Estimate: Low/Medium/High")
    recommended_action: str = Field(description="Concrete recommendation")
    cited_row_ids: List[int] = Field(description="Row IDs from the uploaded CSV that support this theme")

class AnalysisResult(BaseModel):
    themes: List[Theme]

# ---------- UI ----------
uploaded = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded)
    st.subheader("Preview")
    st.dataframe(df.head(20), use_container_width=True)

    text_col = st.selectbox("Which column contains the customer feedback text?", df.columns.tolist())
    max_rows = st.slider("How many rows to analyze (start small)", min_value=5, max_value=50, value=15)

    if st.button("Analyze with AI"):
        with st.spinner("Analyzing..."):
            sample = df.head(max_rows).copy()
            sample["__row_id"] = sample.index.astype(int)

            # Build a compact input payload with row ids
            records = []
            for _, r in sample.iterrows():
                records.append({
                    "row_id": int(r["__row_id"]),
                    "text": str(r[text_col])[:2000]
                })

            system = (
                "You are a product leader. Your job is to synthesize customer feedback into actionable product insights. "
                "Be specific and avoid generic advice. Every theme must include citations to row_id values."
            )

            user = {
                "task": "Cluster the feedback into 3-7 themes. For each theme: name, summary, frequency, severity, recommended_action, cited_row_ids.",
                "feedback": records
            }

            resp = client.responses.create(
                model="gpt-4o-mini",
                input=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": json.dumps(user)},
                    {
                        "role": "user",
                        "content": (
                            "Return ONLY valid JSON. No markdown, no commentary. "
                            "Schema: {\"themes\": [{\"theme\": \"\", \"summary\": \"\", "
                            "\"frequency\": \"Low|Medium|High\", \"severity\": \"Low|Medium|High\", "
                            "\"recommended_action\": \"\", \"cited_row_ids\": [0]}]}. "
                            "cited_row_ids must be real row_id integers from the input."
                        ),
                    },
                ],
            )

            raw = resp.output_text.strip()

            # Try to parse JSON, and auto-repair once if needed
            try:
                out = json.loads(raw)
            except json.JSONDecodeError:
                repair = client.responses.create(
                    model="gpt-4o-mini",
                    input=[
                        {"role": "system", "content": "Fix JSON."},
                        {"role": "user", "content": "Repair this into valid JSON only:\n" + raw},
                    ],
                )
                out = json.loads(repair.output_text)

            result = AnalysisResult(**out)

        st.success("Done")

        st.subheader("Themes")
        for t in result.themes:
            with st.expander(f"{t.theme} (Freq: {t.frequency}, Sev: {t.severity})", expanded=True):
                st.write(t.summary)
                st.markdown(f"**Recommended action:** {t.recommended_action}")

                cited = df.loc[t.cited_row_ids, [text_col]].copy()
                cited["row_id"] = cited.index
                st.markdown("**Citations:**")
                st.dataframe(cited[["row_id", text_col]], use_container_width=True)

        # Export markdown
        md_lines = ["# AI Insight Synthesizer Output\n"]
        for t in result.themes:
            md_lines.append(f"## {t.theme}")
            md_lines.append(f"- Summary: {t.summary}")
            md_lines.append(f"- Frequency: {t.frequency}")
            md_lines.append(f"- Severity: {t.severity}")
            md_lines.append(f"- Recommended action: {t.recommended_action}")
            md_lines.append(f"- Cited rows: {', '.join(map(str, t.cited_row_ids))}\n")

        md = "\n".join(md_lines)
        st.download_button("Download Markdown Report", md, file_name="insights_report.md")
else:
    st.info("Upload a CSV to begin.")
    
