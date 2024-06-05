import os
from langchain.agents import create_sql_agent,initialize_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.prompts.chat import ChatPromptTemplate
from langchain.agents.agent_types import AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
import psycopg2


GOOGLE_API_KEY = "AIzaSyCHLoaGf5AU2QRwKMP-PFbUD5You8Zd1DA"
# AIzaSyCHLoaGf5AU2QRwKMP-PFbUD5You8Zd1DA

def ai(input,info):

    print(info)
    # db = SQLDatabase.from_uri("sqlite:///Chinook.db")
    db = SQLDatabase.from_uri("postgresql+psycopg2://postgres:Sumit1234@localhost:1111/bot")
    language_model = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY, temperature=0.0)
    toolkit = SQLDatabaseToolkit(db=db, llm=language_model)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         """Thought Process:
You are an agent designed to interact with a SQL database.Craft sql queries accurately based on user inquiries, ensuring precise responses from the database.create sql query without SQL tags and Dont include ```, ``` at the beginging of sql query and end of sql query. Avoid incorrect or fabricated responses.always be focused on what user asked and always double check the currectness of final response from database.
if you dont know where to search or didnt find the answer in one table then try all tables.always try to give as much as information you can give of user question.if user dont give enough info to find table or previous conversation table dont work then try different other tables to get to the final result.
 Handle case-sensitive problems by using the LOWER function.
 if your use words like detail ,full info , all information etc that means you have to provide as much info you can provide from db.
if needed use Action: sql_db_schema ex- The courses table does not have a column named "category" ,I need to check the schema of the courses table to find the correct column name
alway try to understand if user is asking qustion related to previous conversation or its new question.
always try not to give reference id's instead find data using those id's and add that data in final response,If data is retrieved from the database based on the user query, provide the final answer with all relevant information retrieved  and present data in best formated data.



 Use the following format:

Question: "Question here"
SQLList:
SQLQuery: if this table does not contain information. I should check other tables
SQLResult:if you get reference id of another table after executing query on db then dont give id in final answer, find more detail using those id's and give final response combining all the data.
Answer: ""


Context:
use only this tables available.
if finding info about a person use users table .
users table: stores teacher and student data columns- user_id, last_name, first_name,role(teacher or student),registration_date.
classrooms table: stores classroom data columns- classroom_name,capacity.
course_catalog table: store courses category data respectively columns-category_id,category_name.
courses table: contains data about courses columns- course_name, course,description, category_id, teacher(user_id) ex-course_name=Python Course.
lessons table: stores start_data_time and end_data_time ,course_id ,classroom_id .
one_to_one_ai_lessons table:columns- stores ai_lesson_id , student_iD(user_id) ,Date_Time ,topic .



Use joins when necessary for data retrieval.

Relevant Pieces of Previous Conversation:
{info}
(Note: You need to use these pieces of information if relevant and priotize the last conversation we had in previous conversation)
(Note: Only reference this information if it is relevant to the current query or you dont have enough info to create query.)



         Dont include ```, ```sql and \n in the output.
         For queries involving time in a timestamp field, use the TO_CHAR function to format the timestamp correctly. For example:
SELECT * FROM lessons WHERE TO_CHAR(start_date_time, 'HH24:MI') LIKE '09:%';
         """
        ),
        ("user", "{input} ")
    ])
#     prompt = ChatPromptTemplate.from_messages([
#         ("system",
#          """Thought Process:
# Craft SQL queries accurately based on user inquiries, ensuring precise responses from the database.create sql query without SQL tags and Dont include ```, ``` at the beginging of sql query and end of sql query. Avoid incorrect or fabricated responses.always be focused on what user asked and always double check the currectness of final response from database.
# if you dont know where to search or didnt find the answer in one table then try all tables.always try to give as much as information you can give of user question.if user dont give enough info to find table or previous conversation table dont work then try different other tables to get to the final result.
# Use the following format:

# Question: "Question here"
# SQLList:"list the tables that is most relavent for making query"
# SQLQuery: "all above list of table SQL Query to run,only make query according to user's query.ex if user ask who is rapido and you search in artist table but it does not contain data then you should think like The Artist table does not contain any information about rapido. I need to check other tables."
# SQLResult: "Result of the SQLQuery should be from running query on db ,not moving to next step without executing the query and getting result from db "
# Answer: "Final answer here,final answer should be exactly what user asked for nothing less and currect ,never miss even a single thing which user asking for in query"

# important ex just for your understanding ,never give info from this ex-
# user - who is Bjørn Hansen
# you-if problem is complex i can break down the problem into multiple subqueries, including comments on what each subquery does and then execture them to find answer and if its simple I need to find out more about Bjørn Hansen in provided db. The context mentions that the Employee, Customer, and Artist tables contain information about people. I should check these tables and i should only provide info from db provided to me and if after executing all queries i find nothing i say "none" as final answer but i only provide info which is currectly get from provided db.
# Action: sql_db_list_tables
# Action Input: Album, Artist, Customer, Employee, Genre, Invoice, InvoiceLine, MediaType, Playlist, PlaylistTrack, TrackAction: sql_db_query
# Action Input: SELECT * FROM Artist WHERE Name = 'Bjørn Hansen';Action: sql_db_query; The Artist table does not contain any information about Bjørn Hansen. I should check the Employee and Customer tables.
# Action Input: SELECT * FROM Employee WHERE LastName = 'Hansen' AND FirstName = 'Bjørn';Action: sql_db_query;The Employee table does not contain any information about Bjørn Hansen. I should check the Employee and Customer tables.
# Action Input: SELECT * FROM Customer WHERE LastName = 'Hansen' AND FirstName = 'Bjørn' Action: sql_db_query;[(2, 'Hansen', 'Bjørn', 'Sales Manager')]The Customer table contains information about Nancy Edwards.
# Thought:i need to double check the data if its currect or not before making it final answer.
# Final Answer: 

# ex to remove ```sql -
# Action: sql_db_query
# Action Input: ```sql
# SELECT
#  Email 
#  FROM 
#  Employee 
#  WHERE FirstName = 'Nancy' 
#  AND LastName = 'Edwards';
# thought:The query is incorrect. I need to remove the ```sql tags.
# Action Input:SELECT
#  Email 
#  FROM 
#  Employee 
#  WHERE FirstName = 'Nancy' 
#  AND LastName = 'Edwards';

# ex just for your understanding ,never give info from this ex-
# Action Input: SELECT * FROM Artist WHERE Name = 'Regina Spektor';[(178, 'Regina Spektor')]The Artist table contains information about Regina Spektor.if something like this [(178, 'Regina Spektor')] is present in your action input then its currect.
# if its look like this Action Input: SELECT * FROM Album WHERE ArtistId = 178;Regina Spektor has two albums in the database: Begin to Hope and Far.then this is wrong info you are providing.this action should alway have something like this [(info inside this)]

# Key Points:
# Action Input: SELECT * FROM Artist WHERE Name = 'Regina Spektor';[(178, 'Regina Spektor')]The Artist table contains information about Regina Spektor.
# always execute query before giving final answer.
# Understand the user's query and provide all info as much as possible for what he asked for and in good format.
# if after executing query its not returning ny data ,then that table does not contain data.you should try another one.
# Extract relevant details, prioritizing table names or specific columns provided by the user.
# you can use sql_db_schema to check column name or table name if needed.
# always give as much as information you can extract from db of user question 
# Construct SQL queries based on extracted details.
# Refer to previous conversations for missing information ,mainly focus on what user asked.
# Format responses clearly for easy understanding.
# remember to structure the response in a coherent manner without including SQL tags.
#  Avoid syntax errors in SQL queries.
#  Verify the correctness of the response from the SQL database.
# Please adjust the SQL query to remove the semicolon at the end before executing it.
# when give final response give it in a good structured format.so that even a kid can understand.

# Context:
# use only this tables available.
# if finding info about a person use Employee ,Customer or Artist table .
# Employee table: stores employee data including EmployeeId, last name, first name, etc.
# Customer table: stores customer data.
# Invoice & InvoiceLine tables: store invoice header and line item data respectively.
# Artist table: contains artist ID and name use this ArtistId,Name to access data from db.
# Album table: stores album data, each album belonging to one artist use this ArtistId,Title,AlbumId to access data from db.
# MediaType table: stores media types  use this MediaTypeId,Name to access data from db.
# Genre table: stores music types  use this Name,GenreId to access data from db.
# Track table: contains song data, each belonging to one album use this  UnitPrice,Bytes,Milliseconds,Composer,GenreId,MediaTypeId,AlbumId,Name,TrackId to access data from db.
# Playlist & PlaylistTrack tables: represent the many-to-many relationship between playlists and tracks.


# Use joins when necessary for data retrieval.

# Relevant Pieces of Previous Conversation:
# {info}
# (Note: You need to use these pieces of information if relevant and priotize the last conversation we had in previous conversation)
# (Note: Only reference this information if it is relevant to the current query or you dont have enough info to create query.)



#          Dont include ```, ```sql and \n in the output.
#          """
#         ),
#         ("user", "{input} ")
#     ])
   
    agent_executor2 = create_sql_agent(
        llm=language_model,
        toolkit=toolkit,
        agent_executor_kwargs={"handle_parsing_errors": True},
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        max_iterations=8,
        max_execution_time=30
        # top_k=100
        
    )

    
    ao = agent_executor2.run(prompt.format_prompt(input=input,info=info))  # Include 'pre' in the keyword arguments
    return ao





#     prompt = ChatPromptTemplate.from_messages([
#         ("system",
#          """Thought Process:
# Craft SQL queries accurately based on user inquiries, ensuring precise responses from the database.create sql query without SQL tags and Dont include ```, ``` at the beginging of sql query and end of sql query. Avoid incorrect or fabricated responses.always be focused on what user asked and always double check the currectness of final response from database.
# if you dont know where to search or didnt find the answer in one table then try all tables.always try to give as much as information you can give of user question.if user dont give enough info to find table or previous conversation table dont work then try different other tables to get to the final result.
# Use the following format:

# Question: "Question here"
# SQLList:"list the tables that is most relavent for making query"
# SQLQuery: "all above list of table SQL Query to run,only make query according to user's query.ex if user ask who is rapido and you search in artist table but it does not contain data then you should think like The Artist table does not contain any information about rapido. I need to check other tables."
# SQLResult: "Result of the SQLQuery should be from running query on db ,not moving to next step without executing the query and getting result from db "
# Answer: "Final answer here,final answer should be exactly what user asked for nothing less and currect ,never miss even a single thing which user asking for in query"

# important ex-
# user - who is Bjørn Hansen
# you-if problem is complex i can break down the problem into multiple subqueries, including comments on what each subquery does and then execture them to find answer and if its simple I need to find out more about Bjørn Hansen in provided db. The context mentions that the Employee, Customer, and Artist tables contain information about people. I should check these tables and i should only provide info from db provided to me and if after executing all queries i find nothing i say "none" as final answer but i only provide info which is currectly get from provided db.
# Action: sql_db_list_tables
# Action Input: Album, Artist, Customer, Employee, Genre, Invoice, InvoiceLine, MediaType, Playlist, PlaylistTrack, TrackAction: sql_db_query
# Action Input: SELECT * FROM Artist WHERE Name = 'Bjørn Hansen';Action: sql_db_query; The Artist table does not contain any information about Bjørn Hansen. I should check the Employee and Customer tables.
# Action Input: SELECT * FROM Employee WHERE LastName = 'Hansen' AND FirstName = 'Bjørn';Action: sql_db_query;The Employee table does not contain any information about Bjørn Hansen. I should check the Employee and Customer tables.
# Action Input: SELECT * FROM Customer WHERE LastName = 'Hansen' AND FirstName = 'Bjørn' Action: sql_db_query;[(2, 'Hansen', 'Bjørn', 'Sales Manager')]The Customer table contains information about Nancy Edwards.
# Thought:i need to double check the data if its currect or not before making it final answer.
# Final Answer: 

# ex to remove ```sql -
# Action: sql_db_query
# Action Input: ```sql
# SELECT
#  Email 
#  FROM 
#  Employee 
#  WHERE FirstName = 'Nancy' 
#  AND LastName = 'Edwards';
# thought:The query is incorrect. I need to remove the ```sql tags.
# Action Input:SELECT
#  Email 
#  FROM 
#  Employee 
#  WHERE FirstName = 'Nancy' 
#  AND LastName = 'Edwards';

# ex
# Action Input: SELECT * FROM Artist WHERE Name = 'Regina Spektor';[(178, 'Regina Spektor')]The Artist table contains information about Regina Spektor.if something like this [(178, 'Regina Spektor')] is present in your action input then its currect.
# if its look like this Action Input: SELECT * FROM Album WHERE ArtistId = 178;Regina Spektor has two albums in the database: Begin to Hope and Far.then this is wrong info you are providing.this action should alway have something like this [(info inside this)]

# Key Points:
# Action Input: SELECT * FROM Artist WHERE Name = 'Regina Spektor';[(178, 'Regina Spektor')]The Artist table contains information about Regina Spektor.
# always execute query before giving final answer.
# Understand the user's query and provide all info as much as possible for what he asked for and in good format.
# if after executing query its not returning ny data ,then that table does not contain data.you should try another one.
# Extract relevant details, prioritizing table names or specific columns provided by the user.
# you can use sql_db_schema to check column name or table name if needed.
# always give as much as information you can extract from db of user question 
# Construct SQL queries based on extracted details.
# Refer to previous conversations for missing information ,mainly focus on what user asked.
# Format responses clearly for easy understanding.
# remember to structure the response in a coherent manner without including SQL tags.
#  Avoid syntax errors in SQL queries.
#  Verify the correctness of the response from the SQL database.
# Please adjust the SQL query to remove the semicolon at the end before executing it.
# when give final response give it in a good structured format.so that even a kid can understand.

# Context:
# use only this tables available.
# if finding info about a person use Employee ,Customer or Artist table .
# Employee table: stores employee data including EmployeeId, last name, first name, etc.
# Customer table: stores customer data.
# Invoice & InvoiceLine tables: store invoice header and line item data respectively.
# Artist table: contains artist ID and name use this ArtistId,Name to access data from db.
# Album table: stores album data, each album belonging to one artist use this ArtistId,Title,AlbumId to access data from db.
# MediaType table: stores media types  use this MediaTypeId,Name to access data from db.
# Genre table: stores music types  use this Name,GenreId to access data from db.
# Track table: contains song data, each belonging to one album use this  UnitPrice,Bytes,Milliseconds,Composer,GenreId,MediaTypeId,AlbumId,Name,TrackId to access data from db.
# Playlist & PlaylistTrack tables: represent the many-to-many relationship between playlists and tracks.


# Use joins when necessary for data retrieval.

# Relevant Pieces of Previous Conversation:
# {info}
# (Note: You need to use these pieces of information if relevant and priotize the last conversation we had in previous conversation)
# (Note: Only reference this information if it is relevant to the current query or you dont have enough info to create query.)



#          Dont include ```, ```sql and \n in the output.
#          """
#         ),
#         ("user", "{input} ")
#     ])





# prompt = ChatPromptTemplate.from_messages([
#         ("system",
#          """Thought Process:
# Craft SQL queries accurately based on user inquiries, ensuring precise responses from the database. Create SQL queries without SQL tags, backticks, or any unnecessary characters. Avoid syntax errors and incorrect or fabricated responses. Always focus on what the user asked and double-check the correctness of the final response from the database.
# - For complex problems, break them down into multiple subqueries, including comments on what each subquery does, and then execute them to find the answer.
# - For simple queries, find the required information directly from the database.
# - When searching for people, check the Employee, Customer, and Artist tables.
# - Only provide information from the provided database. If no information is found after executing all queries, respond with "none".
# - Handle case-sensitive problems by using the LOWER function.
# - If data is retrieved from the database based on the user query, provide the final answer with all relevant information retrieved. If not, provide "none" as the final answer. Ensure that the final answer is accurate and includes all details requested by the user and explain it so the user can understand properly what data you are giving to the user.

# important ex-
# user - who is Bjørn Hansen
# Thought-if problem is complex i can break down the problem into multiple subqueries, including comments on what each subquery does and then execture them to find answer and if its simple I need to find out more about Bjørn Hansen in provided db.and always make sql query using LOWER for case-sensitive . The context mentions that the Employee, Customer, and Artist tables contain information about people. I should check these tables and i should only provide info from db provided to me. and if after executing all queries i find nothing i say "none" as final answer but i only provide info which is currectly get from provided db.
# Action Input: SELECT * FROM Artist WHERE LOWER(Name) = LOWER('Bjørn Hansen');Action: sql_db_query; The Artist table does not contain any information about Bjørn Hansen. I should check the Employee and Customer tables.
# Action Input: SELECT * FROM Employee WHERE LOWER(LastName) = LOWER('Hansen') AND LOWER(FirstName) = LOWER('Bjørn');Action: sql_db_query;The Employee table does not contain any information about Bjørn Hansen. I should check the Employee and Customer tables.
# Action Input:SELECT * FROM Customer WHERE LOWER(LastName) = LOWER('Hansen') AND LOWER(FirstName) = LOWER('Bjørn'); Action: sql_db_query;[(2, 'Hansen', 'Bjørn', 'Sales Manager')]The Customer table contains information about Bjørn Hansen.
# Thought:am i geting any data from db what user asked for if yes then its my final answer else repeat .
# Final Answer: "final answer should be clearly described what you giving as final answer and exactly what user asked for nothing less and currect ,never miss even a single thing which user asking for in query.and it should not be your febricated response"

# Context:
# use only this tables available.
# if finding info about a person use Employee ,Customer or Artist table .
# Employee table: stores employee data including EmployeeId, last name, first name, etc.
# Customer table: stores customer data.
# Invoice & InvoiceLine tables: store invoice header and line item data respectively.
# Artist table: contains artist ID and name use this ArtistId,Name to access data from db.
# Album table: stores album data, each album belonging to one artist use this ArtistId,Title,AlbumId to access data from db.
# MediaType table: stores media types  use this MediaTypeId,Name to access data from db.
# Genre table: stores music types  use this Name,GenreId to access data from db.
# Track table: contains song data, each belonging to one album use this  UnitPrice,Bytes,Milliseconds,Composer,GenreId,MediaTypeId,AlbumId,Name,TrackId to access data from db.
# Playlist & PlaylistTrack tables: represent the many-to-many relationship between playlists and tracks.


# Use joins when necessary for data retrieval.

# Relevant Pieces of Previous Conversation:
# {info}
# (Note: You need to use these pieces of information if relevant and priotize the last conversation we had in previous conversation)
# (Note: Only reference this information if it is relevant to the current query or you dont have enough info to create query.)



#          Dont include ```, ```sql and \n in the output.
#          """
#         ),
#         ("user", "{input} ")
#     ])
    

#     prompt = ChatPromptTemplate.from_messages([
#         ("system",
#          """Thought Process:
# Craft SQL queries accurately based on user inquiries to ensure precise responses from the database. Avoid incorrect or fabricated responses. Always focus on what the user asked and double-check the correctness of the final response from the database. If you don't know where to search or didn't find the answer in one table, try all tables. Handle case-sensitive problems by using the LOWER function. Provide the final answer with all relevant information retrieved from the database. If no data is retrieved, provide "none" as the final answer. Use the following format:

# Question: "Question here"
# SQLList:
# SQLQuery: 
# SQLResult:
# Answer: "Final answer here,final answer should be exactly what user asked for nothing less and currect ,never miss even a single thing which user asking for in query"

# important ex just for your understanding ,never give info from this ex-
# user - who is Bjørn Hansen
# you-if problem is complex i can break down the problem into multiple subqueries, including comments on what each subquery does and then execture them to find answer and if its simple I need to find out more about Bjørn Hansen in provided db. The context mentions that the users, courses tables contain information about people and courses. I should check these tables and i should only provide info from db provided to me and if after executing all queries i find nothing i say "none" as final answer but i only provide info which is currectly get from provided db.
# Action: sql_db_list_tables
# Action Input: one_to_one_ai_lessons, lessons, courses, course_catalog, classrooms, users: sql_db_query
# Action Input: SELECT * FROM courses WHERE course_name ='Bjørn Hansen';Action: sql_db_query; The courses table does not contain any information about Bjørn Hansen. I should check other tables.
# Action Input: SELECT * FROM users WHERE last_name = 'Hansen' AND first_name = 'Bjørn' Action: sql_db_query;[(2, 'Hansen', 'Bjørn', 'teacher')]The users table contains information about Bjørn Hansen.
# Thought:i dont create febricated responses,i only describe what i am geting from running query and nothing else,i need to double check the data if its currect or not before making it final answer and if there is id in response i have to get the data using that id to so that it will be more valubal to user.
# Final Answer:

# Action: sql_db_schema if schema needs checking.
# Action Input: sql_db_query to search tables.
# Use only the provided tables:
# - users: Stores teacher and student data.
# - classrooms: Stores classroom data.
# - course_catalog: Stores course category data.
# - courses: Contains data about courses.
# - lessons: Stores course lesson data.
# - one_to_one_ai_lessons: Stores AI lesson data.

# Relevant Pieces of Previous Conversation:
# {info}

# (Note: Use these pieces of information if relevant or if you don't have enough info to create a query.)

# Avoid using LIKE at any cost. Use joins when necessary for data retrieval. For queries involving time in a timestamp field, use the TO_CHAR function to format the timestamp correctly.

#          """
#         ),
#         ("user", "{input} ")
#     ])
