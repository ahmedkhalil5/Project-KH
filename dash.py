import streamlit as st
import pandas as pd
import plotly.express as px
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="AD-SHIELD PRO", layout="wide")

# --- 2. إعدادات الـ AI (قراءة من Secrets) ---
# الكود ده بيقرأ المفتاح اللي إنت حطيته في صفحة الإعدادات
try:
    MISTRAL_API_KEY = st.secrets["MISTRAL_API_KEY"]
    client = MistralClient(api_key=MISTRAL_API_KEY)
except:
    st.error("⚠️ يرجى التأكد من إضافة MISTRAL_API_KEY في صفحة Secrets")
    MISTRAL_API_KEY = None

# --- 3. الواجهة الرئيسية ---
st.title("⚡ AD-SHIELD ULTIMATE: WAR ROOM")

# القائمة الجانبية
st.sidebar.header("Performance Planner")
product_price = st.sidebar.number_input("سعر المنتج (EGP/USD)", value=200)
target_roas = st.sidebar.number_input("(Target) المطلوب ROAS الـ", value=5.0)

# حساب الـ Target CPA تلقائياً
target_cpa = product_price / target_roas
st.sidebar.info(f"🎯 Target CPA: {target_cpa:.2f}")

uploaded_file = st.sidebar.file_uploader("📂 Drop Your Ads CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = [c.strip().lower() for c in df.columns]
    
    try:
        # تعريف الأعمدة بشكل صحيح لتجنب الـ NameError
        spend_col = [c for c in df.columns if "spent" in c or "cost" in c][0]
        name_col = [c for c in df.columns if "campaign" in c][0]
        clicks_col = [c for c in df.columns if "clicks" in c][0]
        imp_col = [c for c in df.columns if "impressions" in c or "imp" in c][0]
        roas_col = [c for c in df.columns if "roas" in c or "return" in c][0]
        
        # حساب الـ CTR والـ CPA لكل حملة
        df['ctr'] = (df[clicks_col] / df[imp_col].replace(0, 1)) * 100
        # لنفترض أن عمود النتائج موجود (purchases)
        results_col = [c for c in df.columns if "purchase" in c or "result" in c][0]
        df['cpa'] = df[spend_col] / df[results_col].replace(0, 1)

        # التبديل بين الأوضاع (Operational Mode)
        mode = st.radio("OPERATIONAL MODE", ["Intelligence & Scaling", "Creative Lab (AI Copywriter)"], horizontal=True)

        if mode == "Intelligence & Scaling":
            # عرض الأرقام الأساسية (War Room Metrics)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Total Spend", f"${df[spend_col].sum():,.0f}")
            with c2:
                st.metric("Avg ROAS", f"{df[roas_col].mean():.2f}x")
            with c3:
                st.metric("Avg CTR", f"{df['ctr'].mean():.2f}%")

            # قسم قرارات التوسع (Scaling Decisions)
            st.header("🚀 Scaling Decisions (توصيات التوسع)")
            col_s, col_k = st.columns(2)
            
            with col_s:
                st.success("✅ Scale These (الحملات الكسبانة)")
                winners = df[df[roas_col] >= target_roas]
                for _, row in winners.iterrows():
                    st.write(f"🚀 **{row[name_col]}**")
                    st.write(f"ROAS: {row[roas_col]:.2f} | التوصية: زود الميزانية 20% كل 48 ساعة")

            with col_k:
                st.error("🛑 Kill/Optimize (الحملات الخسرانة)")
                losers = df[df[roas_col] < target_roas]
                for _, row in losers.iterrows():
                    st.write(f"💀 **{row[name_col]}**")
                    st.write(f"ROAS: {row[roas_col]:.2f} | التوصية: وقف الحملة فوراً أو غير الكرييتف")

        elif mode == "Creative Lab (AI Copywriter)":
            st.header("🎨 Creative Lab")
            if MISTRAL_API_KEY:
                prod_name = st.text_input("اسم المنتج أو الخدمة")
                if st.button("Generate Ad Copy"):
                    messages = [ChatMessage(role="user", content=f"اكتب إعلان فيسبوك جذاب لمنتج {prod_name}")]
                    response = client.chat(model="mistral-tiny", messages=messages)
                    st.success(response.choices[0].message.content)
            else:
                st.warning("الـ AI غير مفعّل، تأكد من الـ API Key")

    except Exception as e:
        st.error(f"⚠️ خطأ في معالجة البيانات: {e}")
