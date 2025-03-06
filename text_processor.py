import os
import re
import nltk
from nltk.tokenize import sent_tokenize

# Download NLTK data if not already present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class TextProcessor:
    def __init__(self, data_dir="data", output_dir="chunks"):
        self.data_dir = data_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def clean_text(self, text):
        """Clean the text by removing extra whitespace and normalizing"""
        # Replace multiple newlines with a single one
        text = re.sub(r'\n+', '\n', text)
        # Replace multiple spaces with a single one
        text = re.sub(r' +', ' ', text)
        return text.strip()
    
    def chunk_text(self, text, min_size=500, max_size=1000):
        """Split text into chunks of specified size, respecting sentence boundaries"""
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence)
            
            # If adding this sentence would exceed max_size and we already have content,
            # save the current chunk and start a new one
            if current_size + sentence_size > max_size and current_size >= min_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_size = 0
            
            current_chunk.append(sentence)
            current_size += sentence_size
            
            # If we've reached min_size and the sentence ends with a period,
            # it might be a good place to break
            if current_size >= min_size and sentence.endswith('.'):
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_size = 0
        
        # Add any remaining content as a chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))
            
        return chunks
    
    def process_files(self):
        """Process all text files in the data directory and create chunks"""
        chunk_metadata = []
        
        for filename in os.listdir(self.data_dir):
            if not filename.endswith('.txt'):
                continue
                
            file_path = os.path.join(self.data_dir, filename)
            source_page = filename.replace('.txt', '').replace('_', '/')
            
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            cleaned_text = self.clean_text(text)
            chunks = self.chunk_text(cleaned_text)
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{filename.replace('.txt', '')}_{i}"
                chunk_file = os.path.join(self.output_dir, f"{chunk_id}.txt")
                
                with open(chunk_file, 'w', encoding='utf-8') as f:
                    f.write(chunk)
                
                # Store metadata for this chunk
                category = self.determine_category(source_page)
                chunk_metadata.append({
                    'id': chunk_id,
                    'source': source_page,
                    'category': category,
                    'path': chunk_file
                })
        
        return chunk_metadata
    
    def determine_category(self, source_page):
        """Determine the category of content based on the URL"""
        if 'get-help-online' in source_page:
            return 'online_help'
        elif 'get-help-in-person' in source_page:
            return 'in_person_help'
        elif 'start-your-recovery' in source_page:
            return 'recovery'
        elif 'housing' in source_page:
            return 'housing'
        elif 'financial' in source_page:
            return 'financial'
        else:
            return 'general'

if __name__ == "__main__":
    processor = TextProcessor()
    metadata = processor.process_files()
    print(f"Created {len(metadata)} chunks with metadata")