from typing import List
import time
import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from src.core.lore_keeper import LoreKeeper
from dotenv import load_dotenv

load_dotenv()

class LoreKeeperImpl(LoreKeeper):
    def __init__(self, model_name: str = None, max_retries: int = 3):
        self.provider = os.getenv("AI_PROVIDER", "google").lower()
        self.model_name = model_name
        self.max_retries = max_retries
        self.documents = []
        self.vector_store = None
        self.embeddings = None
        self.fallback_mode = False
        
        self.api_key = os.getenv("GOOGLE_API_KEY")
        
        # DB Path strategy: use different folders for different providers
        if self.provider == "local":
             self.db_path = "./chroma_db_local"
             self.model_name = self.model_name or "nomic-embed-text"
        else:
             self.db_path = "./chroma_db"
             self.model_name = self.model_name or "models/text-embedding-004"
             if not self.api_key:
                print("[WARN] GOOGLE_API_KEY not found. Vector search might fail.")

    def _initialize_embeddings(self):
        """Initialize embeddings with retry logic"""
        if self.embeddings is not None:
            return
        
        for attempt in range(self.max_retries):
            try:
                if self.provider == "local":
                    print(f"[INFO] Initializing Local Embeddings ({self.model_name})...")
                    self.embeddings = OllamaEmbeddings(
                        model=self.model_name
                    )
                else:
                    print(f"[INFO] Initializing Google Embeddings ({self.model_name})...")
                    self.embeddings = GoogleGenerativeAIEmbeddings(
                        model=self.model_name,
                        google_api_key=self.api_key
                    )
                
                print(f"[OK] Embeddings initialized successfully.")
                return
            except Exception as e:
                print(f"[WARN] Attempt {attempt + 1}/{self.max_retries} failed: {e}")
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print("[ERR] Failed to initialize embeddings. Entering fallback mode.")
                    self.fallback_mode = True
                    raise

    def update_api_key(self, new_api_key: str) -> bool:
        """BYOK: Update API Key for embeddings"""
        try:
            print(f"[INFO] LoreKeeper: Updating API Key for embeddings...")
            self.api_key = new_api_key
            # Re-initialize embeddings with new key
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=self.model_name or "models/text-embedding-004",
                google_api_key=new_api_key
            )
            
            # Re-create vector store with new embeddings if it exists
            # (Safest way to ensure the new key is used)
            if self.documents and self.db_path:
                 print("[INFO] LoreKeeper: Re-initializing Vector Store...")
                 self.vector_store = Chroma.from_documents(
                    documents=self.documents,
                    embedding=self.embeddings,
                    collection_name="kongjwi_story",
                    persist_directory=self.db_path
                )
                
            print("[OK] LoreKeeper API Key updated successfully.")
            return True
        except Exception as e:
            print(f"[ERR] Failed to update LoreKeeper API Key: {e}")
            return False

    def load_book(self, file_path: str) -> None:
        """
        Loads the text file and chunks it.
        """
        if not file_path:
            raise ValueError("File path cannot be empty")
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Story file not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error reading file: {e}")
            
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.documents = text_splitter.create_documents([text])
        print(f"Loaded {len(self.documents)} chunks from {file_path}")

    def build_index(self) -> None:
        """
        Builds the ChromaDB index with error handling.
        """
        if not self.documents:
            print("No documents to index. Call load_book() first.")
            return

        try:
            # Initialize embeddings if not already done
            self._initialize_embeddings()
            
            # Persist directory could be made configurable
            self.vector_store = Chroma.from_documents(
                documents=self.documents,
                embedding=self.embeddings,
                collection_name="kongjwi_story",
                persist_directory=self.db_path
            )
            print("Index built successfully.")
        except Exception as e:
            print(f"[ERR] Failed to build index: {e}")
            print("[WARN] Entering fallback mode (in-memory search only)")
            self.fallback_mode = True

    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        """
        Retrieves relevant contexts with fallback to simple text search.
        """
        if self.fallback_mode or not self.vector_store:
            # Fallback: simple keyword search in documents
            print("[WARN] Using fallback search (no vector DB)")
            return self._fallback_search(query, top_k)
        
        try:
            results = self.vector_store.similarity_search(query, k=top_k)
            return [doc.page_content for doc in results]
        except Exception as e:
            print(f"[WARN] Vector search failed: {e}, using fallback")
            return self._fallback_search(query, top_k)
    
    def _fallback_search(self, query: str, top_k: int = 3) -> List[str]:
        """
        Simple keyword-based search as fallback when vector DB is unavailable.
        """
        if not self.documents:
            return ["콩쥐팥쥐 이야기를 참고하세요."]
        
        # Simple keyword matching
        query_lower = query.lower()
        scored_docs = []
        
        for doc in self.documents:
            content_lower = doc.page_content.lower()
            # Count keyword matches
            score = sum(1 for word in query_lower.split() if word in content_lower)
            if score > 0:
                scored_docs.append((score, doc.page_content))
        
        # Sort by score and return top_k
        scored_docs.sort(reverse=True, key=lambda x: x[0])
        
        # If no matches found or specific 'start' query, return the first chunk (Chapter 1)
        # This prevents empty context which leads to hallucinations
        if not scored_docs:
            print("[INFO] Fallback search found no matches. Returning Chapter 1 context.")
            return [self.documents[0].page_content]
            
        results = [content for _, content in scored_docs[:top_k]]
        return results

