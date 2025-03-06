import os
from langchain_mistralai import MistralAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from vector_store import VectorStore

class PhoenixAssistant:
    def __init__(self, api_key=None):
        # Use environment variable if api_key not provided
        self.api_key = api_key or os.environ.get("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("Mistral API key is required. Set MISTRAL_API_KEY environment variable or pass it to the constructor.")
        
        self.llm = MistralAI(model="mistral-large-latest", api_key=self.api_key)
        self.vector_store = VectorStore()
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.setup_chain()
    
    def setup_chain(self):
        template = """You are Phoenix Assistant, an AI helper for people affected by the 2025 Los Angeles County fires. 
        Your goal is to provide accurate, helpful information to assist with recovery and rebuilding efforts.

        Chat History:
        {chat_history}
        
        Context information from official sources:
        {context}
        
        Human: {human_input}
        
        Phoenix Assistant:"""
        
        prompt = PromptTemplate(
            input_variables=["chat_history", "context", "human_input"],
            template=template
        )
        
        self.chain = LLMChain(
            llm=self.llm,
            prompt=prompt,
            memory=self.memory,
            verbose=True
        )
    
    def get_context(self, query, num_chunks=3):
        """Retrieve relevant context from the vector store"""
        results = self.vector_store.query(query, limit=num_chunks)
        
        if not results:
            return "No specific information found in the database. I'll try to help with general knowledge."
        
        context_parts = []
        for i, result in enumerate(results):
            context_parts.append(f"Source: {result['source']}\nCategory: {result['category']}\n{result['content']}")
        
        return "\n\n".join(context_parts)
    
    def ask(self, query):
        """Process a user query and return a response"""
        context = self.get_context(query)
        
        response = self.chain.predict(
            human_input=query,
            context=context
        )
        
        return response

if __name__ == "__main__":
    # For testing
    import os
    os.environ["MISTRAL_API_KEY"] = "your-api-key-here"  # Replace with your actual API key
    
    assistant = PhoenixAssistant()
    
    # Test questions
    test_questions = [
        "How do I apply for FEMA assistance?",
        "Where can I find temporary housing in Altadena?",
        "What are the steps to start rebuilding my home?",
        "Are there any upcoming deadlines I should know about?"
    ]
    
    for question in test_questions:
        print(f"Question: {question}")
        response = assistant.ask(question)
        print(f"Response: {response}")
        print("-" * 50)