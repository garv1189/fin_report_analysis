import streamlit as st
import pdfplumber
import fitz  # PyMuPDF
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import os
import requests
from dotenv import load_dotenv
from fpdf import FPDF

# Load API keys from .env file
load_dotenv()
LLAMA_API_KEY = os.getenv("87379a27-6004-47a1-837c-d9460485bf68")
LLAMA_API_URL = "https://api.llama.com/v1/chat/completions"

def extract_text_from_pdf(pdf_file):
    """Extract text from the uploaded PDF file."""
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_tables_from_pdf(pdf_file):
    """Extract tables from the PDF as dataframes."""
    dfs = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                df = pd.DataFrame(table[1:], columns=table[0])
                dfs.append(df)
    return dfs

def call_llama_api(prompt):
    """Call Llama 3 API for financial insights and analysis."""
    headers = {"Authorization": f"Bearer {LLAMA_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama-3", "messages": [{"role": "user", "content": prompt}], "max_tokens": 500}
    response = requests.post(LLAMA_API_URL, headers=headers, json=payload)
    return response.json()["choices"][0]["message"]["content"]

def generate_financial_insights(text):
    """Generate 5 key financial insights."""
    prompt = f"Extract and summarize 5 key financial insights from the following annual report:\n{text[:4000]}"
    return call_llama_api(prompt)

def calculate_financial_ratios(df):
    """Calculate key financial ratios from extracted tables."""
    ratios = {}
    try:
        total_assets = df[df.columns[1]].astype(float).sum()
        total_liabilities = df[df.columns[2]].astype(float).sum()
        revenue = df[df.columns[3]].astype(float).sum()
        profit = df[df.columns[4]].astype(float).sum()

        ratios["Debt-to-Equity Ratio"] = round(total_liabilities / (total_assets - total_liabilities), 2)
        ratios["Profit Margin"] = round((profit / revenue) * 100, 2)
        ratios["Return on Assets (ROA)"] = round((profit / total_assets) * 100, 2)
    except Exception as e:
        st.error(f"Error calculating ratios: {e}")
    return ratios

def generate_visualizations(df):
    """Create 5 financial visualizations."""
    st.subheader("📊 Financial Visualizations")
    fig1 = px.line(df, x=df.columns[0], y=df.columns[3], title="Revenue Trend Over Time")
    st.plotly_chart(fig1)
    fig2 = px.bar(df, x=df.columns[0], y=df.columns[4], title="Profit Comparison")
    st.plotly_chart(fig2)
    fig3 = px.pie(df, names=df.columns[1], values=df.columns[2], title="Assets vs. Liabilities")
    st.plotly_chart(fig3)
    fig4 = px.scatter(df, x=df.columns[3], y=df.columns[4], title="Revenue vs. Profit")
    st.plotly_chart(fig4)
    fig5 = px.area(df, x=df.columns[0], y=df.columns[2], title="Liabilities Growth Over Time")
    st.plotly_chart(fig5)

def generate_analytics(text):
    """Generate 5 deep-dive analytics from the financial report."""
    prompt = f"Analyze this financial report and provide 5 detailed financial analytics insights:\n{text[:4000]}"
    return call_llama_api(prompt)

def generate_pdf_report(insights, ratios, analytics):
    """Generate a printable PDF report."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, "Financial Report Summary", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Key Insights:", ln=True)
    for insight in insights.split('\n'):
        pdf.cell(0, 10, f"- {insight}", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, "Financial Ratios:", ln=True)
    for key, value in ratios.items():
        pdf.cell(0, 10, f"{key}: {value}", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, "Advanced Analytics:", ln=True)
    for analytic in analytics.split('\n'):
        pdf.cell(0, 10, f"- {analytic}", ln=True)
    pdf_file = "financial_report.pdf"
    pdf.output(pdf_file)
    return pdf_file

def main():
    st.title("📊 AI-Powered Financial Report Analyzer")
    uploaded_file = st.file_uploader("Upload Annual Financial Report (PDF)", type=["pdf"])
    if uploaded_file:
        text = extract_text_from_pdf(uploaded_file)
        dfs = extract_tables_from_pdf(uploaded_file)
        
        with st.spinner("Analyzing Report with Llama 3..."):
            insights = generate_financial_insights(text)
            st.subheader("📢 Key Financial Insights")
            st.write(insights)
        
        st.subheader("📈 Financial Data Visualization")
        for df in dfs:
            st.dataframe(df)
            generate_visualizations(df)
            ratios = calculate_financial_ratios(df)
            st.subheader("📊 Key Financial Ratios")
            st.write(ratios)
        
        with st.spinner("Generating Advanced Analytics..."):
            analytics = generate_analytics(text)
            st.subheader("📑 Financial Analytics")
            st.write(analytics)
        
        with st.spinner("Generating Printable Report..."):
            pdf_file = generate_pdf_report(insights, ratios, analytics)
            st.download_button(label="📥 Download Report", data=open(pdf_file, "rb").read(), file_name=pdf_file, mime="application/pdf")
        
        st.success("✅ Analysis Complete!")

if __name__ == "__main__":
    main()
