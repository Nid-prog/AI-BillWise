# 🧾 AI BillWise

AI BillWise is an AI-powered receipt and expense assistant that uses Gemini to analyze receipts, extract bill details, split expenses, answer questions about the bill, and send a bill summary by email.

## ✨ Features

* 📷 Upload receipt images
* 🤖 AI-powered receipt analysis using Gemini
* 🏪 Extract store name and date
* 🧾 Extract individual items and prices
* 💰 Extract subtotal, taxes, total, and currency
* 👥 Split the bill between multiple people
* 💬 Ask questions about the receipt using AI
* 📧 Send the bill summary through Gmail
* 🔐 API keys and credentials are protected using Streamlit Secrets

## 🛠️ Technologies Used

* Python
* Streamlit
* Google Gemini API
* Pillow
* Gmail SMTP

## 🚀 How It Works

1. Upload a receipt image.
2. Gemini analyzes the receipt.
3. AI BillWise extracts the store, date, items, prices, taxes, total, and currency.
4. Enter the number of people to split the bill.
5. Ask questions about the receipt.
6. Send the generated bill summary to an email address.

## 📂 Project Structure

```text
AI-BillWise/
│
├── .streamlit/
│   └── secrets.toml.example
├── app.py
├── prompts.py
├── requirements.txt
├── .gitignore
└── README.md
```

## 🔐 Environment Variables / Secrets

The application uses Streamlit Secrets for sensitive information.

Required secrets:

```toml
GEMINI_API_KEY = "your-gemini-api-key"
GMAIL_ADDRESS = "your-gmail-address"
GMAIL_APP_PASSWORD = "your-gmail-app-password"
```

**Never upload your real API key or Gmail App Password to GitHub.**

## ▶️ Run Locally

Clone the repository and install the required packages:

```bash
pip install -r requirements.txt
```

Then run:

```bash
streamlit run app.py
```

## 🌐 Live Demo

**AI BillWise:**
https://ai-billwise-ezdejuqyn5i8uqfompt2se.streamlit.app/

## 👩‍💻 Author

**Nidhi Kante**

Built as an AI-powered receipt and expense assistant project.
