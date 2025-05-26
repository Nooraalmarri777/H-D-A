import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Vaccination KPI Analyzer", layout="wide")
st.title("Vaccination KPI Analyzer")

# رفع الملف
uploaded_file = st.file_uploader("Upload your health data file (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file:
    # قراءة الملف
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.subheader("Raw Data")
        st.dataframe(df)

        # قائمة منسدلة لاختيار الأعمدة للتحليل
        columns = st.multiselect("Select columns for analysis", df.columns.tolist(), default=df.columns.tolist())

        # تحقق من وجود الأعمدة المطلوبة
        required_columns = ["VaccinationType", "Region", "IsVaccinated"]
        if all(col in df.columns for col in required_columns):
            st.subheader("KPI Analysis")

            # تحليل حسب نوع التطعيم
            st.markdown("### عدد المطعمين حسب نوع التطعيم")
            vaccinated_by_type = df[df["IsVaccinated"] == True]["VaccinationType"].value_counts()
            st.bar_chart(vaccinated_by_type)

            # تحليل حسب النطاقات المكانية
            st.markdown("### عدد المطعمين حسب النطاق المكاني (شمالي، جنوبي، شرقي، غربي)")
            vaccinated_by_region = df[df["IsVaccinated"] == True]["Region"].value_counts()
            st.bar_chart(vaccinated_by_region)

            # الرسم البياني المخصص
            st.subheader("Custom Chart")

            x_col = st.selectbox("X-axis", options=columns)
            y_col = st.selectbox("Y-axis", options=columns)
            chart_type = st.selectbox("Chart Type", ["Bar", "Line", "Box", "Histogram", "Pie"])
            chart_title = st.text_input("Chart Title", "Custom KPI Chart")
            chart_color = st.color_picker("Pick a Chart Color", "#008B8B")

            fig, ax = plt.subplots()

            if chart_type == "Bar":
                ax.bar(df[x_col], df[y_col], color=chart_color)
            elif chart_type == "Line":
                ax.plot(df[x_col], df[y_col], color=chart_color)
            elif chart_type == "Box":
                sns.boxplot(x=df[x_col], y=df[y_col], color=chart_color, ax=ax)
            elif chart_type == "Histogram":
                ax.hist(df[y_col], bins=20, color=chart_color)
            elif chart_type == "Pie":
                pie_data = df[y_col].value_counts()
                ax.pie(pie_data, labels=pie_data.index, colors=[chart_color]*len(pie_data), autopct="%1.1f%%")

            ax.set_title(chart_title)
            st.pyplot(fig)

        else:
            st.warning("يرجى التأكد من وجود الأعمدة التالية في بياناتك: 'VaccinationType', 'Region', 'IsVaccinated'")

    except Exception as e:
        st.error(f"Error loading file: {e}")
else:
    st.info("Please upload a file to begin.")