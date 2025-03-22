import streamlit as st
import pandas as pd
import fitz  # PyMuPDF for PDF text extraction
import json
import matplotlib.pyplot as plt
from faker import Faker
import random
from fpdf import FPDF
from google.generativeai import configure, GenerativeModel

# Configure Gemini API Key
GEMINI_API_KEY = "AIzaSyCCkjNjyD8AzU119dSbCSlu4aEoRr6Z05o"
configure(api_key=GEMINI_API_KEY)

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text

# Streamlit App
st.title("Financial Data Extraction & Insights")

uploaded_file = st.file_uploader("Upload Annual Report PDF", type="pdf")

if uploaded_file:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.read())
    
    text = extract_text_from_pdf("temp.pdf")
    extracted_data = {"financial_text": text}
    
    json_data = json.dumps(extracted_data, indent=4)
    st.subheader("Extracted Data in JSON Format")
    st.json(json_data)
    
    with open("financial_data.json", "w") as json_file:
        json_file.write(json_data)
    
    st.download_button("Download JSON Data", data=json_data, file_name="financial_data.json")
    
# Generate Fake Data for Visualization
faker = Faker()
fake_data = {
    "current_assets": random.uniform(100000, 500000),
    "current_liabilities": random.uniform(50000, 250000),
    "cash_equivalents": random.uniform(20000, 150000),
    "total_liabilities": random.uniform(100000, 500000),
    "shareholder_equity": random.uniform(50000, 300000),
    "total_assets": random.uniform(200000, 800000),
    "operating_income": random.uniform(50000, 200000),
    "interest_expenses": random.uniform(10000, 50000),
    "net_sales": random.uniform(300000, 900000),
    "cogs": random.uniform(100000, 500000),
    "net_income": random.uniform(20000, 100000),
    "average_inventory": random.uniform(50000, 150000),
    "average_accounts_receivable": random.uniform(30000, 120000)
}

# Compute Financial Ratios
ratios = {
    "Current Ratio": fake_data["current_assets"] / fake_data["current_liabilities"],
    "Cash Ratio": fake_data["cash_equivalents"] / fake_data["current_liabilities"],
    "Debt to Equity Ratio": fake_data["total_liabilities"] / fake_data["shareholder_equity"],
    "Debt Ratio": fake_data["total_liabilities"] / fake_data["total_assets"],
    "Interest Coverage Ratio": fake_data["operating_income"] / fake_data["interest_expenses"],
    "Asset Turnover Ratio": fake_data["net_sales"] / fake_data["total_assets"],
    "Inventory Turnover Ratio": fake_data["cogs"] / fake_data["average_inventory"],
    "Receivables Turnover Ratio": fake_data["net_sales"] / fake_data["average_accounts_receivable"],
    "Gross Margin Ratio": (fake_data["net_sales"] - fake_data["cogs"]) / fake_data["net_sales"],
    "Operating Margin Ratio": fake_data["operating_income"] / fake_data["net_sales"],
    "Return on Assets (ROA)": fake_data["net_income"] / fake_data["total_assets"],
    "Return on Equity (ROE)": fake_data["net_income"] / fake_data["shareholder_equity"],
}

st.subheader("Financial Ratios")
df_ratios = pd.DataFrame(ratios.items(), columns=["Metric", "Value"])
st.table(df_ratios)

# Generate Graphs
st.subheader("Financial Visualizations")
fig, ax = plt.subplots()
ax.bar(ratios.keys(), ratios.values(), color='blue')
plt.xticks(rotation=45, ha='right')
plt.ylabel("Ratio Value")
st.pyplot(fig)

# Generate Insights using Gemini API
model = GenerativeModel("gemini-pro")
response = model.generate_content(f"""Analyze the following financial ratios: {ratios}. 
Provide three key insights and recommendations.""")
insights = response.text

st.subheader("AI-Generated Insights")
st.write(insights)

# Generate Final Report in PDF
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Arial", style='B', size=16)
pdf.cell(200, 10, "Financial Report", ln=True, align='C')

pdf.set_font("Arial", size=12)
pdf.cell(200, 10, "Extracted Financial Ratios:", ln=True)
for key, value in ratios.items():
    pdf.cell(200, 10, f"{key}: {value:.2f}", ln=True)

pdf.cell(200, 10, "\nAI-Generated Insights:", ln=True)
pdf.multi_cell(0, 10, insights)

pdf_output = "Financial_Report.pdf"
pdf.output(pdf_output)
st.download_button("Download Financial Report", data=open(pdf_output, "rb"), file_name="Financial_Report.pdf")
