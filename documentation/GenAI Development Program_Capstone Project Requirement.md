GenAI Development Program
Final Evaluation Project – Batch 1
Assessment Overview
As part of the final assessment, learners are required to select ONE project from the three projects listed below and complete the project according to the specified requirements.
The objective of this assessment is to evaluate the learner’s ability to apply the concepts covered throughout the program to build a functional, well-structured and production-oriented GenAI application.
Important Guidelines
•	Learners may select any ONE of the three projects.
•	The project must be implemented primarily in Python.
•	The solution should run locally on the learner’s system.
•	Learners should use the GenAI frameworks and techniques covered during the program wherever applicable.
•	External paid services are not required.
•	Learners may use OpenAI/Gemini APIs if they have access, but the project should not depend on expensive or complex external infrastructure.
•	The submitted project should contain clean, modular and understandable code.
•	The learner should provide a README.md explaining the architecture, setup instructions, approach and how to run the application.
•	Learners should submit the complete source code along with sample input data and sample output.
•	The project should demonstrate the learner’s own understanding and implementation of the concepts.
•	Certification eligibility will be determined based on the quality, completeness and functionality of the submitted project.
________________________________________
Project 1 – AI-Powered Document Processing & Business Workflow
Project Objective
Build a GenAI-powered document processing workflow that automatically processes a collection of business documents and performs multiple AI-powered tasks on each document.
The objective is to demonstrate your ability to build a batch-oriented LLM workflow with structured outputs, parallel/sequential processing and automated content generation.
Suggested Business Scenario
Build an AI Customer Complaint & Case Processing System.
The system receives customer complaint documents from a local data/ folder and processes each document automatically.
Example input documents may contain:
•	Customer name
•	Contact information
•	Complaint description
•	Product/service involved
•	Issue details
•	Resolution provided
•	Escalation information
•	Supporting information
The documents can be .txt, .pdf or .docx files.
________________________________________
Functional Requirements
1. Document Ingestion
The application should:
•	Read documents from a designated data/ folder.
•	Support at least two document formats.
•	Process multiple documents in a batch.
•	Extract the textual content from each document.
•	Handle basic file-level errors gracefully.
2. Structured Information Extraction
For every document, the LLM should extract structured information such as:
•	Customer Name
•	Email
•	Phone Number
•	Complaint Category
•	Issue Description
•	Resolution Provided
•	Complaint: Yes/No
•	Escalation Required: Yes/No
•	Supporting Document Available: Yes/No
•	Overall Case Status
The output should follow a defined schema using Pydantic or another structured-output mechanism.
The application should not simply save the raw LLM response.
________________________________________
3. Automated Response Generation
For each complaint, generate a professional customer response email based on the extracted information.
The email should:
•	Address the customer appropriately.
•	Summarize the issue.
•	Mention the resolution/status.
•	Maintain a professional tone.
•	Avoid inventing information that is not present in the source document.
________________________________________
4. Management Case Summary
For each document, generate a concise internal case summary containing:
•	Case overview
•	Key issue
•	Action taken
•	Current status
•	Recommended next action
________________________________________
5. Workflow Design
The workflow should execute the three AI tasks:
Document → Structured Extraction
Document/Extracted Data → Customer Email
Document/Extracted Data → Internal Case Summary
The learner may implement the workflow sequentially or use parallel execution where appropriate.
The implementation should clearly demonstrate workflow orchestration rather than placing the entire application inside one large LLM call.
________________________________________
6. Batch Processing
The application should be capable of processing multiple documents automatically.
For example:
data/
├── complaint_001.pdf
├── complaint_002.pdf
├── complaint_003.txt
├── complaint_004.docx
└── complaint_005.pdf
The system should process all eligible files and produce corresponding outputs.
________________________________________
Expected Output
A recommended output structure:
output/
├── structured_data/
├── customer_emails/
├── case_summaries/
└── final_report.csv
The final report should provide a consolidated view of the processed documents.
________________________________________
Expected Technical Skills Demonstrated
The project should demonstrate:
•	Python
•	LLM API integration
•	Prompt Engineering
•	Structured Outputs
•	Pydantic
•	Batch Processing
•	Sequential/Parallel Workflow
•	Error Handling
•	Modular Code
•	File Processing
•	Git/GitHub
•	Basic logging
________________________________________
Project 2 – Enterprise Knowledge Assistant with Advanced RAG
Project Objective
Build a production-oriented RAG application that allows users to ask questions about a collection of private documents.
The objective is to demonstrate that you can build more than a basic “chat with PDF” application by implementing advanced retrieval techniques, conversation memory and a usable interface.
________________________________________
Suggested Business Scenario
Build an Employee Knowledge Assistant for a fictional organization.
The application should answer questions using a collection of company documents such as:
•	Employee policies
•	Leave policy
•	HR handbook
•	IT policies
•	Travel policy
•	Benefits documentation
•	Code of conduct
•	Company FAQs
All documents should be stored locally.
________________________________________
Functional Requirements
1. Document Ingestion
The system should:
•	Load documents from a local folder.
•	Support at least two document formats.
•	Split documents into appropriate chunks.
•	Generate embeddings.
•	Store embeddings in a local vector database.
Recommended options:
•	FAISS
•	ChromaDB
________________________________________
2. Basic Retrieval
Implement semantic/vector retrieval to identify relevant document chunks for a user query.
The application should return the most relevant context to the LLM before generating the final answer.
________________________________________
3. Hybrid Search
Implement Hybrid Search combining:
•	Vector/Semantic Search
•	Keyword-based Search such as BM25
The system should combine the results from both retrieval approaches.
________________________________________
4. Reranking
Implement a reranking step after initial retrieval.
The basic flow should be:
User Query → Retrieval → Candidate Documents → Reranking → Final Context → LLM
The purpose is to improve the relevance of the context provided to the LLM.
________________________________________
5. Conversational Memory
The application should remember relevant conversation history.
For example:
User: What is the leave policy?
AI: Employees receive…
User: What about carry-forward?
The system should understand that the second question refers to the previously discussed leave policy.
Learners may use the LangChain memory capabilities covered during the program.
________________________________________
6. Source Citations
The application should identify the source documents used to generate an answer.
For example:
Sources:
- Leave_Policy.pdf
- Employee_Handbook.pdf
The answer should be grounded in the retrieved documents.
________________________________________
7. User Interface
Build a simple and clean interface using:
•	Streamlit
The interface should support:
•	Chat interaction
•	Conversation history
•	Clear/reset conversation
•	Display of retrieved sources
•	Basic error messages
________________________________________
8. Hallucination Handling
The system should instruct the LLM to avoid making unsupported claims.
If the required information cannot be found in the available documents, the application should clearly communicate that the information was not found.
________________________________________
Expected Architecture
Documents
    ↓
Document Loader
    ↓
Chunking
    ↓
Embeddings
    ↓
Vector Store
    ↓
        ┌── Vector Search
Query ──┤
        └── Keyword/BM25 Search
                    ↓
              Hybrid Results
                    ↓
                Reranking
                    ↓
             Relevant Context
                    ↓
              LLM + Memory
                    ↓
          Grounded Answer + Sources
                    ↓
                Streamlit UI
________________________________________
Expected Technical Skills Demonstrated
The project should demonstrate:
•	Python
•	LangChain
•	RAG
•	Document Loaders
•	Chunking
•	Embeddings
•	FAISS/ChromaDB
•	Hybrid Search
•	BM25
•	Reranking
•	Conversation Memory
•	Prompt Engineering
•	Structured application architecture
•	Streamlit
•	Source Citation
•	Hallucination Mitigation
________________________________________
Project 3 – AI Operations Assistant Using Agentic AI
Project Objective
Build a basic Agentic AI assistant that can understand a user’s request, decide which tool is required, execute the appropriate tool and return the final response.
The objective is to demonstrate practical understanding of:
Tool Calling → Agent → State → Routing → Multi-Step Workflow
The project should remain intentionally realistic and achievable on a local machine.
________________________________________
Suggested Business Scenario
Build an AI IT Support Assistant for a fictional organization.
The assistant should help employees with common IT support requests.
The system will have access to a few local tools/data sources.
For example:
•	Employee information
•	IT issue/ticket database
•	Knowledge base
•	System status information
•	Ticket creation functionality
The data can be represented using simple JSON, CSV or SQLite files.
No real enterprise system integration is required.
________________________________________
Required Tools
The agent should have at least three tools.
Tool 1 – Knowledge Search
Search a local IT knowledge base.
Example:
User: How do I reset my VPN password?

Agent → Knowledge Search Tool
      → Finds relevant article
      → Generates answer
________________________________________
Tool 2 – Ticket Lookup
Search existing support tickets stored locally.
Example:
User: What is the status of my laptop issue?

Agent → Ticket Lookup Tool
      → Searches ticket data
      → Returns ticket status
________________________________________
Tool 3 – Ticket Creation
Create a new support ticket in a local JSON/SQLite database.
Example:
User: My VPN is not working. Please raise a ticket.

Agent → Collect required information
      → Create Ticket Tool
      → Generate ticket ID
      → Confirm creation
________________________________________
Agent Requirements
The agent should be able to:
•	Understand the user’s request.
•	Decide whether a tool is required.
•	Select the appropriate tool.
•	Pass appropriate parameters to the tool.
•	Process the tool response.
•	Generate a final user-friendly response.
________________________________________
LangGraph Requirement
Learners should use LangGraph for workflow orchestration.
The workflow should demonstrate:
•	State
•	Nodes
•	Edges
•	Conditional routing
•	Tool execution
•	Final response generation
A possible architecture:
User Query
    ↓
Intent / Decision Node
    ↓
Conditional Routing
    ├── Knowledge Search
    ├── Ticket Lookup
    └── Ticket Creation
             ↓
        Tool Result
             ↓
      Response Generation
             ↓
        Final Answer
________________________________________
Memory / State
The agent should maintain relevant state during the conversation.
Example:
User:
I have a VPN issue.

Agent:
What is your employee ID?

User:
EMP1024.

Agent:
I found your profile. Would you like me to check existing tickets?

User:
Yes.
The workflow should retain the required information across these interactions.
________________________________________
Safety / Validation Requirements
The agent should not blindly execute every action.
For example:
•	Validate required information before creating a ticket.
•	Do not create duplicate tickets unnecessarily.
•	Clearly communicate when information is missing.
•	Handle tool failures gracefully.
•	Do not invent ticket information.
•	Clearly distinguish between retrieved information and generated recommendations.
________________________________________
User Interface
A simple Streamlit interface is recommended.
The application should provide:
•	Chat interface
•	Conversation history
•	Clear/reset option
•	Tool/action result visibility where appropriate
•	Error handling
________________________________________
Expected Technical Skills Demonstrated
The project should demonstrate:
•	Python
•	LangGraph
•	Agentic AI
•	Tool Calling
•	Function Calling
•	State Management
•	Conditional Routing
•	Local Data/Database Integration
•	Prompt Engineering
•	Streamlit
•	Error Handling
•	Modular Architecture
CrewAI may be used as an alternative to LangGraph, provided the learner demonstrates equivalent agentic workflow concepts.
________________________________________
Common Submission Requirements
Regardless of the selected project, every learner must submit the following.
1. Source Code
•	Complete Python source code.
•	Proper project structure.
•	Modular implementation.
•	No unnecessary hard-coded values.
•	Clear variable and function names.
2. README.md
The README should contain:
•	Project title
•	Problem statement
•	Solution overview
•	Architecture diagram
•	Technology stack
•	Project structure
•	Setup instructions
•	Environment variable requirements
•	How to run the application
•	Sample inputs
•	Sample outputs
•	Key design decisions
•	Limitations
3. Sample Data
Learners must provide sufficient sample data so that the evaluator can run the application without creating data from scratch.
4. Demonstration
The learner should provide either:
•	A short demonstration video, or
•	A live demonstration during evaluation
The demonstration should show the major functional requirements working.
5. GitHub Repository
The project should be maintained in a GitHub repository containing:
•	Source code
•	README
•	Sample data
•	Requirements file
•	Configuration/example environment file
•	Architecture diagram
API keys or secrets must never be committed to GitHub.
________________________________________
Evaluation Criteria
The assessment will primarily evaluate the following areas:
Evaluation Area	What Will Be Evaluated
Functional Completeness	Are the required features actually implemented?
GenAI Implementation	Is the learner correctly using LLM/GenAI capabilities?
Architecture	Is the application logically structured and modular?
Technical Depth	Has the learner implemented the required techniques rather than merely mentioning them?
Code Quality	Is the code readable, maintainable and reasonably organized?
Error Handling	Does the application handle common failures gracefully?
User Experience	Is the application reasonably easy to use?
Documentation	Can another person understand and run the project?
Engineering Practices	Git, configuration, environment variables, logging and basic production practices
Demonstration	Can the learner explain the architecture, implementation and key technical decisions?
________________________________________
Certification Assessment Principle
The assessment is not intended to test how many technologies a learner can name.
It is intended to determine whether the learner can apply the concepts taught during the program to build a functional GenAI application.
A successful submission should demonstrate:
Understand → Design → Implement → Test → Explain
Learners are therefore expected to understand the implementation rather than simply assemble code from external sources.
________________________________________
Recommended Difficulty Level
The three projects are intentionally designed at different points across the GenAI Engineering spectrum:
Project 1
GenAI Workflow & Structured Output
Focus:
LLM Application Development + Workflow Orchestration + Structured Outputs
Project 2
Advanced RAG Application
Focus:
RAG + Advanced Retrieval + Memory + User Experience
Project 3
Agentic AI Application
Focus:
Agents + Tool Calling + LangGraph + State + Conditional Workflows
Together, these three options provide learners with meaningful choice while allowing the evaluation team to assess the core competencies covered throughout the GenAI Development program.
________________________________________
Final Assessment Outcome
Learners who successfully complete one of the projects and demonstrate sufficient technical understanding during evaluation will be considered to have qualified the final project assessment and become eligible for program certification, subject to the program’s certification policy.
