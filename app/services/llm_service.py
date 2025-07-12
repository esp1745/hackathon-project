"""
LLM service for handling conversations with the language model
"""

import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage, BaseMessage

from app.config import settings


class LLMService:
    """Service for LLM interactions"""
    
    def __init__(self):
        """Initialize the LLM service"""
        # Check if we have a valid API key
        print(f"DEBUG LLM: API Key = {settings.OPENAI_API_KEY[:10]}..." if settings.OPENAI_API_KEY else "DEBUG LLM: API Key = None")
        self.demo_mode = (not settings.OPENAI_API_KEY or 
                         settings.OPENAI_API_KEY == "your_openai_api_key_here" or 
                         not settings.OPENAI_API_KEY.startswith("sk-"))
        
        if self.demo_mode:
            print("⚠️  Running in DEMO MODE - No OpenAI API key provided")
            print("📝 To use real AI responses, set your OpenAI API key in .env file")
            self.client = None
            self.chat_model = None
        else:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.OPENAI_MODEL
            self.chat_model = ChatOpenAI(
                model=self.model,
                temperature=0.7
            )
        
        # System prompt for the AI
        self.system_prompt = """You are a helpful, intelligent voice assistant with access to custom knowledge through RAG (Retrieval-Augmented Generation). 
        
        Your capabilities include:
        - Answering questions based on general knowledge
        - Providing information from uploaded documents
        - Engaging in natural conversations
        - Maintaining context across conversation turns
        - Specialized knowledge about real estate properties and market data
        
        Guidelines:
        - Be conversational and natural in your responses
        - Use the provided context from documents when available
        - Keep responses concise but informative
        - If you don't know something, say so rather than guessing
        - Be helpful and friendly in your tone
        - For real estate queries, provide detailed information about properties, brokers, pricing, and market insights
        - When discussing property data, mention specific details like addresses, rents, sizes, and broker information
        
        When responding to voice interactions, keep in mind that your response will be converted to speech, so use natural language that sounds good when spoken."""
    
    async def generate_response(
        self, 
        message: str, 
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        rag_context: Optional[List[str]] = None
    ) -> str:
        """
        Generate a response using the LLM
        
        Args:
            message: User message
            conversation_history: Previous conversation messages
            rag_context: Context from RAG system
            
        Returns:
            AI response
        """
        try:
            # Demo mode response
            if self.demo_mode:
                return self._generate_demo_response(message, rag_context)
            
            # Prepare messages for the LLM
            messages: List[BaseMessage] = [SystemMessage(content=self.system_prompt)]
            
            # Add conversation history if available
            if conversation_history:
                for msg in conversation_history[-10:]:  # Limit to last 10 messages
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        messages.append(AIMessage(content=msg["content"]))
            
            # Add RAG context if available
            if rag_context:
                context_text = "\n\n".join(rag_context)
                enhanced_message = f"Context from documents:\n{context_text}\n\nUser question: {message}"
                messages.append(HumanMessage(content=enhanced_message))
            else:
                messages.append(HumanMessage(content=message))
            
            # Generate response
            response = await self.chat_model.agenerate([messages])
            
            return response.generations[0][0].text.strip()
            
        except Exception as e:
            raise Exception(f"LLM response generation failed: {str(e)}")
    
    def _generate_demo_response(self, message: str, rag_context: Optional[List[str]] = None) -> str:
        """Generate a demo response when no API key is available"""
        message_lower = message.lower()
        
        # Check for real estate related queries
        if any(word in message_lower for word in ['property', 'real estate', 'rent', 'broker', 'apartment', 'house']):
            if rag_context:
                return f"Based on the property data available, I can help you with real estate information. I found some relevant property details in our database. What specific information are you looking for about properties, brokers, or rental rates?"
            else:
                return "I can help you with real estate information! I have access to property data including listings, brokers, rental rates, and market insights. What would you like to know about available properties?"
        
        # Check for general conversation
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm your voice assistant. I can help you with information, answer questions, and provide insights from our knowledge base. How can I assist you today?"
        
        if any(word in message_lower for word in ['help', 'what can you do']):
            return "I'm a voice assistant with access to custom knowledge and real estate data. I can answer questions, provide information from documents, and help you find property information. Just ask me anything!"
        
        # Default response
        return "I understand your message. In demo mode, I can provide general responses and help you explore the system. For full AI capabilities, please add your OpenAI API key to the .env file."
    
    async def generate_response_with_functions(
        self,
        message: str,
        functions: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate response with function calling capabilities
        
        Args:
            message: User message
            functions: Available functions
            conversation_history: Previous conversation messages
            
        Returns:
            Response with function calls if applicable
        """
        try:
            # Demo mode response
            if self.demo_mode:
                return {
                    "response": self._generate_demo_response(message),
                    "function_call": None
                }
            
            # Prepare messages
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add conversation history
            if conversation_history:
                messages.extend(conversation_history[-10:])
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Generate response with function calling
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=functions,
                function_call="auto"
            )
            
            return {
                "response": response.choices[0].message.content,
                "function_call": response.choices[0].message.function_call
            }
            
        except Exception as e:
            raise Exception(f"LLM function calling failed: {str(e)}")
    
    def format_conversation_history(
        self, 
        history: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Format conversation history for LLM consumption
        
        Args:
            history: Raw conversation history
            
        Returns:
            Formatted conversation history
        """
        formatted_history = []
        
        for msg in history:
            if msg.get("role") in ["user", "assistant"]:
                formatted_history.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        return formatted_history
    
    async def summarize_conversation(
        self, 
        conversation_history: List[Dict[str, Any]]
    ) -> str:
        """
        Summarize a conversation for context
        
        Args:
            conversation_history: Conversation to summarize
            
        Returns:
            Conversation summary
        """
        try:
            if not conversation_history:
                return ""
            
            # Demo mode summary
            if self.demo_mode:
                return "Demo conversation - User interacted with the voice assistant system."
            
            # Create summary prompt
            messages_text = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in conversation_history[-20:]  # Last 20 messages
            ])
            
            summary_prompt = f"""Please provide a brief summary of this conversation:

{messages_text}

Summary:"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes conversations concisely."},
                    {"role": "user", "content": summary_prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Conversation summarization failed: {str(e)}")


# Create global LLM service instance
llm_service = LLMService() 