import boto3
import streamlit as st
import os
import uuid
#from langchain_community.vectorstores import FAISS
from langchain.vectorstores import FAISS
from langchain_aws import BedrockEmbeddings


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

##Splits the pages of the doc into chunks using Text Splitter
def split_text(pages,chunk_size, chunk_overlap):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,chunk_overlap=chunk_overlap)
    docs = text_splitter.split_documents(pages)
    return docs

##Create Vector Store using FAISS
def create_vector_store(request_id,documents):
    vectorstore_faiss=FAISS.from_documents(documents,bedrock_embeddings)
    file_name=f"{request_id}.bin"
    folder_path="/tmp/"
    vectorstore_faiss.save_local(index_name=file_name,folder_path=folder_path)

    #uploading files to s3 after emebedding is complete
    s3_client.upload_file(Filename=folder_path + "/" + file_name + ".faiss", Bucket=BUCKET_NAME, Key="my_faiss.faiss")
    s3_client.upload_file(Filename=folder_path + "/" + file_name + ".pkl", Bucket=BUCKET_NAME, Key="my_faiss.pkl")

    return True


## INITIALIZE MAIN METHOD
def main():
    st.write("This is admin site for chat with PDF demo")
    uploaded_file = st.file_uploader("Choose a file","pdf")

    if uploaded_file is not None:
        request_id = get_unique_id()
        st.write(f"Request ID:- {request_id}")
        saved_file_name = f"(request_id).pdf"
        with open(saved_file_name, mode="wb") as w:
            w.write(uploaded_file.getvalue())

        loader = PyPDFLoader(saved_file_name)
        pages = loader.load_and_split()

        st.write(f"Total pages: {len(pages)}")

        ##Split pages into chunks and displaying couple of chunks
        splitted_docs = split_text(pages,1000,200)
        st.write(f"Splitted docs length {len(splitted_docs)}")
        st.write("Here is the first chunk")
        st.write(splitted_docs[0])
        st.write("Here is the second chunk")
        st.write(splitted_docs[1])

        st.write("Creating vector store")
        result = create_vector_store(request_id,splitted_docs)

        if result:
            st.write("Document processed successfully and added to vector store")
        else:
            st.write("Oops Error observed.Please troubleshoot")    

if __name__=='__main__':
    main()