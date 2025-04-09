import streamlit as st
import pandas as pd
import knowledge_search as ks
import os
import productdescription

st.title("🤖 Product Description Generator")


def compute(file):
    with st.expander(file):
        df = productdescription.compute(file)
        st.dataframe(df[["Category", "Brand", "Model", "Product Description"]])


def main():
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if not os.path.exists("input-files/"):
        os.mkdir("input-files/")

    if uploaded_file is not None:
        file_path = "input-files/" + uploaded_file.name
        with open(file_path, 'wb') as file:
            file.write(uploaded_file.read())

        df = pd.read_csv(file_path)
        columns = df.columns.tolist()
        selected_columns = set()
        st.sidebar.title("📖Columns!")
        st.sidebar.write("Select fields to exclude from internet research!")
        cols = st.columns(3)

        for i, col_name in enumerate(columns):
            with cols[i % 3]:
                if st.sidebar.checkbox(col_name, value=False, key=col_name):
                    selected_columns.add(col_name)

        if st.button("Generate Description"):
            ks.generate_json_from_csv(file_path, "tech_components_dataset.json", selected_columns)
            compute(file_path)


def search():
    st.title("About")
    st.write("""
    This is the about page. Here you can provide information about your app.
    """)


# Create a sidebar with navigation
# st.sidebar.title("Navigation")
# page = st.sidebar.selectbox("Go to", ["Home", "Search"])

if __name__ == "__main__":
    main()
