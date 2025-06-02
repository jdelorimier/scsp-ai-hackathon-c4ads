# dino_matcher.py
import torch
import torchvision.transforms as T
from PIL import Image
from io import BytesIO
import numpy as np
import faiss
import os
from timm import create_model
import pickle
import numpy as np
import faiss
import requests

class ResizePadToSquare:
    def __init__(self, size, fill=0):
        self.size = size
        self.fill = fill

    def __call__(self, img):
        # Resize image keeping aspect ratio
        img.thumbnail((self.size, self.size), Image.BILINEAR)
        
        # Pad to square
        pad_width = self.size - img.size[0]
        pad_height = self.size - img.size[1]
        
        padding = (
            pad_width // 2,
            pad_height // 2,
            pad_width - pad_width // 2,
            pad_height - pad_height // 2
        )
        
        return T.functional.pad(img, padding, fill=self.fill)

class DINOv2Embedder:
    def __init__(self, model_name='vit_large_patch14_dinov2.lvd142m', device='cpu'):
        self.device = device
        self.model = create_model(model_name, pretrained=True)
        self.model.eval().to(device)

        self.transform = T.Compose([
            T.Resize(518),
            ResizePadToSquare(518, fill=0),
            # T.CenterCrop(518),
            T.ToTensor(),
            T.Normalize(mean=[0.5]*3, std=[0.5]*3)
        ])

    def embed_image(self, img: Image.Image) -> np.ndarray:
        img_tensor = self.transform(img).unsqueeze(0).to(self.device)
        with torch.no_grad():
            features = self.model.forward_features(img_tensor)  # usually a dict or tensor

            if isinstance(features, dict):  # DINOv2 model from timm returns dict
                features = features['x_norm_patchtokens']  # or try 'x_norm_clstoken' if available

            pooled = features.mean(dim=1)  # mean across patch tokens

        return pooled.cpu().squeeze(0).numpy()


class Matcher:
    def __init__(self, embedder: DINOv2Embedder):
        self.embedder = embedder
        self.embeddings = []
        self.labels = []
        self.index = None

    def add_to_knowledge_base(self, image_path, label=None):
        img = Image.open(image_path).convert("RGB")
        emb = self.embedder.embed_image(img)
        self.embeddings.append(emb)
        self.labels.append(label or image_path)

    def build_index(self):
        dim = self.embeddings[0].shape[0]
        self.index = faiss.IndexFlatIP(dim)
        emb_matrix = np.vstack(self.embeddings)
        faiss.normalize_L2(emb_matrix)
        self.index.add(emb_matrix)

    def save_knowledge_base(self, path_prefix="kb"):
        # Save embeddings and labels
        with open(f"{path_prefix}_data.pkl", "wb") as f:
            pickle.dump({
                "embeddings": self.embeddings,
                "labels": self.labels,
            }, f)

        # Save FAISS index
        faiss.write_index(self.index, f"{path_prefix}_index.faiss")

    def load_knowledge_base(self, path_prefix="kb"):
        # Load embeddings and labels
        with open(f"{path_prefix}_data.pkl", "rb") as f:
            data = pickle.load(f)
            self.embeddings = data["embeddings"]
            self.labels = data["labels"]

        # Load FAISS index
        self.index = faiss.read_index(f"{path_prefix}_index.faiss")

    def match(self, image_path = None, image_url = None, top_k=1, threshold=0.90):
        if image_url:
            response = requests.get(image_url)
            content = BytesIO(response.content)
        else:
            content = image_path
        img = Image.open(content).convert("RGB")
        cand_emb = self.embedder.embed_image(img)
        faiss.normalize_L2(cand_emb.reshape(1, -1))
        D, I = self.index.search(cand_emb.reshape(1, -1), top_k)

        results = []
        for dist, idx in zip(D[0], I[0]):
            if dist >= threshold:
                results.append((self.labels[idx], float(dist)))
        return results