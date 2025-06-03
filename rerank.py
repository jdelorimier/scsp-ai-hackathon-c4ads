from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth
import base64
import os
from openai import OpenAI
import pandas as pd
import json

# Load the .env file
load_dotenv()
API_KEY = os.getenv('OPENAI_KEY')

# Load and encode your images
def encode_image(file_path=None, file_url= None):
    if file_url:
        response = requests.get(file_url)
        response.raise_for_status()
        image_data = response.content
    elif file_path:
        with open(file_path, "rb") as image_file:
            image_data = image_file.read()
    else:
        raise ValueError("Either file_path or file_url must be provided.")

    return base64.b64encode(image_data).decode('utf-8')

def lookup_image_info(kb_paths):
    df = pd.read_csv("documents/DATA_WITH_PATH.csv")
    df['path_x'] = "documents/final/" + df['path_x']
    df = df[["Citation_x", "path_x"]]
    df = df[df['path_x'].isin(kb_paths)]
    df_grouped = df.groupby('path_x', as_index=False).agg({
    'Citation_x': lambda x: ' '.join(x.astype(str))
    })
    result_dict = df_grouped.set_index('path_x')['Citation_x'].to_dict()
    return result_dict


def rerank_streamlit(matches, canidate_image_url, candidate_image_description):
    """
    matches = [('documents/final/sudan-ancient-treasures-images/31344.png', 0.8022968769073486), ('documents/final/sudan-ancient-treasures-images/31354.png', 0.7959303259849548), ('documents/final/sudan-ancient-treasures-images/31245a_f.png', 0.7935127019882202)]
    """
    paths = [x[0] for x in matches]
    description_lookup = lookup_image_info(paths)

    image1_base64 = encode_image(file_path=paths[0])
    image2_base64 = encode_image(file_path=paths[1])
    image3_base64 = encode_image(file_path=paths[2])
    canidate_image_base64 = encode_image(file_url=canidate_image_url)
    system_prompt = """
    You are an expert in visual analysis and forensic investigation of cultural artifacts. Your task is to investigate a potential illegal sale of artifacts stolen from a conflict zone.

    Given:

    An input image and its detailed description

    A marketplace image and its marketplace description

    Carefully compare the input image and description with the marketplace image and description. Analyze both the visual similarities and the textual details of the descriptions.

    Your goal is to:

    Explain the similarities between the two artifacts based on their visual features and descriptive elements.

    Assess whether there is a possible match indicating the artifact in the marketplace listing could be the stolen item.

    Provide clear, reasoned explanations for your conclusions, citing specific points from both images and descriptions.

    Focus on objective comparison criteria, including shape, markings, style, material, and any distinctive features mentioned or visible.
    """

    prompt_text = f"""
    You are an expert in visual and textual artifact analysis. Compare the following three museum artifact images, which may potentially have been stolen. The descriptions for each image are provided below in the same order:

    Image 1: {description_lookup.get(paths[0], "Description not available")}

    Image 2: {description_lookup.get(paths[1], "Description not available")}

    Image 3: {description_lookup.get(paths[2], "Description not available")}

    Below is an image that may be a stolen artifact, along with the seller’s posted description:

    Suspect Item Description:
    {candidate_image_description}

    Instructions:

    Carefully analyze the artistic and stylistic details of the three museum images and compare them to the suspect image and its description.

    Determine if any of the museum images are a high-quality match to the suspect image.

    If no museum image appears to match, return the phrase "No images appear to match" in your explanation.

    Return your response strictly in the following JSON format:
    ```
    {{
      "analysis": "Your detailed explanation of the comparison and reasoning.",
      "path": "The actual path string of the selected matching image (e.g., '{description_lookup.get(paths[0], None)}', '{description_lookup.get(paths[1], None)}', '{description_lookup.get(paths[2], None)}'). If no match, return null."

    }}
    ```
    """

    # Create a message for GPT-4o with image comparisons
    client = OpenAI(api_key=API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image1_base64}"}},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image2_base64}"}},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image3_base64}"}},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{canidate_image_base64}"}},
                    {"type": "text", "text": prompt_text}
                ]
            }
        ],
        temperature=0.5,
    )
    output = response.choices[0].message.content.strip("`json\n")
    return json.loads(output)

if __name__ == "__main__":
    matches = [('documents/final/sudan-ancient-treasures-images/31346.png', 0.5404447913169861), ('documents/final/sudan-ancient-treasures-images/31226.png', 0.5346109867095947), ('documents/final/ancient_kingdoms_images/24397.png', 0.5181676149368286)]
    image_url ='https://i.ebayimg.com/images/g/7cIAAOSwFHZnMA8N/s-l225.jpg'
    desc = "Ancient City Of Naqa In Sudan Carved statue of a lion lies amongst- 1960 Photo"
    result = rerank_streamlit(matches, canidate_image_url=image_url, candidate_image_description=desc)
    print(json.loads(result))
