import streamlit as st
from ebay import streamlit_image
from dino_main import streamlit_analysis
from rerank import rerank_streamlit
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['STREAMLIT_DISABLE_WATCHDOG_WARNINGS'] = 'TRUE'

KB_IMAGE_PATH = "documents/final/*/*.png"
SAMPLE = "documents/sample/*.png"
LOAD_FROM_CACHE = True


"""
DATA INPUTS
"""

# --- Mock query function ---
def run_query(user_input):
    if user_input.strip().lower() == "cats":
        return {
            "results": [
                {"title": "Cat 1", "imageUrl": "https://i.ebayimg.com/images/g/7cIAAOSwFHZnMA8N/s-l225.jpg"},
                {"title": "Cat 2", "imageUrl": "https://i.ebayimg.com/images/g/7cIAAOSwFHZnMA8N/s-l225.jpg"},
                {"title": "Cat 3", "imageUrl": "https://i.ebayimg.com/images/g/7cIAAOSwFHZnMA8N/s-l225.jpg"},
                {"title": "Cat 4", "imageUrl": "https://i.ebayimg.com/images/g/7cIAAOSwFHZnMA8N/s-l225.jpg"},
            ]
        }
    else:
        return {"results": []}
    
# --- Analysis function ---
def run_analysis(selected_result):
    st.subheader("Analysis Results")
    st.write(f"🔎 Running analysis on: **{selected_result['title']}**")

def run_dino_analysis(selected_result):
    st.subheader("Analysis Results")
    st.write(f"🔎 Running multimodal image match on: **{selected_result['title']}**")
    matches = streamlit_analysis(selected_result)
    st.write(f"Canidate matches identified")
    # st.write(f"{matches}")
    return matches

def run_rerank(matches, selected_result):
    canidate_image_url = selected_result['imageUrl']
    candidate_image_description = selected_result['description']
    rerank = rerank_streamlit(matches, canidate_image_url=selected_result)
    return rerank


# --- Streamlit UI ---
st.title("Image Search App")
user_input = st.text_input("Enter your query:")

if user_input:
    # response = run_query(user_input)
    response = streamlit_image(user_input)
    print(response)
    if response:
        results = response.get("results", [])
    else:
        results = []

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
                    st.image(item["imageUrl"], width=150)
                    st.write(f"**{item['title']}**")
                    if st.button(f"Select", key=f"select_{idx}"):
                        matches = run_dino_analysis(item)
                        match_paths = [x[0] for x in matches]
                        for match_path in match_paths:
                            st.image(match_path, width=150)

                        # Step 2
                        image_url = item["imageUrl"]
                        image_description = item['description']
                        reranked = rerank_streamlit(matches, canidate_image_url=image_url, candidate_image_description=image_description)
                        st.subheader("Confirming Matches against O3 Reasoning Model")
                        st.write(reranked["analysis"])
                        if reranked["path"]:
                            st.image(reranked["path"], caption="Suggested Match", use_column_width=True)
                        st.stop()  # stop rendering further to avoid duplicate analysis

    else:
        st.warning("No results found.")
