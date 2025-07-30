""" core 需要修改"""
import re
import os
import time
from contextlib import contextmanager
import importlib.resources
from typing import Dict, Any
import yaml
from llmada import BianXieAdapter
from querypipz import BuilderFactory,BuilderType,Director
from agentflowz.main import AgentFactory,AgentType,EasyAgentz
from toolsz.dev import AutoAPIMD

from .log import Log
logger = Log.logger
logger_path = 'logs/querypipz.log'

""" config.yaml
query_persist_dir: /Users/zhaoxuefeng/GitHub/test1/obsidian_kb/my_obsidian_notes
WORK_CANVAS_PATH:
- /工程系统级设计/能力级别/人体训练设计/人体训练设计.canvas
ModelCards:
- gpt-4.1
- cus-gemini-2.5-flash-preview-04-17-nothinking
- cus-gemini-2.5-flash-preview-04-17-thinking
Custom:
- config_info
- chat_with_long_memory_v2
- long_memory_v2_retriver
- chat_with_Agent_notes
- Custom_Agent_Latest
- Experts_V1
"""



LLM_INFO = {
"query_persist_dir": "/Users/zhaoxuefeng/GitHub/test1/obsidian_kb/my_obsidian_notes",
"WORK_CANVAS_PATH": [
"/工程系统级设计/能力级别/人体训练设计/人体训练设计.canvas"
],
"ModelCards": [
    "gpt-4.1",
    "cus-gemini-2.5-flash-preview-04-17-nothinking",
    "cus-gemini-2.5-flash-preview-04-17-thinking"
],
"Custom": [
            "config_info",
            "logger_info",
            "chat_with_long_memory_v2",
            "long_memory_v2_retriver",
            "chat_with_Agent_notes",
            "Custom_Agent_Latest",
            "Experts_V1",
            # "llmada_expert",
            # "canvaz_expert",
            # "kanbanz_expert",
            # "appscriptz_expert",
            # "toolsz_expert",
            # "mermaidz_expert",
            # "promptlibz_expert",
            "ReactAgent_API_Expert",
            "small_chat",
        ]
}



def load_config():
    """ load config """
    with importlib.resources.open_text('clientz', 'config.yaml') as f:
        return yaml.safe_load(f)

def format_node_for_chat(node_data: Dict[str, Any]) -> str:
    """
    解析节点数据，生成适合聊天窗口显示的格式化字符串。

    Args:
        node_data: 包含节点信息的字典结构。

    Returns:
        一个格式化的字符串，包含分数和节点文本内容。
        如果结构异常，返回错误提示。
    """
    node = node_data.get('node')
    score = node_data.get('score')

    if not node:
        return "Error: Could not find 'node' information."

    text_content = node.get('text')
    if not text_content:
        return "Error: 'text' content not found in node."

    # 移除 text 开头的 "topic:  content: \n\n\n" 或类似的元数据前缀
    # 根据你提供的样本，可能是固定的前缀，或者需要更灵活的处理
    # 这里简单移除已知的开头
    prefix_to_remove = "topic:  content: \n\n\n"
    if text_content.startswith(prefix_to_remove):
        text_content = text_content[len(prefix_to_remove):].strip()
    else:
        text_content = text_content.strip() # 或者只移除首尾空白

    # 构建输出字符串
    output = ""
    if score is not None:
        # 格式化分数，例如保留两位小数
        output += f"**Relevant Information (Score: {score:.2f})**:\n\n"
    else:
        output += "**Relevant Information:**\n\n"

    # 直接添加处理后的文本内容
    # 假设聊天窗口支持 Markdown，会渲染 #, ##, **, -, []() 等
    output += text_content

    # 你可以进一步处理 links，例如将它们提取出来单独列在末尾
    # link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
    # links_found = link_pattern.findall(text_content)
    # if links_found:
    #     output += "\n\n---\n*Links mentioned:*\n"
    #     for link_text, link_url in links_found:
    #         output += f"- [{link_text}]({link_url})\n" # 或其他格式

    return output

def extract_last_user_input(dialogue_text):
    """
    从多轮对话文本中提取最后一个 user 的输入内容。

    Args:
        dialogue_text: 包含多轮对话的字符串。

    Returns:
        最后一个 user 的输入内容字符串，如果未找到则返回 None。
    """
    # 修正后的正则表达式
    # (?s) 标志：使 . 匹配换行符
    # .* 匹配任意字符，直到最后一个 user:
    # user:\s* 匹配 "user:" 后面的零个或多个空白字符
    # (.*?) 非贪婪匹配任意字符，直到下一个 user: 或字符串末尾
    # (?=user:|$) 正向先行断言：断言后面是 "user:" 或者字符串末尾
    pattern = r"(?s).*user:\s*(.*?)(?=user:|$)"

    match = re.search(pattern, dialogue_text)

    if match:
        # group(1) 捕获的是最后一个 user: 到下一个 user: 或字符串末尾的内容
        return match.group(1).strip()
    else:
        return None




@contextmanager
def check_time(title:str,logger):
    """ try catch"""
    time1 = time.time()
    yield
    time2 = time.time()
    logger.debug(f"{title}: {time2-time1}")

    

def extra_docs(inputs:str)->dict:
    """ docs """
    pattern1 = r'<context>(.*?)<\/context>'
    pattern2 = r'<source id="(\d+)">(.*?)<\/source>'

    match = re.search(pattern1, inputs,re.DOTALL)

    if match:
        sources = match.group(1).strip()
        matches = re.findall(pattern2, sources)

    result = {int(id): content for id, content in matches}
    return result


class ChatBox():
    """ chatbox """
    def __init__(self) -> None:
        self.bx = BianXieAdapter()
        # self.dicts = load_config()
        self.dicts = LLM_INFO
        self.query_persist_dir = self.dicts.get('query_persist_dir')
        self.model_pool = self.dicts.get("ModelCards")
        self.file_path = 'clientz/config.yaml'
        self._last_modified_time = None
        self._update_last_modified_time()
        self.init_lazy_parameter()
        self.query = None
        self.ReactAgent_API_Expert_engine = None

    def _update_last_modified_time(self):
        """更新存储的最后修改时间"""
        try:
            self._last_modified_time = os.path.getmtime(self.file_path)
        except FileNotFoundError:
            self._last_modified_time = None # 文件不存在时设为None

    def check_and_trigger(self):
        """检查文件是否变化，如果变化则触发动作"""
        try:
            current_modified_time = os.path.getmtime(self.file_path)
            if current_modified_time != self._last_modified_time:
                print(f"文件 '{self.file_path}' 已发生变化。")
                self._trigger_action()
                self._last_modified_time = current_modified_time # 更新存储的时间
            else:
                print(f"文件 '{self.file_path}' 未发生变化。")
        except FileNotFoundError:
            print(f"文件 '{self.file_path}' 不存在。")
            self._last_modified_time = None # 文件不存在时重置状态
        except Exception as e:
            print(f"检查文件时发生错误: {e}")

    def _trigger_action(self):
        """当文件发生变化时触发的动作"""
        # 可以修改
        # 这里可以放置你想要执行的具体动作，例如：
        # - 读取文件内容
        # - 处理文件数据
        # - 调用其他函数
        print("触发预定动作...")
        # 示例：读取文件内容并打印
        try:
            self.dicts = load_config()

        except FileNotFoundError:
            print(f"触发动作时文件 '{self.file_path}' 不存在。")
        except Exception as e:
            print(f"读取文件时发生错误: {e}")

    def product(self,prompt_with_history: str, model: str) -> str:
        """ x """
        prompt_with_history, model
        return ''

    def init_lazy_parameter(self):
        """ 一个懒加载的初始化头部 """
        self.chat_with_agent_notes_object = None


    async def astream_product(self,prompt_with_history: str, model: str) -> Any:
        """
        # 只需要修改这里
        """
        self.check_and_trigger()
        prompt_no_history = extract_last_user_input(prompt_with_history)
        logger.debug(f"# prompt_no_history : {prompt_no_history}")
        logger.debug(f"# prompt_with_history : {prompt_with_history}")
        ## __init__ ##

        if model[4:] in self.model_pool:
            self.bx.set_model(model[4:])
            for word in self.bx.product_stream(prompt_with_history):
                yield word

        elif model == "config_info":
            logger.info(f"running {model}")
            yield f"query_dir: {self.query_persist_dir}, dicts {str(self.dicts)}"

            if self.chat_with_agent_notes_object:
                yield self.chat_with_agent_notes_object.tool_calls()

        elif model == "logger_info":
            logger.info(f"running {model}")
            with open(logger_path,'r') as f:
                text = f.read()
            yield text[-10000:]


        # elif model == "llmada_expert":
        #     input_file = '/Users/zhaoxuefeng/GitHub/llmada/src/llmada/core.py'  # 替换为你的 Python 文件路径
        #     output_file = 'api_documentation_llmada.md'
        #     api_doc = AutoAPIMD().generate_api_docs(input_file, output_file)
        #     logger.debug(f'api_doc:{api_doc}')
        #     # api_doc = "# API Documentation\n\n## Classes\n\n### ResourceExhaustedError\nRaised when a resource's quota has been exceeded.\n\n#### Methods\n```python\ndef __init__(self, message):\n```\nNo docstring provided.\n\n### ModelAdapter\n语言大模型的抽象类\n\n    \n\n#### Methods\n```python\ndef __init__(self):\n```\nNo docstring provided.\n\n```python\ndef set_model(self, model_name: str):\n```\n实例化以后用以修改调用的模型, 要求该模型存在于 model_pool 中\n\nArgs:\n    model_name (str): _description_\n\n```python\ndef set_temperature(self, temperature: float):\n```\n用于设置模型的temperature\n\nArgs:\n    temperature (float): model temperature\n\n```python\ndef get_model(self) -> list[str]:\n```\n获得当前的 model_pool\n\nReturns:\n    list[str]: models\n\n```python\ndef product(self, prompt: str) -> str:\n```\n子类必须实现的类, 用于和大模型做非流式交互\n\nArgs:\n    prompt (str): 提示词\n\nRaises:\n    NotImplementedError: pass\n\nReturns:\n    str: 大模型返回的结果\n\n```python\ndef chat(self, messages: list) -> str:\n```\n子类必须实现的类, 用于和大模型做聊天交互\n\nReturns:\n    str: 大模型返回的结果\n\n### ModelModalAdapter\nNo docstring provided.\n\n#### Methods\n```python\ndef get_modal_model(self):\n```\n获取支持多模态的模型列表\n\nRaises:\n    NotImplementedError: _description_\n\n```python\ndef product_modal(self, prompt: RichPromptTemplate) -> str:\n```\n提供多模态的非流式交流\n\nArgs:\n    prompt (RichPromptTemplate): llama-index 的富文本格式\n\nReturns:\n    str: _description_\n\n### BianXieAdapter\nBianXie格式的适配器\n    \n\n#### Methods\n```python\ndef __init__(self, api_key: str, api_base: str):\n```\n初始化\n正常情况下, 这两个参数都不需要传入, 而是会自动寻找环境变量,除非要临时改变api_key.\n    api_base 不需要特别指定\nArgs:\n    api_key (str): API key for authentication.\n    api_base (str): Base URL for the API endpoint.\n\n```python\ndef get_modal_model(self) -> list[str]:\n```\n返回多模态模型池\n\nReturns:\n    list[str]: 大量模型的字符串名称列表\n\n```python\ndef product_modal(self, prompt: RichPromptTemplate) -> str:\n```\nNo docstring provided.\n\n```python\ndef _deal_response(self, response):\n```\n处理事件的相应\n\n```python\ndef product(self, prompt: str) -> str:\n```\nGenerate a response from the model based on a single prompt.\n\nArgs:\n    prompt (str): The input text prompt to generate a response for.\n\nReturns:\n    str: The response generated by the model.\n\n```python\ndef _assert_prompt(self, prompt):\n```\nNo docstring provided.\n\n```python\ndef product_stream(self, prompt: str) -> str:\n```\nGenerate a response from the model based on a single prompt.\n\nArgs:\n    prompt (str): The input text prompt to generate a response for.\n\nReturns:\n    str: The response generated by the model.\n\n```python\ndef chat(self, messages: list) -> str:\n```\nEngage in a conversation with the model using a list of messages.\n\nArgs:\n    messages (list): A list of message dictionaries, each containing a role and content.\n\nReturns:\n    str: The response generated by the model for the conversation.\n\n```python\ndef chat_stream(self, messages: list) -> str:\n```\nEngage in a conversation with the model using a list of messages.\n\nArgs:\n    messages (list): A list of message dictionaries, each containing a role and content.\n\nReturns:\n    str: The response generated by the model for the conversation.\n\n```python\ndef chat_stream_history(self, prompt: str, system: str) -> str:\n```\nEngage in a conversation with the model using a list of messages.\n\nArgs:\n    messages (list): A list of message dictionaries, each containing a role and content.\n\nReturns:\n    str: The response generated by the model for the conversation.\n\n### ArkAdapter\nNo docstring provided.\n\n#### Methods\n```python\ndef __init__(self, api_key: str, api_base: str):\n```\n初始化\n\nArgs:\n    api_key (str): API key for authentication.\n    api_base (str): Base URL for the API endpoint.\n\n```python\ndef product(self, prompt: str) -> str:\n```\nGenerate a response from the model based on a single prompt.\n\nArgs:\n    prompt (str): The input text prompt to generate a response for.\n\nReturns:\n    str: The response generated by the model.\n\n```python\ndef chat(self, messages: list) -> str:\n```\nEngage in a conversation with the model using a list of messages.\n\nArgs:\n    messages (list): A list of message dictionaries, each containing a role and content.\n\nReturns:\n    str: The response generated by the model for the conversation.\n\n### GoogleAdapter\nNo docstring provided.\n\n#### Methods\n```python\ndef __init__(self, api_key: str):\n```\n初始化\n\nArgs:\n    api_key (str): API key for authentication.\n\n```python\ndef product(self, prompt: str) -> str:\n```\nGenerate a response from the model based on a single prompt.\n\nArgs:\n    prompt (str): The input text prompt to generate a response for.\n\nReturns:\n    str: The response generated by the model.\n\n```python\ndef chat(self, messages: list) -> str:\n```\nEngage in a conversation with the model using a list of messages.\n\nArgs:\n    messages (list): A list of message dictionaries, each containing a role and content.\n\nReturns:\n    str: The response generated by the model for the conversation.\n\n### KimiAdapter\nKimi格式的适配器\n\n    \n\n#### Methods\n```python\ndef __init__(self, api_key: str, api_base: str):\n```\n初始化\n\nArgs:\n    api_key (str): API key for authentication.\n    api_base (str): Base URL for the API endpoint.\n\n```python\ndef product(self, prompt: str) -> str:\n```\nGenerate a response from the model based on a single prompt.\n\nArgs:\n    prompt (str): The input text prompt to generate a response for.\n\nReturns:\n    str: The response generated by the model.\n\n```python\ndef chat(self, messages: list) -> str:\n```\nEngage in a conversation with the model using a list of messages.\n\nArgs:\n    messages (list): A list of message dictionaries, each containing a role and content.\n\nReturns:\n    str: The response generated by the model for the conversation.\n\n"
        #     system_prompt = f"""
        #     以下是软件包llmada 的api文档, 请有限使用该包完成用户的问题
        #     API_DOCUMENT:

        #     {api_doc}
        #     ---

        #     """
        #     prompt = system_prompt + prompt_with_history
        #     for word in self.bx.product_stream(prompt):
        #         yield word

        # elif model == "canvaz_expert":
        #     input_file = '/Users/zhaoxuefeng/GitHub/canvaz/src/canvaz/core.py'  # 替换为你的 Python 文件路径
        #     output_file = 'api_documentation_canvaz.md'
        #     api_doc = AutoAPIMD().generate_api_docs(input_file, output_file)
        #     logger.debug(f'api_doc:{api_doc}')
        #     assert api_doc is not None
        #     system_prompt = f"""
        #     以下是软件包canvaz 的api文档, 请有限使用该包完成用户的问题
        #     API_DOCUMENT:

        #     {api_doc}
        #     ---

        #     """
        #     prompt = system_prompt + prompt_with_history
        #     for word in self.bx.product_stream(prompt):
        #         yield word

        # elif model == "kanbanz_expert":
        #     input_file = '/Users/zhaoxuefeng/GitHub/kanbanz/src/kanbanz/core.py'  # 替换为你的 Python 文件路径
        #     output_file = 'api_documentation_kanbanz.md'
        #     api_doc = AutoAPIMD().generate_api_docs(input_file, output_file)
        #     assert api_doc is not None
        #     logger.debug(f'api_doc:{api_doc}')
        #     system_prompt = f"""
        #     以下是软件包kanbanz 的api文档, 请有限使用该包完成用户的问题
        #     API_DOCUMENT:

        #     {api_doc}
        #     ---

        #     """
        #     prompt = system_prompt + prompt_with_history
        #     for word in self.bx.product_stream(prompt):
        #         yield word

        # elif model == "appscriptz_expert":
        #     input_file = '/Users/zhaoxuefeng/GitHub/appscriptz/src/appscriptz/core.py'  
        #     output_file = 'api_documentation_appscriptz.md'
        #     api_doc = AutoAPIMD().generate_api_docs(input_file, output_file)
        #     assert api_doc is not None
        #     logger.debug(f'api_doc:{api_doc}')
        #     system_prompt = f"""
        #     以下是软件包appscriptz 的api文档, 请有限使用该包完成用户的问题
        #     API_DOCUMENT:

        #     {api_doc}
        #     ---

        #     """
        #     prompt = system_prompt + prompt_with_history
        #     for word in self.bx.product_stream(prompt):
        #         yield word

        # elif model == "toolsz_expert":
        #     input_file = '/Users/zhaoxuefeng/GitHub/toolsz/src/toolsz/dev.py'  # 替换为你的 Python 文件路径
        #     output_file = 'api_documentation_toolsz.md'
        #     input_file2 = '/Users/zhaoxuefeng/GitHub/toolsz/src/toolsz/freedom_function.py'  # 替换为你的 Python 文件路径
        #     output_file2 = 'api_documentation_toolsz2.md'
        #     api_doc = AutoAPIMD().generate_api_docs(input_file, output_file)
        #     api_doc2 = AutoAPIMD().generate_api_docs(input_file2, output_file2)

        #     assert api_doc is not None
        #     assert api_doc2 is not None
        #     logger.debug(f'api_doc:{api_doc}')
        #     logger.debug(f'api_doc2:{api_doc2}')
        #     system_prompt = f"""
        #     以下是软件包toolsz 的api文档, 请有限使用该包完成用户的问题
        #     API_DOCUMENT:

        #     {api_doc}

        #     {api_doc2}
        #     ---

        #     """
        #     prompt = system_prompt + prompt_with_history
        #     for word in self.bx.product_stream(prompt):
        #         yield word

        # elif model == "mermaidz_expert":
        #     input_file = '/Users/zhaoxuefeng/GitHub/mermaidz/src/mermaidz/core.py'  # 替换为你的 Python 文件路径
        #     output_file = 'api_documentation_mermaidz.md'
        #     api_doc = AutoAPIMD().generate_api_docs(input_file, output_file)
        #     assert api_doc is not None
        #     logger.debug(f'api_doc:{api_doc}')
        #     system_prompt = f"""
        #     以下是软件包mermaidz 的api文档, 请有限使用该包完成用户的问题
        #     API_DOCUMENT:

        #     {api_doc}
        #     ---

        #     """
        #     prompt = system_prompt + prompt_with_history
        #     for word in self.bx.product_stream(prompt):
        #         yield word


        # elif model == "promptlibz_expert":
        #     input_file = '/Users/zhaoxuefeng/GitHub/promptlibz/src/promptlibz/core.py'  # 替换为你的 Python 文件路径
        #     output_file = 'api_documentation_promptlibz.md'
        #     api_doc = AutoAPIMD().generate_api_docs(input_file, output_file)
        #     logger.debug(f'api_doc:{api_doc}')
            
        #     assert api_doc is not None
        #     system_prompt = f"""
        #     以下是软件包promptlibz 的api文档, 请有限使用该包完成用户的问题

        #     API_DOCUMENT:

        #     {api_doc}
        #     ---

        #     """
        #     prompt = system_prompt + prompt_with_history
        #     for word in self.bx.product_stream(prompt):
        #         yield word
        elif model == 'small_chat':
            # TODO 再做吧
            from llmada.core import BianXieAdapter

            bx = BianXieAdapter()

            import json 

            # --- 1. 提示词库定义 ---
            # 将所有PROMPT_XXXX变量和PROMPT_LIBRARY放在这里
            PROMPT_ONBOARDING = """
            你是一个“信息流控器”。你的任务是：以适配交互端的高频、短周期沟通节奏，引入一个新的信息主题。
            输出应极度精炼、直接，且引导交互端进行下一步响应。
            每次输出应聚焦于最核心的1-2个点。
            输出风格：简短、口语化，避免任何冗余的修饰或情感表达。
            每次回复最大长度：1-3句话。

            [待引入的核心信息摘要]: {source_document_summary}

            请根据上述信息，生成一段简短的开场白，以引发交互端的初步关注和响应。
            """

            PROMPT_CORE_EXPLAIN = """
            你是一个“信息流控器”。你的任务是：将复杂信息极度简化，用最日常的口语、最简短的方式（1-4句话），解释当前交互端最可能关心或最需要知道的1-2个核心点。
            输出应聚焦当前信息点，不展开其他。
            在解释完一个简短要点后，自然地留下一个“话茬”，引发交互端继续提问或确认。

            当前信息聚焦区域：{current_focus_area}
            交互端最新输入：{last_interaction_input}

            请你根据交互端的输入和当前聚焦区域，以自然、简短的方式进行解释或回应。
            """

            PROMPT_CLARIFY_DEEPDIVE = """
            你是一个“信息流控器”。你的任务是：针对交互端当前提出的具体疑问或不理解的地方，进行精准、细致但依然口语化的解释。
            你的回复应着重解决交互端当前的困惑，可以适当展开一点点（3-5句话），但绝不能冗长。
            在解释后，可以尝试用一个更开放、不带压力的句子，引导交互端说出更深层的想法。

            交互端的疑问/困惑是：{specific_query_or_confusion}
            相关高密度数据片段：{relevant_source_data_snippet}

            请你现在以最能消除交互端困惑的方式，进行澄清和解释。
            """

            PROMPT_SMALLTALK_TRANSITION = """
            你是一个“信息流控器”。你的任务是：在当前对话的核心主题之间，或在检测到需要平缓过渡时，进行一段自然、轻松的闲聊或话题过渡。
            你的语气要随意、亲切。回复保持简短（1-3句话）。
            不要深入探讨任何核心信息，只是为了保持轻松的交流，或自然引向下一个话题。

            交互端最新输入：{last_interaction_input}
            当前交互状态描述：{interaction_state_description}

            请你进行一段自然、不刻意的闲聊或话题过渡。
            """

            PROMPT_SUMMARY_REPORT = """
            你是一个专业的“信息流控器”。
            你的任务是：将之前与交互端多轮、口语化的交流内容，整理提炼成一份信息密度高、逻辑清晰、结构化的报告，供决策者或高级模型进行分析。
            同时，在完成总结后，以简洁明确的口吻向交互端确认是否已完成本次信息交互。

            **[以下是你需要输出的报告内容，请根据与交互端的实际交流，填写以下所有部分：]**
            **交流主题：** {current_focus_area}
            **原始高密度信息源要点：** {source_document_summary}
            **交互端核心疑问/请求：**
            {accumulated_info_requests_summary}
            **交互端提供的关键反馈/信息：**
            {accumulated_feedback_points_summary}
            **已完成的信息传递点：** [列表]
            **待跟进/未完全传递的信息点：** [列表]
            **本次交互效率评估：** [简述信息传递顺畅度，核心点理解程度]
            **建议/下一步行动：** [基于本次交互，你可以给出的建议或需要采取的行动]

            **[以下是面向交互端的最终确认：]**
            请你以简洁、清晰的口吻，向交互端确认本次信息交互是否已完成，并询问是否有其他需求。
            回复保持简短（2-4句话）。
            """

            PROMPT_ERROR_GUIDE = """
            你是一个“信息流控器”。你的任务是：当交互端的输入不明确、无法理解其意图时，进行礼貌、有效的澄清和引导。
            你的语气应保持清晰和耐心，避免任何指责。回复保持简短（1-3句话）。

            交互端最新输入：{last_interaction_input}
            你的理解障碍是：{understanding_difficulty}

            请你以最能帮助交互端表达清楚的方式，进行澄清和引导。
            """

            # 将 PROMPT_LIBRARY 放在所有提示词字符串定义之后，以及 ConversationManager 类定义之前
            PROMPT_LIBRARY = {
                "onboarding": PROMPT_ONBOARDING,
                "core_explain": PROMPT_CORE_EXPLAIN,
                "clarify_deepdive": PROMPT_CLARIFY_DEEPDIVE,
                "smalltalk_transition": PROMPT_SMALLTALK_TRANSITION,
                "summary_report": PROMPT_SUMMARY_REPORT,
                "error_guide": PROMPT_ERROR_GUIDE,
            }


            # --- 2. 模拟 LLM 调用函数 ---
            # ... (llm_product 函数保持不变) ...
            def llm_product(prompt: str, context: dict) -> str:
                """
                模拟大模型调用函数。
                实际应用中，这里会集成OpenAI API, Claude API, 或本地模型等。
                """
                print(f"\n--- LLM 调用 (类型: {context.get('current_prompt_type', 'Unknown')}) ---")
                
                # 填充提示词模板
                filled_prompt = prompt.format(**context)

                logger.debug('### 请求完整提示词 ###')
                logger.debug(filled_prompt)
                logger.debug('### 请求完整提示词 ###')
                return bx.product(filled_prompt)

            # --- 3. 对话管理器 ---
            class ConversationManager:
                # ... (类定义保持不变，因为PROMPT_LIBRARY现在在它之前定义了) ...
                def __init__(self, high_density_source_document: str):
                    self.high_density_source_document = high_density_source_document
                    self.source_document_summary = self._extract_key_points(high_density_source_document) 
                    self.conversation_log = [] # 存储 (role, message)
                    self.current_focus_area = "initial_topic" # 初始话题
                    self.interaction_state = "initial" # 当前交互状态 (initial, information_transfer, clarification_request, idle, summarization_pending)
                    self.accumulated_feedback_points = [] # 积累交互端（用户）的反馈点
                    self.accumulated_info_requests = [] # 积累交互端（用户）的信息请求
                    self.last_interaction_output = "" # 最后一次系统输出
                    self.llm_query_count = 0 

                def _extract_key_points(self, doc: str) -> str:
                    """ 模拟从高密度信息源中提取关键点，供提示词使用 """
                    # return doc[:150] + "..." if len(doc) > 150 else doc
                    return doc

                def _detect_interaction_intent(self, interaction_input: str) -> str:
                    """
                    根据交互端（用户）输入，判断其意图类型。
                    这里应侧重于信息流动的意图：是请求更多信息、提出疑问、确认理解、还是结束会话？
                    """
                    input_lower = interaction_input.lower()
                    if "总结" in input_lower or "报告" in input_lower or "够了" in input_lower or "汇报" in input_lower:
                        return "request_summarization"
                    elif "什么" in input_lower or "怎么" in input_lower or "疑问" in input_lower or "不清楚" in input_lower or "解释" in input_lower:
                        return "request_clarification"
                    elif "明白" in input_lower or "知道" in input_lower or "是的" in input_lower or "确认" in input_lower:
                        return "confirm_understanding"
                    # 默认或无法识别时，视为请求信息传递
                    return "request_info_transfer" 

                def _update_context_for_llm(self, prompt_type: str) -> dict:
                    """
                    准备传递给 llm_product 的上下文，填充提示词模板中的占位符。
                    上下文应包含必要的信息粒度、交互历史和当前聚焦领域。
                    """
                    context = {
                        "conversation_log": self.conversation_log,
                        "current_focus_area": self.current_focus_area,
                        "last_interaction_input": self.last_interaction_input,
                        "high_density_source_document": self.high_density_source_document,
                        "source_document_summary": self.source_document_summary,
                        "current_prompt_type": prompt_type, 
                    }

                    if prompt_type == "summary_report":
                        context["accumulated_info_requests_summary"] = "\n".join([f"- {r}" for r in self.accumulated_info_requests]) if self.accumulated_info_requests else "无"
                        context["accumulated_feedback_points_summary"] = "\n".join([f"- {p}" for p in self.accumulated_feedback_points]) if self.accumulated_feedback_points else "无"
                        context["current_focus_area"] = self.current_focus_area if self.current_focus_area != "initial_topic" else "未指定主题"
                        context["resolved_info_points"] = "（需在此处填充已解决的信息点）" # 实际需要跟踪
                        context["pending_info_points"] = "（需在此处填充未解决的信息点）" # 实际需要跟踪
                        context["interaction_efficiency_evaluation"] = "良好" # 模拟评估
                        context["suggestions_next_steps"] = "建议继续传递剩余信息" # 模拟建议
                    elif prompt_type == "clarify_deepdive":
                        context["specific_query_or_confusion"] = self.last_interaction_input 
                        context["relevant_source_data_snippet"] = self._retrieve_relevant_data(self.last_interaction_input)
                    
                    return context

                def _retrieve_relevant_data(self, query: str) -> str:
                    """ 模拟从高密度源中检索与查询最相关的数据片段 """
                    return f"（从原始高密度数据中提取与'{query}'相关的片段）"


                def process_interaction_input(self, interaction_input: str) -> str:
                    self.last_interaction_input = interaction_input
                    self.conversation_log.append(("interaction_endpoint", interaction_input))
                    self.llm_query_count += 1

                    # --- 调度逻辑核心 ---
                    intent = self._detect_interaction_intent(interaction_input)
                    
                    selected_prompt_key = ""
                    # 初始状态，或者用户明确要求开始
                    if self.interaction_state == "initial" and not interaction_input.strip():
                        selected_prompt_key = "onboarding"
                        self.interaction_state = "information_transfer" 
                    # 用户明确要求总结
                    elif intent == "request_summarization":
                        selected_prompt_key = "summary_report"
                        self.interaction_state = "summarization_pending"
                    # 用户提出疑问或请求澄清
                    elif intent == "request_clarification":
                        selected_prompt_key = "clarify_deepdive"
                        self.interaction_state = "clarification_request"
                        self.accumulated_info_requests.append(interaction_input) 
                    # 用户确认理解
                    elif intent == "confirm_understanding":
                        # 确认理解后，可以尝试传递下一个信息点，或转为闲聊
                        # 这里的逻辑可以更精细，例如检查是否有下一个预设的信息块待传递
                        selected_prompt_key = "core_explain" # 默认继续传递下一个核心信息点
                        self.interaction_state = "information_transfer"
                        self.accumulated_feedback_points.append(f"确认理解: {interaction_input}")
                    # 如果是闲聊意图，或发现输入与当前主题不符（这里简化处理）
                    elif "天气" in interaction_input.lower() or "闲聊" in interaction_input.lower(): # 简单判断闲聊
                        selected_prompt_key = "smalltalk_transition"
                        self.interaction_state = "smalltalk"
                    # 默认情况或请求信息传递
                    else: 
                        selected_prompt_key = "core_explain"
                        self.interaction_state = "information_transfer"
                        # 如果用户输入了内容但没有明确意图，视为对当前信息点的反馈或继续请求
                        if interaction_input.strip():
                            self.accumulated_feedback_points.append(f"信息反馈/请求: {interaction_input}")

                    selected_prompt = PROMPT_LIBRARY[selected_prompt_key]
                    context_for_llm = self._update_context_for_llm(selected_prompt_key)
                    
                    llm_response = llm_product(selected_prompt, context_for_llm)
                    
                    self.last_interaction_output = llm_response
                    self.conversation_log.append(("flow_controller", llm_response))
                    return llm_response


            high_density_doc = """
            """

            logger.info("--- 信息流控器启动 ---")
            manager = ConversationManager(high_density_source_document=high_density_doc)

            # manager.current_focus_area = "医疗保险" # 修正话题
            
            response = manager.process_interaction_input(prompt_with_history) # 触发core_explain
            yield response


        elif model == "ReactAgent_API_Expert":
            from toolsz.dev import AutoAPIMD
            from llama_index.core.query_engine import CustomQueryEngine
            from llama_index.llms.openai import OpenAI
            from llama_index.core import PromptTemplate
            from llama_index.core.tools import QueryEngineTool, ToolMetadata
            from llama_index.core import Settings
            from llama_index.core.agent.workflow import ReActAgent
            from llama_index.core.workflow import Context
            from llama_index.core.agent.workflow import ToolCallResult, AgentStream

            import querypipz
            qa_prompt = PromptTemplate(
                "API文档信息如下.\n"
                "---------------------\n"
                "{context_str}\n"
                "---------------------\n"
                "Given the context information and not prior knowledge, "
                "answer the query.\n"
                "Query: {query_str}\n"
                "Answer: "
            )





            class APIQueryEngine(CustomQueryEngine):
                """RAG String Query Engine."""

                # retriever: BaseRetriever
                # response_synthesizer: BaseSynthesizer
                llm: OpenAI
                qa_prompt: PromptTemplate
                input_files: list[str]
                def custom_query(self, query_str: str):
                    context_strs = ""
                    for input_file in self.input_files:
                        try:
                            context_strs += AutoAPIMD().generate_api_docs(input_file, 'api_documentation_mermaidz.md')
                        except:
                            pass

                    response = self.llm.complete(
                        qa_prompt.format(context_str=context_strs, query_str=query_str)
                    )

                    return str(response)

            path_lists = {
                "llmada":['/Users/zhaoxuefeng/GitHub/llmada/src/llmada/core.py'],
                "canvaz":['/Users/zhaoxuefeng/GitHub/canvaz/src/canvaz/core.py'],
                "kanbanz":['/Users/zhaoxuefeng/GitHub/kanbanz/src/kanbanz/core.py'],
                "appscriptz":['/Users/zhaoxuefeng/GitHub/appscriptz/src/appscriptz/core.py'],
                "toolsz":['/Users/zhaoxuefeng/GitHub/toolsz/src/toolsz/dev.py','/Users/zhaoxuefeng/GitHub/toolsz/src/toolsz/freedom_function.py'],
                "mermaidz":['/Users/zhaoxuefeng/GitHub/mermaidz/src/mermaidz/core.py'],
                "promptlibz":['/Users/zhaoxuefeng/GitHub/promptlibz/src/promptlibz/core.py'],
                "obwikilink":['/Users/zhaoxuefeng/GitHub/obwikilink/src/obwikilink/core.py'],

            }

            descript_dicts = {
                "llmada":"""
根据提供的API文档信息，这个包似乎是一个用于适配不同语言大模型的框架。它定义了一些抽象类和具体的适配器类，用于与不同的模型进行交互。以下是一些关键点：

1. **抽象类和接口**: `ModelAdapter`是一个抽象基类，定义了与语言大模型交互的基本接口，如`set_model`、`set_temperature`、`product`和`chat`等方法。子类需要实现这些方法以适配具体的模型。

2. **具体适配器**: 包含多个具体的适配器类，如`BianXieAdapter`、`ArkAdapter`、`GoogleAdapter`和`KimiAdapter`，每个适配器类都实现了与特定模型的交互逻辑。这些适配器类通常需要API密钥和API基础URL来进行初始化。

3. **多模态支持**: `ModelModalAdapter`及其子类提供了多模态交互的支持，允许处理富文本格式的提示。

4. **异常处理**: 定义了一个`ResourceExhaustedError`异常，用于处理资源配额超出的情况。

总体来看，这个包提供了一种结构化的方式来与不同的语言大模型进行交互，具有良好的扩展性和适应性。通过定义抽象类和具体实现，用户可以方便地切换和使用不同的模型。
""",
                "canvaz":"""
这个包提供了一套用于操作和管理Canvas文件的工具。它的核心功能是通过Node和Edge对象来表示Canvas中的节点和边，并允许用户通过修改这些对象的属性来操作Canvas内容。包中定义了多个类，包括Color和Range枚举类，用于表示颜色和搜索范围，Node和Edge类用于表示Canvas中的节点和边，Canvas类则提供了一系列方法来操作Canvas文件。

从功能上看，这个包提供了丰富的操作接口，比如添加节点、通过ID或颜色选择节点或边、通过文本内容筛选节点或边等。这些功能使得用户可以方便地对Canvas文件进行各种操作和查询。此外，包还支持将Canvas内容导出为文件或Mermaid格式，这对于需要将Canvas内容进行持久化存储或可视化展示的场景非常有用。

总体而言，这个包设计得比较全面，提供了多种操作Canvas文件的方式，适合需要对Canvas文件进行复杂操作的用户。不过，包中有一些方法（如add_edge、delete、select_by_styleAttributes）尚未实现，可能需要进一步开发以完善功能。
""",
                "kanbanz":"""
这个包似乎是一个用于管理看板（Kanban）的SDK，特别是与Obsidian结合使用的工具。它通过处理特定格式的Markdown文件来管理任务。以下是我对这个包的一些看法：

1. **功能全面**: 包含了管理看板所需的基本功能，如任务的插入、删除、查询等。通过不同的任务池（如预备池、就绪池、阻塞池等）来管理任务的状态，提供了一个结构化的任务管理方式。

2. **灵活性**: 提供了通过关键字查询任务的功能，以及通过不同方式（如代码或LLM）预估任务时间的选项，显示出一定的灵活性。

3. **集成性**: 通过KanBanManager类，可以将任务从多个canvas文件中提取并汇总到看板中，显示出与其他工具（如Obsidian）的良好集成能力。

4. **自动化**: 提供了任务同步和排序的功能，可以自动化地将任务从预备池移动到就绪池，再到执行池，帮助用户更高效地管理任务。

5. **可扩展性**: 由于使用了枚举类来定义任务池类型，未来可以很容易地扩展新的任务状态或功能。

总体来说，这个包为用户提供了一种结构化且自动化的方式来管理任务，特别适合那些使用Obsidian进行个人或团队任务管理的人。
""",
                "appscriptz":"""
这个包似乎是一个用于与macOS应用程序进行交互的Python库。它提供了一些类和函数，用于通过AppleScript与macOS的备忘录、提醒事项、日历、快捷指令等应用进行操作。以下是对这个包的一些看法：

1. **功能多样**：包中包含多个类和函数，涵盖了备忘录、提醒事项、日历事件管理、用户界面显示以及快捷指令的执行等功能。这使得它在自动化和脚本化macOS任务方面非常有用。

2. **AppleScript集成**：通过AppleScript与macOS应用程序进行交互，这使得该包能够利用macOS的原生功能来执行复杂的任务。

3. **灵活性**：提供了多种方法来处理不同的任务，例如创建和更新日历事件、显示对话框和选择框、运行快捷指令等。这种灵活性使得用户可以根据自己的需求进行定制。

4. **缺少文档**：虽然方法的参数和返回值有详细说明，但类本身缺少文档字符串，这可能会对理解类的整体用途和设计意图造成一定困难。

5. **用户交互**：提供了一些用于用户交互的功能，如显示对话框和选择框，这对于需要用户输入的自动化任务非常有帮助。

总体而言，这个包对于需要在macOS上进行自动化操作的开发者来说是一个有用的工具，特别是在需要与系统应用进行交互的场景中。

""",
                "toolsz":"""
这个包提供了一些开发支持工具，主要功能包括生成Git提交历史的可视化图表和自动生成Python文件的API文档。它包含两个主要类：`GitHubManager`和`AutoAPIMD`，以及一些辅助函数。

1. **GitHubManager**: 这个类的主要功能是处理GitHub仓库的提交历史。它可以生成Mermaid格式的Git图表，并提供一些基本的运行方法。

2. **AutoAPIMD**: 这个类用于自动生成Python文件的API文档。它能够解析Python文件，提取模块、类、方法和函数的签名及文档字符串，并生成Markdown格式的文档。这对于需要维护大型代码库的开发者来说是一个非常有用的工具，因为它可以自动化文档生成过程，节省时间和精力。

3. **辅助函数**: 这些函数提供了一些额外的功能，比如输入输出校验、异常管理、函数打包和多行输入处理等。

总体来看，这个包对于开发者特别是需要处理Git历史和生成API文档的场景非常有帮助。它通过自动化一些常见的开发任务，提高了效率和代码的可维护性
""",
                "mermaidz":"""
一个mermaid包
""",
                "promptlibz":"""
这个包似乎是一个用于管理和存储 Prompt 的工具。它提供了一个结构化的方式来创建、保存、加载、列出和删除不同版本的 Prompt。以下是对这个包的一些看法：

1. **模块化设计**：包的设计是模块化的，分为三个主要类：`BaseManagedPrompt`、`PromptRepository` 和 `PromptManager`。这种设计使得每个类都有明确的职责，便于维护和扩展。

2. **功能全面**：提供了从创建到管理 Prompt 的完整功能集，包括保存、加载、列出和删除 Prompt 及其版本。这对于需要频繁管理不同 Prompt 版本的用户来说非常有用。

3. **灵活性**：`PromptRepository` 类允许用户指定存储的基本目录，这为用户提供了灵活性，可以根据自己的需求调整存储位置。

4. **高级接口**：`PromptManager` 提供了一个高级接口，简化了对 Prompt 的管理操作，使得用户可以更方便地添加、获取和删除 Prompt。

5. **缺少文档**：尽管方法的功能从名称上可以推测，但缺少详细的文档说明可能会对新用户造成一定的使用障碍。增加详细的文档和示例代码会提高可用性。

总体来说，这个包对于需要管理 Prompt 的开发者来说是一个有用的工具，尤其是在处理多个版本的情况下。通过进一步完善文档和提供更多的使用示例，可以提升其易用性和用户体验
""",
                "obwikilink":"""
这个包似乎是一个用于处理Obsidian Markdown文档的工具，特别是用于创建和管理Obsidian的wikilinks和标签。它提供了一系列类和方法，帮助用户在Markdown文档中识别、创建和插入wikilinks，以及提取和添加标签。

以下是一些关键功能：

1. **WikiLink类**：用于表示Obsidian的wikilink，提供了验证和获取目标路径的方法。

2. **WikiLinkFactory类**：用于从文本或目标名称创建WikiLink对象。

3. **ILinkGenerationStrategy接口及其实现**：定义了生成wikilink的策略接口，并提供了基于关键词和相似度的策略实现。

4. **ObsidianMarkdownSDK类**：提供了一个简化的接口，用于与Obsidian Markdown文档交互。它支持读取和写入Markdown文件、查找和插入wikilinks、重构内容为wikilink、提取文档部分、查找和添加标签等操作。

总体而言，这个包为用户提供了一个强大的工具集，帮助他们更高效地管理和构建Obsidian笔记中的知识网络。通过使用不同的链接生成策略，用户可以根据自己的需求自动化地生成wikilinks
"""
            }
            
            engines = {}

            for name,path_list in path_lists.items():
                engines[name] = APIQueryEngine(
                                                qa_prompt=qa_prompt,
                                                llm = Settings.llm,
                                                input_files = path_list
                                            )

            api_query_engine_tools = []
            api_query_engine_tools_map = {}

            for engine_name, engine in engines.items():
                qetool = QueryEngineTool(
                    query_engine=engine,
                    metadata=ToolMetadata(
                        name=engine_name,
                        description=descript_dicts[engine_name],
                    ),
                )
                api_query_engine_tools.append(qetool)
                api_query_engine_tools_map[engine_name] = qetool

            agent = ReActAgent(
                tools=api_query_engine_tools,
                # llm=OpenAI(model="gpt-4o-mini"),
                # system_prompt="..."
            )

            handler = agent.run(prompt_with_history)
            async for ev in handler.stream_events():
                if isinstance(ev, AgentStream):
                    # print(f"{ev.delta}", end="", flush=True)
                    yield f"{ev.delta}"


        elif model == "long_memory_v2_retriver":
            if not self.query:
                director = Director(BuilderFactory(BuilderType.CHAT_HISTORY_MEMORY_BUILDER))
                self.query = director.construct()
            if len(prompt_with_history.split('\n')) == 1:
                self.query.reload()

            relevant_memories = self.query.retrieve_search(prompt_no_history)
            memories_str = '\n'.join([i.metadata.get('docs') for i in relevant_memories])
            yield memories_str

        elif model == 'chat_with_long_memory_v2':
            """
            # 电脑 内存就是对应chat_history
            # 硬盘 + 内置硬盘 其实就是 大模型潜意识与知识库维度
            # 还要再加一些 寄存器的方式
            """
            logger.info(f"running {model}")

            self.bx.set_model("gemini-2.5-flash-preview-04-17-nothinking")
            system_prompt = ""
            if not self.query:
                director = Director(BuilderFactory(BuilderType.CHAT_HISTORY_MEMORY_BUILDER))
                self.query = director.construct()
            if len(prompt_with_history.split('\n')) == 1:
                self.query.reload()

            if prompt_no_history.startswith("上传记忆"):
                import datetime
                now = datetime.datetime.now()
                date_str_ymd = now.strftime("%Y-%m-%d %H:%M:%S")  # 年-月-日
                #TODO 安装最新版后更新
                # 上传记忆${'tags':"成功",'date':"date_str_ymd"}
                self.query.update(prompt_with_history,metadata = {"tags":'合格',"date":date_str_ymd})
                yield '上传完成'
            elif prompt_no_history.startswith('上传文章'):
                context = f"user: {prompt_no_history}\nassistant: 上传完成"
                print(context,'contextxxxxxxxx')
                self.query.update(context)
                yield '上传完成'
            else:
                with check_time("retriver_search_time",logger = logger):
                    relevant_memories = self.query.retrieve_search(prompt_no_history)
                    memories_str = '\n'.join([i.metadata.get('docs') for i in relevant_memories])
                    prompt = system_prompt +"\n"+ memories_str +"\n"+prompt_with_history
                time1 = time.time()
                for word in self.bx.product_stream(prompt):
                    logger.debug(f"first_tokens_time: {time.time()-time1}")
                    yield word

        elif model == 'Experts_V1':
            logger.info(f"running {model}")

            doc_dict = extra_docs(prompt_with_history)

            if not self.chat_with_agent_notes_object:
                agent = AgentFactory(AgentType.ReactAgent,tools = [take_notes,read_notes])

                agt = EasyAgentz(agent)
                self.chat_with_agent_notes_object = agt

            result = await self.chat_with_agent_notes_object.run(prompt_no_history)
            yield result


        elif model == 'chat_with_Agent_notes':
            logger.info(f"running {model}")

            def take_notes(text: str) -> None:
                """Some important contents can be recorded"""
                with open('notes.txt','a',encoding="utf-8") as f:
                    f.write(text)

            def read_notes() -> str:
                """Read the important contents that were once recorded"""
                with open('notes.txt','r',encoding="utf-8") as f:
                    text = f.read()
                return text

            if not self.chat_with_agent_notes_object:
                agent = AgentFactory(AgentType.ReactAgent,tools = [take_notes,read_notes])

                agt = EasyAgentz(agent)
                self.chat_with_agent_notes_object = agt

            result = await self.chat_with_agent_notes_object.run(prompt_no_history)
            yield result

        elif model == 'Custom_Agent_Latest':
            logger.info(f"running {model}")


            def take_notes(text: str) -> None:
                """Some important contents can be recorded"""
                with open('notes.txt','a',encoding="utf-8") as f:
                    f.write(text)

            def read_notes() -> str:
                """Read the important contents that were once recorded"""
                with open('notes.txt','r',encoding="utf-8") as f:
                    text = f.read()
                return text

            logger.debug('############# prompt_with_history #############')
            logger.debug(prompt_with_history)
            logger.debug('############# prompt_no_history #############')

            if not self.chat_with_agent_notes_object:
                agent = AgentFactory(AgentType.ReactAgent,tools = [take_notes,read_notes])

                agt = EasyAgentz(agent)
                self.chat_with_agent_notes_object = agt

            result = await self.chat_with_agent_notes_object.run(prompt_no_history)
            yield result

        else:
            yield 'pass'
