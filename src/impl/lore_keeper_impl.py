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
        """BYOK: Validate API Key (Stateless Check)"""
        # NOTE: We do NOT update self.api_key or self.embeddings here anymore.
        # This prevents polluting the global singleton with a user-specific key.
        # Instead, we just verify the key works.
        try:
            print(f"[INFO] LoreKeeper: Verifying User API Key...")
            
            # Temporary test instance
            test_embeddings = GoogleGenerativeAIEmbeddings(
                model=self.model_name or "models/text-embedding-004",
                google_api_key=new_api_key
            )
            
            # Try a simple embedding operation to validate key
            test_embeddings.embed_query("Hello World")
            
            print("[OK] User API Key verified successfully.")
            return True, "Success"
        except Exception as e:
            print(f"[ERR] User API Key Verification Failed: {e}")
            return False, str(e)

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

    def retrieve(self, query: str, top_k: int = 3, api_key: str = None) -> List[str]:
        """
        Retrieves relevant contexts.
        Args:
            query: The search query
            top_k: Number of results to return
            api_key: Optional user-provided API key for this specific request. 
                     If provided, creates an isolated search context.
        """
        
        # 0. Handle Fallback (No DB at all)
        if self.fallback_mode:
            print("[WARN] Using fallback search (no vector DB)")
            return self._fallback_search(query, top_k)
        
        target_store = self.vector_store

        # 1. Handle User API Key (Isolation Logic)
        if api_key:
            # If user provided a key, we must NOT use the global vector_store (which uses global key)
            # We create a lightweight temporary Chroma client pointing to the SAME data,
            # but using the user's key for the embedding function.
            try:
                user_embeddings = GoogleGenerativeAIEmbeddings(
                    model=self.model_name or "models/text-embedding-004",
                    google_api_key=api_key
                )
                
                target_store = Chroma(
                    persist_directory=self.db_path,
                    embedding_function=user_embeddings,
                    collection_name="kongjwi_story"
                )
            except Exception as e:
                print(f"[ERR] Failed to create user-specific vector store: {e}")
                # If key was bad, it would fail here. Failsafe to fallback search.
                return self._fallback_search(query, top_k)

        # 2. Perform Search
        if not target_store:
             return self._fallback_search(query, top_k)

        try:
            results = target_store.similarity_search(query, k=top_k)
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

