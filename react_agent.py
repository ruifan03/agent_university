
from langchain.agents import create_agent
from langchain_core.messages import AIMessage
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

        emitted_messages = set()
        for chunk in self.agent.stream(
            input_dict,
            config=config,
            stream_mode="values",
            context={'report': False},
        ):
            latest_message = chunk['messages'][-1]
            if not isinstance(latest_message, AIMessage):
                continue
            if latest_message.tool_calls:
                continue

            content = latest_message.content
            if isinstance(content, str):
                text = content.strip()
            elif isinstance(content, list):
                text = ''.join(
                    item.get('text', '')
                    for item in content
                    if isinstance(item, dict) and item.get('type') == 'text'
                ).strip()
            else:
                text = ''

            message_key = (
                getattr(latest_message, 'id', None),
                text,
            )
            if text and message_key not in emitted_messages:
                emitted_messages.add(message_key)
                yield text + '\n'
                

if __name__ == '__main__':
    agent = ReactAgent()

    for chunk in agent.execute_stream('我想要知道创新创业学分怎么获得，简要回答即可', thread_id='001'):
        print(chunk, end='', flush=True)

    for chunk in agent.execute_stream('我现在有个创新创业国赛的奖励，可以获得学分吗', thread_id='001'):
            print(chunk, end='', flush=True)





