# Interact with Knowledge Base - Generative AI Application
## Built Using Amazon Bedrock, Langchain, Python, Docker, Amazon S3, Models- AWS Titan and llama3

## Models used:
    Amazon Titan Embedding G1 - Text
    meta.llama3-8b-instruct-v1:0

## Introduction
In this project the objective is to build a CHATBOT like application using 
-  AWS Amazon Bedrock
- docker
- python
- Langchain
- Streamlit

We will use RAG(Retrieval-Augmented generation) concept to provide context to the Large Language model along with user query to generate response from our Knowledge base.

# Personas
- Admin 
    - Owner of Knowledge articles
    - Creates S3 Repo and Vector embeddings
- User
    - Curious User wishing to seek a response for a query based upon all articles in repo


## Architecture
![image info](./Bedrock-ChatWithPdf.png)

## ADMIN Application:
    - Build Admin Web application where AdminUser can upload the pdf.
    - The PDF text is split into chunks
    - Using the Amazon Titan Embedding Model, create the vector representation of the chunks
    - Using FAISS, save the vector index locally
    - Upload the index to Amazon S3 bucket (You can use other vector stores like OpenSearch as well but for this project, I chose cost effective S3)

### Key Docker Commands:

  Build Docker Image:
  `docker build -t pdf-reader-admin .`

  Run ADMIN application:
  `docker run -e BUCKET_NAME=<YOUR S3 BUCKET NAME> -v ~/.aws:/root/.aws -p 8083:8083 -it pdf-reader-admin`



## USER Application:
  - Build User Web application where users can query / chat with the pdf.
  - At the application start, download the index files from S3 to build local FAISS index (vector store)
  - Langchain's RetrievalQA, does the following:
     - Convert the User's query to vector embedding using Amazon Titan Embedding Model (Make sure to use the same model that was used for creating the chunk's embedding on the Admin side)
    - Do similarity search to the FAISS index and retrieve 5 relevant documents pertaining to the user query to build the context
    - Using Prompt template, provide the question and context to the Large Language Model. We are using llama3 model which is available on demand.
   -  Display the LLM's response to the user.

### Docker Commands:

  Build Docker Image:
  `docker build -t pdf-reader-client .`

  Run ADMIN application:
  `docker run -e BUCKET_NAME=<YOUR S3 BUCKET NAME> -v ~/.aws:/root/.aws -p 8084:8084 -it pdf-reader-client`


#### Note: The docker volume mount is only needed in local. If you are running the container in ECS, or EKS, the iam role is used.

