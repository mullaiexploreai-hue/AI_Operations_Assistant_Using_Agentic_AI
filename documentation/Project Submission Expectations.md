Final Assessment Project: Submission & Expected Features
1. What Do You Need to Submit?
For the project you selected, submit:
Complete project/code directory as either: 
A ZIP file, or 
A GitHub repository 
requirements.txt with all required Python dependencies 
.env.example showing the required environment variables, without exposing actual API keys 
Sample input data required to run the application 
README.md with setup instructions, project structure, architecture, and steps to run the application 
The application should be runnable locally on the evaluator's system 
The original assessment also requires sufficient sample data so that the evaluator can run the project without creating data from scratch. 
What You Do NOT Need to Submit
No cloud deployment is required 
No live deployment URL is required 
No PPT or presentation is required 
No .env file containing actual API keys 
No venv or virtual environment folder 
No expensive or complex external infrastructure 

2. Project 1: AI-Powered Document Processing & Business Workflow
When we run your application, the following basic functionality should work:
The application should read multiple input documents from the designated input/data folder. 
It should support at least two document formats, such as PDF, DOCX or TXT. 
It should extract structured information from each document using an LLM and a defined schema. 
It should generate the required customer response/email and internal case summary from the extracted information. 
The workflow should demonstrate multiple processing steps, rather than putting everything into one large LLM call. 
The application should automatically process the available files and save the corresponding outputs in an output folder, including the consolidated report. 
These requirements are based on the document ingestion, structured extraction, response generation, workflow orchestration and batch-processing requirements. 

3. Project 2: Enterprise Knowledge Assistant with Advanced RAG
When we run your application, the following basic functionality should work:
The application should load the provided sample documents from a local folder and build the required RAG pipeline. 
Documents should be chunked, embedded and stored in a local vector database such as FAISS or ChromaDB. 
When a user asks a question, the system should perform retrieval, hybrid search and reranking before generating the answer. 
The application should maintain conversation context, so follow-up questions can be understood correctly. 
Answers should be grounded in the documents, with the relevant source documents displayed to the user. 
If the required information is not available in the provided documents, the application should clearly communicate that it was not found instead of inventing an answer. 
The assessment specifically expects advanced retrieval, memory, source citations, Streamlit interaction and hallucination handling. 

4. Project 3: AI Operations Assistant Using Agentic AI
When we run your application, the following basic functionality should work:
The application should understand the user's request and determine whether a tool is required. 
The agent should have at least three working tools, including knowledge search, ticket lookup and ticket creation. 
The agent should correctly select the appropriate tool and pass the required parameters. 
The workflow should demonstrate LangGraph state, nodes, edges and conditional routing. 
The agent should maintain relevant conversation state, including information collected across multiple interactions. 
The system should validate required information, handle tool failures and avoid duplicate or unsupported actions before executing operations. 
The assessment requires the agent to demonstrate actual tool calling, state management and conditional workflow execution, rather than simply describing these concepts. 

5. What We Expect From the Code
Across all three projects:
Focus on functional implementation, not the number of technologies used. 
Follow a clean and modular project structure. 
Use meaningful variable, function and file names. 
Avoid unnecessary hard-coded values. 
Add basic error handling and logging where appropriate. 
Use docstrings and comments where they improve understanding. 
Refactor repeated or unnecessarily complex code. 
Maintain a proper README.md so another person can understand and run the project. 
Make sure the project demonstrates your understanding of the implementation. 
The assessment is primarily focused on functional completeness, GenAI implementation, architecture, technical depth, code quality, error handling, UX, documentation and engineering practices. 
Key point: You are not expected to build an enterprise-grade production system. The expectation is that the core functionality of your selected project works correctly when we run it locally, and that you can explain what you have built and why.
