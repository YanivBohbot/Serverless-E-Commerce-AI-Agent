# 🛒 Serverless E-Commerce AI Agent (Enterprise-Grade)

An autonomous AI customer support agent built with **LangGraph** and **AWS Bedrock**.
This project demonstrates a production-ready **Agentic Architecture** capable of reasoning, using tools, searching the web, and managing human-in-the-loop workflows for sensitive actions.

## 🚀 Key Features

* **🧠 Advanced Reasoning:** Uses **Claude 3.5 Sonnet** (via Amazon Bedrock) to understand complex user queries.
* **🔄 Cyclic Logic (ReAct):** Built with **LangGraph** to enable loops, self-correction, and multi-step reasoning.
* **🛠️ Multi-Tool Integration:**
    * **DynamoDB:** Real-time order status checks and database updates.
    * **Tavily Search:** Web browsing for real-time external information (news, weather).
    * **RAG (Bedrock Knowledge Base):** Retrieval-Augmented Generation for internal company policies (PDFs/Text).
* **🛡️ Human-in-the-Loop (HIL):** Implements a safety "interrupt" mechanism. Sensitive actions (like refunds) pause the agent and require Manager approval via API before execution.
* **💾 Persistent Memory:** Custom **DynamoDB Checkpointer** to maintain conversation state across stateless AWS Lambda invocations.
* **☁️ Serverless Deployment:** Fully containerized (**Docker**) and deployed on **AWS Lambda** via **ECR**.

## 🏗️ Technical Architecture

* **Orchestration:** LangGraph, LangChain
* **LLM:** Anthropic Claude 3.5 Sonnet (AWS Bedrock)
* **Compute:** AWS Lambda (Docker Image)
* **Database & Memory:** Amazon DynamoDB
* **Vector Database (RAG):** Amazon Bedrock Knowledge Base (OpenSearch Serverless)
* **Infrastructure:** AWS ECR, IAM, S3

## 🧩 How It Works

1.  **Router:** The agent analyzes the intent (Status check? Refund? Technical question?).
2.  **Tool Execution:**
    * *Safe Tools:* Executed immediately (e.g., searching order DB, RAG).
    * *Risky Tools:* Triggers an `interrupt_before` state. The state is saved to DynamoDB, and the Lambda shuts down.
3.  **Resume:** Upon external API approval (`command: RESUME`), the agent re-hydrates its state from DynamoDB and completes the action.

## 📦 Project Structure

```bash
├── src/
│   ├── graph.py            # LangGraph logic (Nodes, Edges, HIL)
│   ├── tools.py            # Tool definitions (RAG, Tavily, DynamoDB)
│   ├── persistence.py      # Custom DynamoDB Checkpointer class
│   ├── lambda_handler.py   # AWS Lambda entry point
│   └── config.py           # Configuration
├── Dockerfile              # Container definition for AWS Lambda
└── requirements.txt        # Dependencies
├── src/
│   ├── graph.py            # LangGraph logic (Nodes, Edges, HIL)
│   ├── tools.py            # Tool definitions (RAG, Tavily, DynamoDB)
│   ├── persistence.py      # Custom DynamoDB Checkpointer class
│   ├── lambda_handler.py   # AWS Lambda entry point
│   └── config.py           # Configuration
├── Dockerfile              # Container definition for AWS Lambda
└── requirements.txt        # Dependencies
