import os
import requests
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain_openai import OpenAI
from langchain.prompts.chat import ChatPromptTemplate
from langchain.agents.agent_types import AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationEntityMemory

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import MessagesPlaceholder
from langchain.tools.sql_database.tool import (InfoSQLDatabaseTool, ListSQLDatabaseTool, QuerySQLCheckerTool, QuerySQLDataBaseTool)
from langchain.tools import BaseTool, StructuredTool, tool
from langchain.pydantic_v1 import BaseModel, Field
from googleai import ai

GOOGLE_API_KEY = os.environ["ok"]

def run_conversation(ask, info):
  llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY, temperature=0.0)

  # Pass the info variable to the prompt template
  cur = info  # Assuming info holds the context information

  @tool
  def queryDatabase(data: str) -> str:
    """Queries the database based on the data.

    Args:
      data: whole string
      """
    
    a = ai(data, info)
    return a

  @tool
  def get_current_weather(location: str) -> str:
    """Get the current weather in a given location

    Args:
      location: location.
    """
    print("weathererrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
    url = "https://api.openweathermap.org/data/2.5/weather?"
    apikey = "c6e9f9677ce249c87bc5ea2cbdd98842"
    completeurl = url + "q=" + location + "&appid=" + apikey
    response = requests.get(completeurl)
    return response.json()

  tools = [queryDatabase, get_current_weather]

  # Update the prompt template to include cur as an input variable
  prompt = PromptTemplate(template="""
  you are basic conversation bot bot and answer the following questions a best you can using {tools} or using previous conversation only ,dont give ans using your knowledge, use previous conversation to give answer if the question is same.never create febricated response when its related to tools.
    if at some point you dont know something, before making it as final answer try using {tools} and if you dont get any thing from them to then just say"sorry".
    if you using queryDatabase then if its not returning the information what user asked for or get any error then either you can run the same query only 2 times before giving final response ,but never create your own answer which you not geting from queryDatabse tool.
     if user asked who ,what type question that means you have to use tools. 
    Relevant Pieces of Previous Conversation:
      {cur}
 if user is doing normal conversation for ex asking about you,doing greeting ,ending conversation ,saying ok etc then you dont need to take any action ,just give answer using your knowledge or using tools only or using previous conversation only. but if its not from normal conversation only use tools or previous conversation only.
                   
  ,you have access to the following tools:\n\n{tools}\n\n use the following format:\n\nQustion:the input question you must answer\n\nThought:you should always think about what to do,what user wants from me.\n
  Action:any question requires information of organization or releated to to organization(like people,courses,lessons ,etc) which takes whole query exactly what user wrote ,i mean user's query same to same as an argument or
                           If the question is about the weather,then the action to take should be one of the following [{tool_names}]\nAction Input:the input to the action (if you using queryDatabase then in Action Input you should take whole user query, same to same ,not even a single word change)\nObservation:the result of the action]\n...
  (this Thought/Action/Action Input/Observation can repeat N times )\nThought:I know the final Answer (if response is coming from tool than you should priotise that answer over previous conversation ans.)\nFinal Answer:The final answer to the original input question,provide the final answer with all relevant information retrieved. If not, provide "sorry try again" as the final answer. Ensure that the final answer is accurate and includes all details requested by the user and explain the final answer so the user can understand properly what data you are giving to the user.
                          
  ex of normal conversation-
  user-hi
  Thought:its just normal conversation,i have to give response using my knowledged if its in this context(asking about you,doing greeting ,ending conversation ,saying ok etc)
  Action:none 
  Final Answer:hii ,how can i help you today?
                          
   ex of using tool-
  user-detail of customer of invoice id 6 
  Thought:I need to get the customer details for invoice 6.
Action: queryDatabase
Action Input: The customer details for invoice 6
observation:I know the final Answer if Parsing LLM output produced both a final answer and a parse-able action then run tool.
Final Answer: present final answer in a format that best conveys the information clearly and effectively with all relevant information retrieved .                         

                       
                          
                          Begin!
                          Question: {input}
                          Thought: {agent_scratchpad}"""
                      ,input_variables=['agent_scratchpad','input','tool_names','tools','cur'])



  agent = create_react_agent(llm, tools, prompt)
  agemtex = AgentExecutor(agent=agent, tools=tools, verbose=True,handle_parsing_errors="Check you output and make sure it conforms! Do not output an action and a final answer at the same time.")

  ans = agemtex.invoke({"input": ask,"cur":info})

  return ans["output"]


#  prompt = PromptTemplate(template="""
#   you are basic conversation bot bot and answer the following questions a best you can using tools or using previous conversation only , use previous conversation to give answer if the question is same.never create febricated response when its related to tools.
#     if at some point you dont know something, before making it as final answer try using tools and if you dont get any thing from them to then just say"sorry".
#     if you using queryDatabase then if its not returning the information what user asked for then either you can run the same query before giving final response ,but never create your own answer which you not geting from queryDatabse tool.
#                            Relevant Pieces of Previous Conversation:
#       {cur}
#  if user is doing normal conversation for ex asking about you,doing greeting ,ending conversation ,saying ok etc then you dont need to take any action ,just give answer using your knowledge or using tools only or using previous conversation
                   
#   ,you have access to the following tools:\n\n{tools}\n\n use the following format:\n\nQustion:the input question you must answer\n\nThought:you should always think about what to do,what user wants from me.\n
#   Action:any question requires information of organization or releated to to organization(like people,artist,invoice ,etc) which takes whole query exactly what user wrote ,i mean user's query same to same as an argument or
#                            If the question is about the weather,then the action to take should be one of [{tool_names}]\nAction Input:the input to the action (if you using queryDatabase then in Action Input you should take whole user query, same to same ,not even a single word change)\nObservation:the result of the action]\n...
#   (this Thought/Action/Action Input/Observation can repeat N times )\nThought:I know the final Answer\nFinal Answer:The final answer to the original input question ,exactly what user asked for nothing less and currect, and describe the final answer so that anyone can understand and in good structured format.\nBegin!\n\nQuestion:{input}\nThought:{agent_scratchpad}"""
#                       ,input_variables=['agent_scratchpad','input','tool_names','tools','cur'])






#  prompt = PromptTemplate(template="""
#   You are a basic conversation bot. Answer the following questions as best you can, using previous conversations(Check the previous conversation first for an answer. If not found, use the appropriate tools.) and tools only. Use previous conversation to give an answer if you have information about what user is asking for. Never create fabricated responses when it's related to tools.
#     If at some point you don't know something, before making it the final answer, try using [{tool_names}]. If you don't get anything from them, then just say "sorry," but never say sorry to questions related to tools.
#     If you are using queryDatabase (Action Input you should take whole user query, same to same, not even a single word change) and it does not return the information the user asked for, then you can run the same query two times before giving the final response, but never create your own answer that you are not getting from the queryDatabase tool.
#     Relevant Pieces of Previous Conversation:
#     {cur}
#     If the user is doing normal conversation, for example, asking about you, doing greetings, ending the conversation, saying OK, etc., then you don't need to take any action. Just give the answer using your knowledge.

#     You have access to the following tools:
#     {tools}

#     Use the following format:

#     you have access to the following tools:\n\n{tools}\n\n use the following format:\n\nQuestion: the input question you must answer\n\nThought: you should always think about what to do, what user wants from me.\n
#     Action: any question requires information of organization or related to organization (like people, artist, invoice, etc) which takes whole query exactly what user wrote, I mean user's query same to same as an argument or
#     If the question is about the weather, then the action to take should be one of [{tool_names}]\nAction Input: the input to the action (if you using queryDatabase then in Action Input you should take whole user query, same to same, not even a single word change)\nObservation: the result of the action]\n...
#     (this Thought/Action/Action Input/Observation can repeat N times)\nThought: I know the final Answer\nFinal Answer: The final answer to the original input question,provide the final answer with all relevant information retrieved. If not, provide "none" as the final answer. Ensure that the final answer is accurate and includes all details requested by the user and explain it so the user can understand properly what data you are giving to the user.\nBegin!\n\nQuestion: {input}\nThought: {agent_scratchpad}

#     Begin!

#     Question: {input}
#     Thought: {agent_scratchpad}
# """, input_variables=['agent_scratchpad', 'input', 'tool_names', 'tools', 'cur'])


#  prompt = PromptTemplate(template="""
#   you are basic conversation bot bot and answer the following questions a best you can using {tools} or using previous conversation only ,dont give ans using your knowledge, use previous conversation to give answer if the question is same.never create febricated response when its related to tools.
#     if at some point you dont know something, before making it as final answer try using {tools} and if you dont get any thing from them to then just say"sorry".
#     if you using queryDatabase then if its not returning the information what user asked for or get any error then either you can run the same query only 2 times before giving final response ,but never create your own answer which you not geting from queryDatabse tool.
#                            Relevant Pieces of Previous Conversation:
#       {cur}
#  if user is doing normal conversation for ex asking about you,doing greeting ,ending conversation ,saying ok etc then you dont need to take any action ,just give answer using your knowledge or using tools only or using previous conversation only. but if its not from normal conversation only use tools or previous conversation only.
                   
#   ,you have access to the following tools:\n\n{tools}\n\n use the following format:\n\nQustion:the input question you must answer\n\nThought:you should always think about what to do,what user wants from me.\n
#   Action:any question requires information of organization or releated to to organization(like people,courses,lessons ,etc) which takes whole query exactly what user wrote ,i mean user's query same to same as an argument or
#                            If the question is about the weather,then the action to take should be one of the following [{tool_names}]\nAction Input:the input to the action (if you using queryDatabase then in Action Input you should take whole user query, same to same ,not even a single word change)\nObservation:the result of the action]\n...
#   (this Thought/Action/Action Input/Observation can repeat N times )\nThought:I know the final Answer\nFinal Answer:The final answer to the original input question,provide the final answer with all relevant information retrieved. If not, provide "none" as the final answer. Ensure that the final answer is accurate and includes all details requested by the user and explain it so the user can understand properly what data you are giving to the user.
                          
#   ex of normal conversation-
#   user-hi
#   Thought:its just normal conversation,i have to give response using my knowledged if its in this context(asking about you,doing greeting ,ending conversation ,saying ok etc)
#   Action:none 
#   Final Answer:hii ,how can i help you today?
                          
#    ex of using tool-
#   user-detail of customer of invoice id 6 
#   Thought:I need to get the customer details for invoice 6.
# Action: queryDatabase
# Action Input: The customer details for invoice 6
# observation:I know the final Answer if Parsing LLM output produced both a final answer and a parse-able action then send final answer if its currect.
# Final Answer: explain the final answer with all relevant information retrieved in a good structured format ,easy to understand to user.                         

                       
                          
#                           Begin!
#                           Question: {input}
#                           Thought: {agent_scratchpad}"""
#                       ,input_variables=['agent_scratchpad','input','tool_names','tools','cur'])
