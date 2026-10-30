
from langchain.agents import create_agent
from model.factory import chat_model
from utils.prompt_loader import load_system_prompt
from tools.agent_tools import rag_summarize, fill_context_for_report 
from tools.middleware import monitor_tool, log_before_model, report_prompt_switch
from langgraph.checkpoint.memory import InMemorySaver

class ReactAgent:
    def __init__(self):
        self.checkpointer = InMemorySaver()

        self.agent = create_agent(
            model=chat_model,
            system_prompt=load_system_prompt(),
            tools=[rag_summarize, fill_context_for_report],
            middleware=[monitor_tool, log_before_model, report_prompt_switch],
            checkpointer=self.checkpointer,
        )

    def execute_stream(self, query, thread_id=None, image_data_url=None):
        if image_data_url:
            content = [
                {'type': 'text', 'text': query},
                {'type': 'image_url', 'image_url': {'url': image_data_url}},
            ]
        else:
            content = query

        input_dict = {
            'messages' : [
                {'role': 'user', 'content': content},
            ]
        }

        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        for chunk in self.agent.stream(input_dict, 
                                       config=config, 
                                       stream_mode="values", 
                                       context={'report': False}):
            lastest_message = chunk['messages'][-1]
            content = lastest_message.content
            if isinstance(content, str) and content.strip():
                yield content.strip() + '\n'
            elif isinstance(content, list):
                text = ''.join(
                    item.get('text', '')
                    for item in content
                    if isinstance(item, dict) and item.get('type') == 'text'
                ).strip()
                if text:
                    yield text + '\n'
                

if __name__ == '__main__':
    agent = ReactAgent()

    for chunk in agent.execute_stream('我想要知道创新创业学分怎么获得，简要回答即可', thread_id='001'):
        print(chunk, end='', flush=True)

    for chunk in agent.execute_stream('我现在有个创新创业国赛的奖励，可以获得学分吗', thread_id='001'):
            print(chunk, end='', flush=True)






