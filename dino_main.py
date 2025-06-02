# main.py
import glob
from tqdm import tqdm
from dino_matcher import DINOv2Embedder, Matcher
from ebay import *
import json

KB_IMAGE_PATH = "documents/final/*/*.png"
SAMPLE = "documents/sample/*.png"
LOAD_FROM_CACHE = True

embedder = DINOv2Embedder(device = 'cpu')
matcher = Matcher(embedder)

# Load your knowledge base
if LOAD_FROM_CACHE:
    print("Load from cache")
    matcher.load_knowledge_base(path_prefix="kb")
    print("Cache loaded")

else:
    for img_path in tqdm(glob.glob(KB_IMAGE_PATH), desc="Building Knowledge Base"):
        matcher.add_to_knowledge_base(img_path)
        matcher.save_knowledge_base(path_prefix="kb")

matcher.build_index()


# Pre step 1
with open("documents/translated_titles_cleaned.json", 'r') as infile:
    data = json.loads(infile.read())

# STEP 1 generate queries
for QUERY in tqdm(data, desc="query list"):
    # QUERY = {
    #     "English":"VINTAGE STATUE MUSEUM PIECE",
    #     "Sudanese Arabic":"رأس أثري - القرن التاسع عشر",
    #     "MSA Arabic":"رأس أثري - القرن التاسع عشر",
    #     "Egyptian Arabic":"رأس أثري - القرن الـ 19",
    #     "French":"TÊTE ANTIQUE - XIXe SIÈCLE"
    #   }
    for query_phrase in QUERY.values():
        print(f"query phrase {query_phrase}")
        token = get_access_token()
        product_hits = search_ebay_products(query = query_phrase, access_token=token, sort="-price", limit=10)
        if product_hits['total'] == 0:
            print('no hits')
        else:
            print("hits!")
            item_list = product_hits['itemSummaries']
            for product in item_list:
                item_id = product['itemId']
                image_url = product['image']['imageUrl']
                title = product['title']
                full_product_details = get_ebay_item(access_token=token, item_id=item_id)
                # Key elements
                # full_product_details['additionalImages']
                image_url = full_product_details['image']['imageUrl']
                short_description = full_product_details['shortDescription']

                image_match = matcher.match(image_url=image_url, threshold=.1, top_k=5)
                for match in tqdm(image_match, desc="iterating canidate products"):
                    if match[1] > 0.5:
                        print(match)
                        print(f"URL:{image_url}")
                        break
                