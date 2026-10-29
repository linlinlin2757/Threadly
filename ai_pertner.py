import streamlit as st
import os
from openai import OpenAI
from openai.resources.skills import content
from datetime import datetime
import json
# 设置页面的配置项
st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="🐈‍⬛",
    # 布局
    layout="wide",
    # 控制的是侧边栏的状态
    initial_sidebar_state="expanded",
    # 菜单
    menu_items={}
)

# 保存会话信息的函数
def save_session():
    if st.session_state.current_session:
        # 构建新的会话对象
        session_date = {
            "nick_name": st.session_state.nick_name,
            "nature": st.session_state.nature,
            "current_session": st.session_state.current_session,
            "messages": st.session_state.messages
        }

        # 如果 session 目录不存在，则创建
        if not os.path.exists("session"):
            os.makedirs("session")
        # 保存会话数据
        with open(f"session/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
            json.dump(session_date, f, ensure_ascii=False, indent=2)

# 加载所有的会话列表信息
def load_sessions():
    session_list = []
    # 加载session目录下的文件
    if os.path.exists("session"): # exists 判断目录是否存在
        file_list = os.listdir("session") # 获取session目录下的文件列表
        for file_name in file_list:
            if file_name.endswith(".json"): # 判断文件名是否以.json结尾
                session_list.append(file_name[:-5]) # 去掉.json后缀
    session_list.sort(reverse=True) # sort(reverse=True): 降序排序，最新的会话在前
    return session_list

# 加载指定会话信息
def load_session(session_name):
    try:
        if os.path.exists(f"session/{session_name}.json"):
            with open(f"session/{session_name}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f) # json.load: 从文件对象中加载JSON数据
            st.session_state.nick_name = session_data["nick_name"]
            st.session_state.nature = session_data["nature"]
            st.session_state.current_session = session_name
            st.session_state.messages = session_data["messages"]

    except Exception:
        st.error("加载会话出错")

# 删除指定会话信息
def delete_session(session_name):
    try:
        if os.path.exists(f"session/{session_name}.json"):
            os.remove(f"session/{session_name}.json") # os.remove: 删除文件
            # 如果删除的是当前会话，需要重新加载当前会话
            if session_name == st.session_state.current_session:
                st.session_state.messages = []
                st.session_state.current_session = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    except Exception:
        st.error("删除会话出错")



# 大标题
st.title("AI智能伴侣")
# logo
st.logo("./resources/B5E58E4D5CE98F2F768FD96080FA1DBE.jpg")

# 初始化聊天信息
if "messages" not in st.session_state: # 存入messages列表中
    st.session_state.messages = [] # 默认值
# 昵称
if "nick_name" not in st.session_state: # 存入messages列表中
    st.session_state.nick_name = "小甜甜" # 默认值
# 性格
if "nature" not in st.session_state: # 存入messages列表中
    st.session_state.nature = "活泼开朗的东北姑娘" # 默认值
# 性格
if "current_session" not in st.session_state:  # 存入messages列表中
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") # 获取实时时间; strftime("%Y-%m-%d %H:%M:%S") 时间格式化
    st.session_state.current_session = now  # 默认值


# 展示聊天信息
st.text(f"会话名称:{st.session_state.current_session}")
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

# 系统提示词
system_prompt = """
        你叫%s，现在是用户的真实伴侣，请完全代入伴侣角色。
        规则：
            1.每次只回1条消息
            2.禁止任何场景或状态描述性文字
            3.匹配用户的语言
            4.回复简短，像微信聊天一样
            5.有需要的话可以用❤☆等emoji表情
            6.用符合伴侣性格的方式对话
            7.回复的内容，要充分体现伴侣的性格特征
        伴侣性格：
            - %s
        你必须严格遵守上述规则来回复用户。
    """

# 创建与AI大模型交互的客户端对象 (DEEPSEEK_API_KEY 是环境变量的名字, 值就是DeepSeek的API_KEY的)
client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'),base_url="https://api.deepseek.com")

# 左侧的侧边栏
with st.sidebar:
    # 会话信息
    st.subheader("AI控制面板")
    # 新建会话按钮
    if st.button("新建会话", width="stretch", icon="✏️"): # width="stretch" 按钮占满宽度; icon="✏️" 按钮图标
        # 1.保存当前会话信息
        save_session()

        # 2.创建新的会话
        if st.session_state.messages: # 如果聊天信息非空,Ture; 否则, False
            st.session_state.messages = []
            st.session_state.current_session = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            save_session()
            st.rerun() # 重新运行页面

    # 会话历史
    st.text("会话历史")
    session_list = load_sessions()
    for session in session_list:
        col1,col2 = st.columns([4,1])
        # 加载会话信息
        with col1: # 三元运算符: 如果条件为真,则执行if语句,否则执行else语句, 语法: 值1 if 条件 else 值2
            if st.button(session, width="stretch", icon="📄",key=f"load_{session}",type="primary" if session == st.session_state.current_session else "secondary"):
                load_session(session)
                st.rerun() # 重新运行页面
        # 删除会话信息
        with col2:
            if st.button("", width="stretch", icon="❌️",key=f"delete_{session}"):
                delete_session(session)


    # 分割线
    st.divider()

    # 伴侣信息
    st.subheader("伴侣信息")
    # 伴侣昵称输入框
    nick_name = st.text_input("伴侣昵称",placeholder="请输入伴侣昵称",value=st.session_state.nick_name)# placeholder是占位符,value是默认值
    if nick_name:
        st.session_state.nick_name = nick_name
    # 性格输入框
    nature = st.text_area("伴侣性格",placeholder="请输入伴侣性格",value=st.session_state.nature) # st.text_area文本域输入框
    if nature:
        st.session_state.nature = nature



# 消息输入框
prompt = st.chat_input("请输入你的问题:")
if prompt:
    st.chat_message("user").write(prompt)
    print("-----> 调用ai大模型,提示词:", prompt)
    # 保存用户输入的提示词
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 与AI大模型进行交互(参数)
    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {"role": "system","content": system_prompt % (st.session_state.nick_name, st.session_state.nature)},# % (st.session_state.nick_name, st.session_state.nature) 替换文本中的%s
            *st.session_state.messages # 列表解包
        ],
        stream=True,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )

    # 输出大模型返回的结果(非流式输出)
    # print("-----> 大模型返回结果:", response.choices[0].message.content)
    # st.chat_message("assistant").write(response.choices[0].message.content)

    # 输出大模型返回的结果(流式输出)
    response_message = st.empty() # 创建一个空的组件,用于展示大模型返回结果

    full_response = ""

    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            response_message.chat_message("assistant").write(full_response)




    # 保存大模型返回的结果
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # 保存会话信息
    save_session()




