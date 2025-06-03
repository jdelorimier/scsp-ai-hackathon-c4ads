import streamlit as st

"""
DATA INPUTS
"""

# --- Mock query function ---
def run_query(user_input):
    if user_input.strip().lower() == "cats":
        return {
            "results": [
                {"title": "Cat 1", "image_url": "https://i.ebayimg.com/images/g/7cIAAOSwFHZnMA8N/s-l225.jpg"},
                {"title": "Cat 2", "image_url": "https://i.ebayimg.com/images/g/7cIAAOSwFHZnMA8N/s-l225.jpg"},
                {"title": "Cat 3", "image_url": "https://i.ebayimg.com/images/g/7cIAAOSwFHZnMA8N/s-l225.jpg"},
                {"title": "Cat 4", "image_url": "https://i.ebayimg.com/images/g/7cIAAOSwFHZnMA8N/s-l225.jpg"},
            ]
        }
    else:
        return {"results": []}

# --- Analysis function ---
def run_analysis(selected_result):
    st.subheader("Analysis Results")
    st.write(f"Running analysis on: **{selected_result['title']}**")
    st.markdown(f"✅ Processed: **{selected_result['title']}**")

# --- Streamlit UI ---
st.title("Image Search App")
user_input = st.text_input("Enter your query:")

if user_input:
    response = run_query(user_input)
    results = response.get("results", [])

    if results:
        st.write(f"Found {len(results)} results:")

        # Display items in a grid with "Select" buttons
        cols_per_row = 2
        for i in range(0, len(results), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                idx = i + j
                if idx >= len(results):
                    break
                item = results[idx]
                with col:
                    st.image(item["image_url"], width=150)
                    st.write(f"**{item['title']}**")
                    if st.button(f"Select", key=f"select_{idx}"):
                        run_analysis(item)
                        st.stop()  # stop rendering further to avoid duplicate analysis
    else:
        st.warning("No results found.")
