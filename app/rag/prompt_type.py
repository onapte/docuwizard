from dataclasses import dataclass
from enum import Enum

class PromptType(Enum):
    TEXT = "text"
    CODE = "code"
    OTHER = "other"


@dataclass
class Prompt:
    context: str
    question: str
    promptType: PromptType = PromptType.TEXT

    def format_prompt(self):
        if self.promptType == PromptType.CODE:
            role = "You are a coding assistant. Answer precisely and concisely."
        elif self.promptType == PromptType.TEXT:
            role = "You are a helpful assistant. Answer based on the document context."
        else:
            role = "You are a general assistant. Use the context to help the user."
        
        return f"""
        Context:
        {self.context}

        Question:
        {self.question}
        """