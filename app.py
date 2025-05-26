import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

st.set_page_config(page_title="Health Data Analyzer", layout="wide")
st.title("Health Data Analyzer")

# ========== Sidebar - خيارات التقرير ==========
st.sidebar.header("Report Options")
report_type = st.sidebar.selectbox("Select Report Type", ["Weekly", "Monthly", "Quarterly", "Yearly"])

# أوصاف التحليل
analysis_descriptions = {
    "Summary": "عرض وصف عام للبيانات مثل المتوسط والانحراف المعياري.",
    "Statistical Measures": "تحليل إحصائي متقدم للقيم مثل التباين والمدى والمتوسط.",
    "Trends": "رؤية تغير القيم مع الوقت لاكتشاف الارتفاع أو الانخفاض.",
    "Gaps": "اكتشاف القيم المفقودة في البيانات.",
    "KPIs": "عرض مؤشرات الأداء الرئيسية مثل المتوسط والحد الأقصى والأدنى."
}

# اختيار نوع التحليل
analysis_type = st.sidebar.multiselect(
    "Select Type of Analysis",
    ["Summary", "Statistical Measures", "Trends", "Gaps", "KPIs"]
)

# عرض وصف التحليل الأول
if analysis_type:
    selected = analysis_type[0]
    st.sidebar.markdown(f"**About this analysis:** {analysis_descriptions[selected]}")

# اقتراح الرسم البياني حسب نوع التحليل
default_chart_map = {
    "Summary": "Box",
    "Statistical Measures": "Histogram",
    "Trends": "Line",
    "Gaps": "Bar",
    "KPIs": "Bar"
}
default_analysis = analysis_type[0] if analysis_type else "Summary"
recommended_chart = default_chart_map.get(default_analysis, "Line")

chart_type = st.sidebar.selectbox(
    "Select Chart Type",
    ["Bar", "Line", "Box", "Histogram", "Pie"],
    index=["Bar", "Line", "Box", "Histogram", "Pie"].index(recommended_chart)
)
st.sidebar.caption(f"**Recommended chart for {default_analysis}:** {recommended_chart}")

# ========== رفع الملف ==========
uploaded_file = st.file_uploader("Upload your health data file (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.subheader("Raw Data")
        st.dataframe(df)

        columns = st.multiselect("Select columns for analysis", df.columns.tolist(), default=df.columns.tolist())

        # ========== Summary ==========
        if "Summary" in analysis_type:
            st.subheader("Summary Statistics")
            st.write(df[columns].describe())

        # ========== Statistical Measures ==========
        if "Statistical Measures" in analysis_type:
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

        # ========== Trends ==========
        if "Trends" in analysis_type:
            st.subheader("Trend Visualization")

            time_col = st.selectbox("Select time column", df.columns)
            value_col = st.selectbox("Select value column", df.select_dtypes(include=np.number).columns.tolist())

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

            st.session_state["trend"] = trend_df  # حفظ مؤقت

            fig = px.line(
                trend_df,
                x=time_col,
                y=value_col,
                title=f"{value_col} Over Time ({report_type})",
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)

            # اقتراحات ذكية
            st.subheader("Smart Suggestions (Trends)")
            trend_values = trend_df[value_col].values

            if len(trend_values) > 2:
                if all(x < y for x, y in zip(trend_values, trend_values[1:])):
                    st.success(f"{value_col} is steadily increasing.")
                elif all(x > y for x, y in zip(trend_values, trend_values[1:])):
                    st.warning(f"{value_col} is steadily decreasing.")
                else:
                    st.info(f"{value_col} shows fluctuation. Consider investigating seasonal patterns.")
            else:
                st.info("Not enough data points to determine trend.")

        # ========== KPIs ==========
        if "KPIs" in analysis_type:
            st.subheader("Key Performance Indicators")
            kpi_col = st.selectbox("Select column for KPI visualization", columns)
            st.metric(label=f"Mean of {kpi_col}", value=round(df[kpi_col].mean(), 2))
            st.metric(label=f"Max of {kpi_col}", value=round(df[kpi_col].max(), 2))
            st.metric(label=f"Min of {kpi_col}", value=round(df[kpi_col].min(), 2))

        # ========== Gaps ==========
        if "Gaps" in analysis_type:
            st.subheader("Missing Values and Gaps")
            st.write(df[columns].isnull().sum())

        # ========== رسم مخصص ==========
        st.subheader("Custom Chart")
        x_col = st.selectbox("X-axis", columns)
        y_col = st.selectbox("Y-axis", columns)
        title = st.text_input("Chart Title", "Custom Chart")
        color = st.color_picker("Chart Color", "#69b3a2")

        fig, ax = plt.subplots()

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

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Please upload a CSV or Excel file to get started.")