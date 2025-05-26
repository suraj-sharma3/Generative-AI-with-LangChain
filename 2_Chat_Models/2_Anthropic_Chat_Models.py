from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

load_dotenv()

model = ChatAnthropic(model='claude-3-5-sonnet-20241022') # you can also set the temperature and max_tokens

result = model.invoke('What is the capital of Mongolia')

print(result.content)