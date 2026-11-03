import re
import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class TechnicalManualRAGEngine:
    """
    Retrieval-Augmented Generation (RAG) engine for aviation technical manuals.
    Indexes AMM, SB, and AD documentation into semantic chunks,
    performs vector similarity search, and synthesizes grounded answers with citations.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        self.chunks: List[Dict[str, Any]] = []
        self.tfidf_matrix = None
        self.is_indexed = False

    def index_document(self, doc_ref: str, revision: str, full_text: str, specifications: Dict[str, Any]):
        """
        Chunks the document prose and specifications table into retrievable knowledge modules.
        """
        self.chunks = []

        # 1. Chunk Specifications Table as dedicated knowledge units
        for param, data in specifications.items():
            val = data.get("value", "")
            raw = data.get("raw", "")
            self.chunks.append({
                "source_doc": doc_ref,
                "revision": revision,
                "category": "Technical Specification",
                "title": f"Specification: {param}",
                "content": f"The technical specification for '{param}' is defined as '{val}'. Raw entry: {raw}",
                "tokens": f"{param} {val} {raw}"
            })

        # 2. Chunk text prose into semantic sections (paragraphs / numbered tasks)
        raw_paragraphs = [p.strip() for p in re.split(r"\n\s*\n|\n(?=\d+\.\s+)", full_text) if len(p.strip()) > 30]
        
        for idx, para in enumerate(raw_paragraphs):
            # Extract section heading if present
            first_line = para.splitlines()[0]
            sec_title = first_line[:60] if len(first_line) > 5 else f"Section Paragraph {idx + 1}"
            
            self.chunks.append({
                "source_doc": doc_ref,
                "revision": revision,
                "category": "Accomplishment Procedure / Note",
                "title": sec_title,
                "content": para,
                "tokens": para
            })

        if self.chunks:
            corpus = [c["tokens"] for c in self.chunks]
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
            self.is_indexed = True

    def query(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Retrieves top relevant chunks and constructs an engineering response with citations.
        """
        if not self.is_indexed or not self.chunks:
            return {
                "answer": "No technical manuals are currently indexed in the RAG engine. Ingest a document first.",
                "citations": [],
                "confidence": 0.0
            }

        query_vec = self.vectorizer.transform([question])
        scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_indices = np.argsort(scores)[::-1][:top_k]

        retrieved_chunks = []
        max_score = 0.0

        for idx in top_indices:
            score = float(scores[idx])
            if score > 0.05:
                chunk = self.chunks[idx].copy()
                chunk["similarity_score"] = round(score, 3)
                retrieved_chunks.append(chunk)
                if score > max_score:
                    max_score = score

        if not retrieved_chunks:
            return {
                "answer": "The requested query did not match any indexed aerospace specifications, tasks, or effectivity criteria.",
                "citations": [],
                "confidence": 0.0
            }

        # Synthesize domain-grounded engineering answer
        answer_text = self._synthesize_answer(question, retrieved_chunks)

        return {
            "answer": answer_text,
            "citations": retrieved_chunks,
            "confidence": round(min(max_score * 1.5, 1.0), 2)
        }

    def _synthesize_answer(self, question: str, chunks: List[Dict[str, Any]]) -> str:
        q_lower = question.lower()
        top_chunk = chunks[0]

        # Handle specific parameter questions
        if any(w in q_lower for w in ["pressure", "psi", "bar"]):
            p_chunk = next((c for c in chunks if "pressure" in c["content"].lower()), top_chunk)
            return f"According to <b>{p_chunk['source_doc']} ({p_chunk['revision']})</b>: {p_chunk['content']}"

        elif any(w in q_lower for w in ["torque", "in-lbs", "ft-lbs", "tighten"]):
            t_chunk = next((c for c in chunks if "torque" in c["content"].lower()), top_chunk)
            return f"Per <b>{t_chunk['source_doc']} ({t_chunk['revision']})</b> installation specifications: {t_chunk['content']}"

        elif any(w in q_lower for w in ["gse", "ground", "tool", "equipment", "cart"]):
            g_chunk = next((c for c in chunks if any(k in c["content"].lower() for k in ["gse", "ground", "relief", "rig", "tool"])), top_chunk)
            return f"Regarding Ground Support Equipment & Tooling in <b>{g_chunk['source_doc']}</b>: {g_chunk['content']}"

        elif any(w in q_lower for w in ["part number", "p/n", "supersed"]):
            pn_chunk = next((c for c in chunks if "p/n" in c["content"].lower()), top_chunk)
            return f"Per Part Catalog Specifications in <b>{pn_chunk['source_doc']}</b>: {pn_chunk['content']}"

        elif any(w in q_lower for w in ["msn", "aircraft", "tail", "fleet", "applicab"]):
            app_chunk = next((c for c in chunks if any(k in c["content"].lower() for k in ["applicab", "msn", "a320", "fleet"])), top_chunk)
            return f"Applicability & Effectivity statement per <b>{app_chunk['source_doc']}</b>: {app_chunk['content']}"

        # General synthesis
        synthesis = f"Based on <b>{top_chunk['source_doc']} ({top_chunk['revision']})</b> [{top_chunk['title']}]:<br/>{top_chunk['content']}"
        return synthesis
