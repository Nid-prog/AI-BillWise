import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
import json
import smtplib
import time
from email.message import EmailMessage


# --------------------------------
# CONNECT TO GEMINI
# --------------------------------

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)


# --------------------------------
# APP TITLE
# --------------------------------

st.title("AI BillWise")
st.write("Your AI-powered receipt and expense assistant")


# --------------------------------
# UPLOAD RECEIPT
# --------------------------------

receipt = st.file_uploader(
    "Upload your receipt",
    type=["jpg", "jpeg", "png"]
)


if receipt:

    # Display receipt
    image = Image.open(receipt)
    st.image(image, caption="Uploaded Receipt")


    # --------------------------------
    # RECEIPT ANALYSIS
    # --------------------------------

    # Analyze only once for the uploaded receipt
    if "receipt_data" not in st.session_state:

        with st.spinner("🔍 Analyzing your receipt..."):

            for attempt in range(3):

                try:

                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=[
                            """
                            Analyze this receipt and return ONLY valid JSON.

                            Use exactly this structure:

                            {
                                "store_name": "store name",
                                "date": "date",
                                "currency": "currency code such as INR, USD, BHD",
                                "items": [
                                    {
                                        "name": "item name",
                                        "price": 0.00
                                    }
                                ],
                                "subtotal": 0.00,
                                "taxes_and_charges": 0.00,
                                "total": 0.00
                            }

                            Important:
                            - Extract the final total amount from the receipt.
                            - Extract the currency used on the receipt.
                            - Keep prices as numbers, not strings.
                            - Do not include any explanation outside the JSON.
                            """,

                            types.Part.from_bytes(
                                data=receipt.getvalue(),
                                mime_type=receipt.type
                            )
                        ]
                    )

                    response_text = response.text.strip()

                    # Remove Markdown code block if Gemini adds it
                    if response_text.startswith("```"):
                        response_text = response_text.replace(
                            "```json", ""
                        )
                        response_text = response_text.replace(
                            "```", ""
                        )
                        response_text = response_text.strip()

                    # Convert JSON to Python
                    receipt_data = json.loads(response_text)

                    # Save result so Gemini doesn't run again
                    # every time Streamlit reruns
                    st.session_state.receipt_data = receipt_data

                    break

                except Exception as e:

                    if attempt < 2:
                        time.sleep(3)
                    else:

                        st.error(
                            "⚠️ Gemini is temporarily unavailable."
                        )

                        st.info(
                            "We tried 3 times. Please wait a little "
                            "and upload the receipt again."
                        )

                        st.stop()


    # Get saved receipt data
    receipt_data = st.session_state.receipt_data


    # --------------------------------
    # RECEIPT DETAILS
    # --------------------------------

    st.subheader("🧾 Receipt Details")

    st.write(
        "**Store:**",
        receipt_data["store_name"]
    )

    st.write(
        "**Date:**",
        receipt_data["date"]
    )

    st.write(
        "**Currency:**",
        receipt_data["currency"]
    )


    # Items
    st.write("### Items")

    for item in receipt_data["items"]:

        st.write(
            f"- {item['name']}: "
            f"{item['price']:.2f} "
            f"{receipt_data['currency']}"
        )


    # Subtotal
    st.write(
        f"**Subtotal:** "
        f"{receipt_data['subtotal']:.2f} "
        f"{receipt_data['currency']}"
    )


    # Taxes
    st.write(
        f"**Taxes & Charges:** "
        f"{receipt_data['taxes_and_charges']:.2f} "
        f"{receipt_data['currency']}"
    )


    # Total
    st.write(
        f"### Total: "
        f"{receipt_data['total']:.2f} "
        f"{receipt_data['currency']}"
    )


    # --------------------------------
    # BILL SPLITTING
    # --------------------------------

    st.subheader("👥 Split the Bill")

    people = st.number_input(
        "How many people are splitting the bill?",
        min_value=1,
        value=2,
        step=1
    )

    total_amount = float(
        receipt_data["total"]
    )

    currency = receipt_data["currency"]

    amount_per_person = (
        total_amount / people
    )

    st.success(
        f"Each person should pay: "
        f"{amount_per_person:.2f} {currency}"
    )


    # --------------------------------
    # AI CHAT
    # --------------------------------

    st.subheader("💬 Ask About Your Bill")

    question = st.text_input(
        "Ask a question about this receipt:"
    )


    if question:

        receipt_context = json.dumps(
            receipt_data,
            indent=2
        )

        chat_prompt = f"""
        You are an AI bill assistant.

        Answer the user's question accurately using ONLY
        the receipt information provided below.

        Important rules:
        - Understand exactly what the user is asking.
        - If the user asks how many items are on the receipt,
          count the items in the "items" list.
        - If the user asks for the most expensive item,
          compare the item prices.
        - If the user asks for the total,
          use the "total" field.
        - If the user asks for the subtotal,
          use the "subtotal" field.
        - Do not answer a different question.
        - Keep the answer short and clear.

        Receipt information:
        {receipt_context}

        User question:
        {question}
        """


        try:

            chat_response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=chat_prompt
            )

            st.write("### 🤖 AI Answer")

            st.write(
                chat_response.text
            )

        except Exception:

            st.error(
                "⚠️ Gemini is temporarily unavailable. "
                "Please try again in a few seconds."
            )


    # --------------------------------
    # SEND BILL SUMMARY BY EMAIL
    # --------------------------------

    st.subheader("📧 Send Bill Summary")

    recipient_email = st.text_input(
        "Enter the email address to send the bill summary:"
    )


    if st.button("📨 Send Bill Summary"):

        if not recipient_email:

            st.warning(
                "Please enter an email address."
            )

        else:

            email = EmailMessage()

            email["Subject"] = (
                "AI BillWise - Bill Summary"
            )

            email["From"] = (
                st.secrets["GMAIL_ADDRESS"]
            )

            email["To"] = recipient_email


            # Create bill summary
            summary = f"""
AI BillWise - Bill Summary

Store: {receipt_data["store_name"]}
Date: {receipt_data["date"]}
Currency: {receipt_data["currency"]}

Items:
"""


            for item in receipt_data["items"]:

                summary += (
                    f"- {item['name']}: "
                    f"{item['price']:.2f} "
                    f"{receipt_data['currency']}\n"
                )


            summary += f"""
Subtotal: {receipt_data["subtotal"]:.2f} {receipt_data["currency"]}
Taxes & Charges: {receipt_data["taxes_and_charges"]:.2f} {receipt_data["currency"]}
Total: {receipt_data["total"]:.2f} {receipt_data["currency"]}

Split among {people} people:
Each person pays {amount_per_person:.2f} {receipt_data["currency"]}

Sent using AI BillWise.
"""


            email.set_content(summary)


            try:

                with smtplib.SMTP_SSL(
                    "smtp.gmail.com",
                    465
                ) as server:

                    server.login(
                        st.secrets["GMAIL_ADDRESS"],
                        st.secrets["GMAIL_APP_PASSWORD"]
                    )

                    server.send_message(email)


                st.success(
                    "✅ Bill summary sent successfully!"
                )


            except Exception as e:

                st.error(
                    "❌ Failed to send email."
                )

                st.write(str(e))