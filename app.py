import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Vaccination KPI Analyzer", layout="wide")
st.title("Vaccination KPI Analyzer")

# رفع الملف
uploaded_file = st.file_uploader("Upload your health data file (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.subheader("Raw Data")
        st.dataframe(df)

        # اختيار الأعمدة للتحليل
        columns = st.multiselect("Select columns for analysis", df.columns.tolist(), default=df.columns.tolist())

        # اختيار نوع التحليل
        analysis_type = st.selectbox("Select KPI Analysis Type", [
            "None",
            "Vaccinated by Vaccination Type",
            "Vaccinated by Region"
        ])

        if analysis_type != "None":
            # اختيار نوع الرسم البياني وتخصيصه
            chart_type = st.selectbox("Select Chart Type", ["Bar", "Pie", "Line"])
            chart_color = st.color_picker("Pick a Chart Color", "#007ACC")
            chart_title = st.text_input("Enter Chart Title", value=analysis_type)

            # تنفيذ التحليل المختار
            if analysis_type == "Vaccinated by Vaccination Type":
                if all(col in df.columns for col in ["VaccinationType", "IsVaccinated"]):
                    filtered = df[df["IsVaccinated"] == True]
                    result = filtered["VaccinationType"].value_counts()

                    st.subheader("Result Table")
                    st.dataframe(result)

                    st.subheader("Chart")
                    fig, ax = plt.subplots()
                    if chart_type == "Bar":
                        ax.bar(result.index, result.values, color=chart_color)
                    elif chart_type == "Line":
                        ax.plot(result.index, result.values, color=chart_color)
                    elif chart_type == "Pie":
                        ax.pie(result.values, labels=result.index, colors=[chart_color]*len(result), autopct='%1.1f%%')
                    ax.set_title(chart_title)
                    st.pyplot(fig)
                else:
                    st.warning("Missing columns: 'VaccinationType' and 'IsVaccinated'")

            elif analysis_type == "Vaccinated by Region":
                if all(col in df.columns for col in ["Region", "IsVaccinated"]):
                    filtered = df[df["IsVaccinated"] == True]
                    result = filtered["Region"].value_counts()

                    st.subheader("Result Table")
                    st.dataframe(result)

                    st.subheader("Chart")
                    fig, ax = plt.subplots()
                    if chart_type == "Bar":
                        ax.bar(result.index, result.values, color=chart_color)
                    elif chart_type == "Line":
                        ax.plot(result.index, result.values, color=chart_color)
                    elif chart_type == "Pie":
                        ax.pie(result.values, labels=result.index, colors=[chart_color]*len(result), autopct='%1.1f%%')
                    ax.set_title(chart_title)
                    st.pyplot(fig)
                else:
                    st.warning("Missing columns: 'Region' and 'IsVaccinated'")

        # رسم مخصص
        st.subheader("Custom Chart")
        x_col = st.selectbox("X-axis", columns)
        y_col = st.selectbox("Y-axis", columns)
        custom_chart_type = st.selectbox("Chart Type", ["Bar", "Line", "Box", "Histogram", "Pie"], key="custom")
        custom_title = st.text_input("Custom Chart Title", "Custom KPI Chart")
        custom_color = st.color_picker("Chart Color", "#00BFFF", key="color_custom")

        if st.button("Generate Custom Chart"):
            fig, ax = plt.subplots()
            if custom_chart_type == "Bar":
                ax.bar(df[x_col], df[y_col], color=custom_color)
            elif custom_chart_type == "Line":
                ax.plot(df[x_col], df[y_col], color=custom_color)
            elif custom_chart_type == "Box":
                sns.boxplot(x=df[x_col], y=df[y_col], color=custom_color, ax=ax)
            elif custom_chart_type == "Histogram":
                ax.hist(df[y_col], bins=20, color=custom_color)
            elif custom_chart_type == "Pie":
                pie_data = df[y_col].value_counts()
                ax.pie(pie_data, labels=pie_data.index, colors=[custom_color]*len(pie_data), autopct="%1.1f%%")

            ax.set_title(custom_title)
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Error loading file: {e}")
else:
    st.info("Please upload a file to begin.")