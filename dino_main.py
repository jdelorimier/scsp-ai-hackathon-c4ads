# main.py
import glob
from tqdm import tqdm
from dino_matcher import DINOv2Embedder, Matcher

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

# PATHS
# canidate_paths = [
#     "/Users/nike/Code/GitHub/sudanese-antiquities-hackathon/documents/kb_sudan/26883.png",
#     "/Users/nike/Code/GitHub/sudanese-antiquities-hackathon/documents/sample/test.jpg"
# ]

# for path in canidate_paths:
#     result = matcher.match(path, threshold=.5, top_k = 3)
#     print(result)

# canidate_url = "https://i.ebayimg.com/images/g/7cIAAOSwFHZnMA8N/s-l1600.jpg"

# result = matcher.match(image_url=canidate_url, threshold=.1, top_k=5)

canidate_path = "/Users/nike/Desktop/screenshots/videos/Screenshot 2025-06-02 at 2.39.55 PM.png"

result = matcher.match(image_path=canidate_path, threshold=.1, top_k=5)

print(result)


