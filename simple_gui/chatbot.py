from openai import OpenAI

class ChatBot:
    def __init__(self, api_key, personality="friendly"):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        
        self.conversation_history = []
        self.personality = personality
        self.personality_prompts = {
            "friendly": "You are a friendly and helpful AI assistant.",
            "professional": "You are a professional and formal AI assistant.",
            "funny": "You are a humorous and witty AI assistant. Use jokes and lighthearted responses.",
            "sarcastic": "You are a sarcastic AI assistant with a sharp wit."
        }
    
    def set_personality(self, personality):
        """Set chatbot personality"""
        if personality in self.personality_prompts:
            self.personality = personality
            return True
        return False
    
    def get_response(self, user_message, username="User"):
        """Get chatbot response with context awareness"""
        try:
            # Build system message with personality
            system_message = self.personality_prompts.get(
                self.personality, 
                "You are a helpful AI assistant."
            )
            
            # Build messages with conversation history
            messages = [{"role": "system", "content": system_message}]
            
            # Add conversation history for context
            for msg in self.conversation_history[-8:]:  
                messages.append(msg)
            
            messages.append({"role": "user", "content": user_message})
            
            # Call DeepSeek API
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            bot_reply = response.choices[0].message.content
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": bot_reply})
            
            # Maintain reasonable history length
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
                
            return bot_reply
            
        except Exception as e:
            return f"Sorry, I'm unable to respond right now: {str(e)}"
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_personality_options(self):
        """Get available personality options"""
        return list(self.personality_prompts.keys())

#test
if __name__ == "__main__":
    bot = ChatBot(api_key="sk-59aea2a31153449891fb6cd2596993d0")  
    
    print("ChatBot I'm here！type exit for exsiting\n")

    while True:
        user_msg = input("you：")
        if user_msg.lower() == "exit":
            break
        
        reply = bot.get_response(user_msg)
        print("bot：", reply)
