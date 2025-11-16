import boto3
import streamlit as st
import os
import uuid
#from langchain_community.vectorstores import FAISS
from langchain.vectorstores import FAISS
from langchain_aws import BedrockEmbeddings
#from langchain.prompts import PromptTemplate
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.llms.bedrock import Bedrock

##Creating S3 client
s3_client = boto3.client("s3")
BUCKET_NAME = os.getenv("BUCKET_NAME")
#BUCKET_NAME = "hk-nlp-rag-learning-kb"

##Initializing bedrock embeddings
bedrock_client = boto3.client(service_name="bedrock-runtime")
bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1",client=bedrock_client)



##Textsplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter

##pdf loader
from langchain_community.document_loaders import PyPDFLoader

def get_unique_id():
    return str(uuid.uuid4())

##Splits the pages of the doc into chunks
def split_text(pages,chunk_size, chunk_overlap):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,chunk_overlap=chunk_overlap)
    docs = text_splitter.split_documents(pages)
    return docs

##Create Vector Store
def create_vector_store(request_id,documents):
    vectorstore_faiss=FAISS.from_documents(documents,bedrock_embeddings)
    file_name=f"{request_id}.bin"
    folder_path="/tmp/"
    vectorstore_faiss.save_local(index_name=file_name,folder_path=folder_path)

    #uploading files to s3 after emebedding is complete
    s3_client.upload_file(Filename=folder_path + "/" + file_name + ".faiss", Bucket=BUCKET_NAME, Key="my_faiss.faiss")
    s3_client.upload_file(Filename=folder_path + "/" + file_name + ".pkl", Bucket=BUCKET_NAME, Key="my_faiss.pkl")

    return True

folder_path="/tmp/"

#loading index
def load_index():
    s3_client.download_file(Bucket=BUCKET_NAME,Key="my_faiss.faiss",Filename=f"{folder_path}my_faiss.faiss")
    s3_client.download_file(Bucket=BUCKET_NAME,Key="my_faiss.pkl",Filename=f"{folder_path}my_faiss.pkl")


#define the llm
def get_llm():
    llm = Bedrock(
        #model_id="anthropic.claude-3-haiku-20240307-v1:0",
        #LLama model arguments########################
        model_id="meta.llama3-8b-instruct-v1:0",
        model_kwargs={"max_gen_len": 512},
        ##############################################
        #model_kwargs={"max_tokens": 512}
        #model_kwargs={"maxTokens": 256}
        client=bedrock_client
    )
    return llm

# -------------------------
# Prompt for LLM
# -------------------------
prompt_template = """
Human: Use the following pieces of context to provide a 
concise answer to the question at the end but summarize with 
at least 250 words with detailed explanations. If you don't know the answer, 
just say that you don't know.

<context>
{context}
</context>

Question: {question}

Assistant:
"""

PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context","question"]
)



#get response from LLM function
def get_response(llm,vectorstore,question):
   
    qa=RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(),
     #   (
     #       search_type="similarity",
     #       search_kwargs={"k": 5}
      #  ),
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )
    result = qa({"query": question})
    return result['result']


## INITIALIZE MAIN METHOD
def main():
    st.header("This is client site for chat with PDF demo using Bedrock RAG")

    load_index()

    dir_list = os.listdir(folder_path)
    st.write(f"Files and Directories in {folder_path}")
    st.write(dir_list)


    #creating index
    faiss_index = FAISS.load_local(
        index_name="my_faiss",
        folder_path =folder_path,
        embeddings=bedrock_embeddings,
        allow_dangerous_deserialization=True
    )

    st.write("Index is ready")

    Question = st.text_input("Ask a Question")

    if st.button("Ask question"):
        with st.spinner("Querying..."):
            llm = get_llm()
            #get response
            st.write("Here is your response")
            st.write(get_response(llm,faiss_index,Question))
        

if __name__=='__main__':
    main()