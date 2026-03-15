import streamlit as st
import pandas as pd
import plotly.express as px
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage


# --- 1. إعدادات النظام ---
st.set_page_config(page_title="AD-SHIELD PRO: MULTI-CURRENCY", layout="wide")


# --- 2. إعدادات AI ---
MISTRAL_API_KEY = "GQgcXZycQirade3Mk7ZN8C6yof7gykiD"


# --- 3. التصميم (Style) ---
st.markdown("""
<style>
    .stApp { background-color: #040509; color: #e0e6ed; }
    .metric-card {
        background: rgba(0, 242, 254, 0.05);
        border: 1px solid #00f2fe;
        padding: 20px; border-radius: 12px; text-align: center;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.1);
    }
    .scale-card { border-right: 5px solid #10b981; background: rgba(16, 185, 129, 0.1); padding: 15px; margin: 10px 0; border-radius: 8px; direction: rtl; }
    .kill-card { border-right: 5px solid #ef4444; background: rgba(239, 68, 68, 0.1); padding: 15px; margin: 10px 0; border-radius: 8px; direction: rtl; }
</style>
""", unsafe_allow_html=True)


# --- 4. الشريط الجانبي (التخصيص الكامل) ---
st.sidebar.header("⚙️ Dashboard Settings")


# أ) اختيار العملة
currency = st.sidebar.selectbox("اختر العملة (Currency)", ["EGP", "SAR", "AED", "USD", "KWD"])


# ب) اختيار الهدف الأساسي للعرض في الكروت
display_metric = st.sidebar.selectbox("اختر الرقم المراد عرضه في الواجهة",
    ["Purchase ROAS", "Checkouts", "Add to Cart (ATC)", "Leads", "Cost Per Result"])


# ج) مدخلات الحاسبة
product_price = st.sidebar.number_input(f"سعر المنتج ({currency})", value=200)
target_goal_val = st.sidebar.number_input(f"الهدف المطلوب (Target {display_metric})", value=5.0)


# --- 5. الواجهة الرئيسية ---
st.title("⚡ AD-SHIELD")
tabs = st.radio("OPERATIONAL MODE", ["📊 Dashboard", "🚀 Scaling Control", "🎨 Creative AI"], horizontal=True)


uploaded_file = st.sidebar.file_uploader("📂 Drop Your Ads CSV", type="csv")


if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = [c.strip().lower() for c in df.columns]
   
    try:
        # البحث الديناميكي عن الأعمدة
        spend_col = [c for c in df.columns if "spent" in c or "cost" in c][0]
        name_col = [c for c in df.columns if "campaign" in c][0]
        clicks_col = [c for c in df.columns if "clicks" in c][0]
        imp_col = [c for c in df.columns if "impressions" in c][0]
       
        # تحديد عمود الأداء بناءً على اختيار المستخدم
        if "roas" in display_metric.lower():
            perf_col = [c for c in df.columns if "roas" in c or "return" in c][0]
        elif "checkout" in display_metric.lower():
            perf_col = [c for c in df.columns if "checkout" in c][0]
        elif "cart" in display_metric.lower():
            perf_col = [c for c in df.columns if "cart" in c or "atc" in c][0]
        else:
            perf_col = [c for c in df.columns if "result" in c or "lead" in c][0]


        df['ctr'] = (df[clicks_col] / df[imp_col].replace(0, 1)) * 100
       
    except Exception as e:
        st.error(f"خطأ في قراءة الأعمدة: تأكد أن الملف يحتوي على بيانات {display_metric}")
        st.stop()


    # --- TAB 1: Dashboard ---
    if tabs == "📊 Dashboard":
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="metric-card"><h4>إجمالي الصرف</h4><h2>{currency} {df[spend_col].sum():,.0f}</h2></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><h4>متوسط {display_metric}</h4><h2>{df[perf_col].mean():.2f}</h2></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card"><h4>متوسط الـ CTR</h4><h2>{df["ctr"].mean():.2f}%</h2></div>', unsafe_allow_html=True)
       
        st.subheader(f"تحليل أداء {display_metric} لكل حملة")
        fig = px.bar(df, x=name_col, y=perf_col, color=perf_col, template="plotly_dark")
        fig.add_hline(y=target_goal_val, line_dash="dot", line_color="#00f2fe", annotation_text="Target")
        st.plotly_chart(fig, use_container_width=True)


    # --- TAB 2: Scaling Control ---
    elif tabs == "🚀 Scaling Control":
        st.header(f"توصيات بناءً على هدف: {display_metric}")
       
        # أزرار التحميل
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button("📥 تحميل التقرير CSV", df.to_csv(index=False).encode('utf-8-sig'), "AdShield_Report.csv", "text/csv")
        with col_dl2:
            st.info("💡 نصيحة: للتحميل PDF، استخدم اختصار (Ctrl+P) واختر Save as PDF لتقرير منسق.")


        col_s, col_k = st.columns(2)
        with col_s:
            st.success("🟢 حملات للتوسع (Scale)")
            for _, r in df[df[perf_col] >= target_goal_val].iterrows():
                st.markdown(f'<div class="scale-card"><b>🚀 {r[name_col]}</b><br>{display_metric}: {r[perf_col]:.2f}<br>التوصية: زود الميزانية 20% فوراً.</div>', unsafe_allow_html=True)
       
        with col_k:
            st.error("🔴 حملات محتاجة تعديل (Kill/Fix)")
            for _, r in df[df[perf_col] < target_goal_val].iterrows():
                st.markdown(f'<div class="kill-card"><b>💀 {r[name_col]}</b><br>{display_metric}: {r[perf_col]:.2f}<br>التوصية: افحص الإعلان أو وقف الحملة.</div>', unsafe_allow_html=True)


    # --- TAB 3: Creative AI ---
    elif tabs == "🎨 Creative AI":
        st.header("توليد إعلانات ذكية")
        lang = st.selectbox("اللغة", ["Egyptian Slang (عامية مصرية)", "Saudi Slang (عامية سعودية)", "English"])
        camp = st.selectbox("اختر الحملة", df[name_col])
        if st.button("Generate Copy ⚡"):
            st.info("الـ AI يقوم بالكتابة بناءً على أهداف " + display_metric + " حالياً...")
            # هنا تستدعي دالة الـ AI اللي عملناها سابقاً


else:
    st.info("يرجى رفع ملف CSV لبدء تشغيل غرفة العمليات.")

