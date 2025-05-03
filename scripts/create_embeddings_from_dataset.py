from datasets import load_dataset
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import logging
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_embeddings_from_dataset(dataset_name: str = "chillies/IELTS-writing-task-2-evaluation", split: str = "train"):
    """
    Load IELTS dataset from Hugging Face and create embeddings directly in ChromaDB
    """
    try:
        # Initialize ChromaDB
        chroma_client = chromadb.Client(Settings(
            persist_directory="db",
            anonymized_telemetry=False
        ))
        
        # Initialize embedding model
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Create or get collection
        try:
            collection = chroma_client.get_collection("essays")
            logger.info("Using existing essays collection")
        except:
            collection = chroma_client.create_collection("essays")
            logger.info("Created new essays collection")
        
        # Load dataset using pandas
        logger.info(f"Loading dataset {dataset_name} from Hugging Face...")
        splits = {'train': 'train.csv', 'test': 'test.csv'}
        df = pd.read_csv(f"hf://datasets/{dataset_name}/" + splits[split])
        
        # Process dataset in batches
        batch_size = 100
        total_processed = 0
        
        for i in range(0, len(df), batch_size):
            batch = df[i:i + batch_size]
            
            # Prepare data
            ids = [str(i + total_processed) for i in range(len(batch))]
            documents = batch['essay'].tolist()  # Assuming 'essay' is the column name for essay content
            metadatas = [{
                'title': f'essay_{i + total_processed}',
                'prompt': row.get('prompt', ''),  # Adjust column names based on actual CSV structure
                'band_score': row.get('band_score', 8.0),  # Adjust column names based on actual CSV structure
                'task': row.get('task', ''),  # Adjust column names based on actual CSV structure
                'topic': row.get('topic', '')  # Adjust column names based on actual CSV structure
            } for i, (_, row) in enumerate(batch.iterrows())]
            
            # Generate embeddings
            embeddings = embedding_model.encode(documents).tolist()
            
            # Add to ChromaDB
            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )
            
            total_processed += len(batch)
            logger.info(f"Processed {total_processed} essays...")
        
        logger.info(f"Successfully added {total_processed} essays to ChromaDB")
        
    except Exception as e:
        logger.error(f"Error processing dataset: {str(e)}")
        raise

if __name__ == "__main__":
    create_embeddings_from_dataset() 