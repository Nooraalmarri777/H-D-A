import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

st.set_page_config(page_title="Health Data Analyzer", layout="wide")

st.title("Health Data Analyzer")

# --- Sidebar ---
st.sidebar.header("Report Options")

# 1- اختيار وقت التقرير
report_type = st.sidebar.selectbox(
    "Select Report Frequency",
    ["Weekly", "Monthly", "Quarterly", "Yearly"]
)

# 2- اختيار نوع التحليل (واحد فقط) مع وصفه
analysis_descriptions = {
    "Summary": "عرض وصف عام للبيانات مثل المتوسط والانحراف المعياري.",
    "Statistical Measures": "تحليل إحصائي متقدم للقيم مثل التباين والمدى والمتوسط.",
    "Trends": "رؤية تغير القيم مع الوقت لاكتشاف الارتفاع أو الانخفاض.",
    "Gaps": "اكتشاف القيم المفقودة في البيانات.",
    "KPIs": "عرض مؤشرات الأداء الرئيسية مثل المتوسط والحد الأقصى والأدنى."
}

analysis_type = st.sidebar.selectbox(
    "Select Type of Analysis",
    list(analysis_descriptions.keys())
)

st.sidebar.markdown(f"**About this analysis:** {analysis_descriptions[analysis_type]}")

# 3- اختيار الرسم البياني الافتراضي حسب نوع التحليل
default_chart_map = {
    "Summary": "Box",
    "Statistical Measures": "Histogram",
    "Trends": "Line",
    "Gaps": "Bar",
    "KPIs": "Bar"
}

recommended_chart = default_chart_map.get(analysis_type, "Line")

chart_type = st.sidebar.selectbox(
    "Select Chart Type",
    ["Bar", "Line", "Box", "Histogram", "Pie"],
    index=["Bar", "Line", "Box", "Histogram", "Pie"].index(recommended_chart)
)

st.sidebar.caption(f"**Recommended chart for {analysis_type}:** {recommended_chart}")

# --- Main Area ---

uploaded_file = st.file_uploader("Upload your health data file (CSV or Excel)", type=["csv", "xlsx"])

def generate_suggestions(df, analysis_type, columns):
    suggestions = []

    if analysis_type in ["Summary", "Statistical Measures"]:
        for col in columns:
            mean = df[col].mean()
            std = df[col].std()
            if pd.isnull(mean) or pd.isnull(std):
                continue
            if std > mean * 0.5:
                suggestions.append(f"العمود '{col}' لديه تشتت عالي. قد تحتاج إلى تنظيف البيانات أو التحقق من القيم الشاذة.")
            else:
                suggestions.append(f"العمود '{col}' بياناته مستقرة نسبيًا.")

    elif analysis_type == "Trends":
        suggestions.append("تحقق من الاتجاهات الموسمية أو التغيرات المفاجئة في البيانات خلال فترة التقرير.")

    elif analysis_type == "Gaps":
        missing = df[columns].isnull().sum()
        for col in columns:
            if missing[col] > 0:
                suggestions.append(f"يوجد {missing[col]} قيمة مفقودة في '{col}'. يفضل التعامل معها (مثل التعبئة أو الحذف).")
            else:
                suggestions.append(f"العمود '{col}' لا يحتوي على قيم مفقودة.")

    elif analysis_type == "KPIs":
        suggestions.append("راجع مؤشرات الأداء بانتظام وحاول تحسين القيم الدنيا والقصوى حسب الهدف.")

    return suggestions

if uploaded_file:
    try:
        # قراءة الملف حسب الامتداد
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.subheader("Raw Data")
        st.dataframe(df)

        columns = st.multiselect("Select columns for analysis", df.columns.tolist(), default=df.columns.tolist())

        if analysis_type == "Summary":
            st.subheader("Summary Statistics")
            st.write(df[columns].describe())

        elif analysis_type == "Statistical Measures":
            st.subheader("Statistical Measures")
            stats_df = pd.DataFrame({
                "Mean": df[columns].mean(),
                "Median": df[columns].median(),
                "Std Deviation": df[columns].std(),
                "Variance": df[columns].var(),
                "Min": df[columns].min(),
                "Max": df[columns].max(),
                "Range": df[columns].max() - df[columns].min(),
                "IQR": df[columns].quantile(0.75) - df[columns].quantile(0.25)
            })
            st.dataframe(stats_df)

        elif analysis_type == "Trends":
            st.subheader("Trend Visualization")
            time_col = st.selectbox("Select time-related column", df.columns)
            numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
            value_col = st.selectbox("Select value column", numeric_cols)

            df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
            df = df.dropna(subset=[time_col, value_col])

            freq_map = {
                "Weekly": "W",
                "Monthly": "M",
                "Quarterly": "Q",
                "Yearly": "Y"
            }
            freq = freq_map.get(report_type, "M")

            trend_df = df.groupby(pd.Grouper(key=time_col, freq=freq))[value_col].mean().reset_index()
            trend_df = trend_df.sort_values(by=time_col)

            fig = px.line(
                trend_df,
                x=time_col,
                y=value_col,
                title=f"{value_col} Over Time ({report_type})",
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)

            # اقتراحات ذكية للاتجاهات
            trend_values = trend_df[value_col].values
            st.subheader("Smart Suggestions (Trends)")
            if len(trend_values) > 2:
                if all(x < y for x, y in zip(trend_values, trend_values[1:])):
                    st.success(f"{value_col} is steadily increasing.")
                elif all(x > y for x, y in zip(trend_values, trend_values[1:])):
                    st.warning(f"{value_col} is steadily decreasing.")
                else:
                    st.info(f"{value_col} shows fluctuation. Consider investigating seasonal patterns.")
            else:
                st.info("Not enough data points to determine trend.")

        elif analysis_type == "KPIs":
            st.subheader("Key Performance Indicators")
            kpi_col = st.selectbox("Select column for KPI visualization", columns)
            st.metric(label=f"Mean of {kpi_col}", value=round(df[kpi_col].mean(), 2))
            st.metric(label=f"Max of {kpi_col}", value=round(df[kpi_col].max(), 2))
            st.metric(label=f"Min of {kpi_col}", value=round(df[kpi_col].min(), 2))

        elif analysis_type == "Gaps":
            st.subheader("Missing Values and Gaps")
            st.write(df[columns].isnull().sum())

        # رسم بياني مخصص
        st.subheader("Custom Chart")
        x_col = st.selectbox("X-axis", columns, key="xcol")
        y_col = st.selectbox("Y-axis", columns, key="ycol")
        title = st.text_input("Chart Title", "Custom Chart")
        color = st.color_picker("Chart Color", "#69b3a2")

        fig, ax = plt.subplots(figsize=(8,4))

        if chart_type == "Bar":
            ax.bar(df[x_col], df[y_col], color=color)
        elif chart_type == "Line":
            ax.plot(df[x_col], df[y_col], color=color)
        elif chart_type == "Box":
            sns.boxplot(x=df[x_col], y=df[y_col], color=color, ax=ax)
        elif chart_type == "Histogram":
            ax.hist(df[y_col], bins=20, color=color)
        elif chart_type == "Pie":
            pie_data = df[y_col].value_counts()
            ax.pie(pie_data, labels=pie_data.index, colors=[color]*len(pie_data), autopct="%1.1f%%")

        ax.set_title(title)
        st.pyplot(fig)

        # عرض الاقتراحات الذكية بعد التحليل (إذا لم تكن Trends لأنه عرضت فوق)
        if analysis_type != "Trends":
            st.subheader("Smart Suggestions / Recommendations")
            suggestions = generate_suggestions(df, analysis_type, columns)
            for sug in suggestions:
                st.info(sug)

    except Exception as e:
        st.error(f"Error processing file: {e}")

else:
    st.info("Please upload a CSV or Excel file to get started.")