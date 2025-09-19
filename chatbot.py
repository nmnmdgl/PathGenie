from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from career_logic import llm

def init_chatbot(roadmap: str, career: str):
    """Initialize chatbot with roadmap + salary context."""
    memory = ConversationBufferMemory(return_messages=True)
    conversation = ConversationChain(llm=llm, memory=memory)

    # Prime with roadmap context
    conversation.run(
        f"Here is the roadmap for {career}: {roadmap}. "
        "You are now a career mentor. Use this roadmap as the context for answering follow-up questions."
    )
    return conversation
