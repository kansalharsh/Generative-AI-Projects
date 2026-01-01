from mcp.server.fastmcp import FastMCP
#from newsapi import NewsApiClient
from eventregistry import *
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

YOUR_API_KEY=os.getenv("YOUR_NEWSAPI_KEY")
#YOUR_API_KEY = "a1d0907a-25ca-451c-b647-0b3274e09c8f"
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
#OPENAI_API_KEY="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"
# Initialize clients with your API keys
#newsapi = NewsApiClient(api_key='YOUR_NEWSAPI_KEY')
#newsapi = NewsApiClient(api_key='a1d0907a-25ca-451c-b647-0b3274e09c8f')
client = OpenAI(api_key=OPENAI_API_KEY)


mcp = FastMCP(name="LiveNewsServer")

####################################################################################
##### Function to return summary of the articles provided by API####################
####################################################################################

def summarize_news_bodies(articles_list):
    """
    Summarizes the 'body' text of provided articles.
    """
    summaries = []
    combined_bodies=[]
    summary = ""

    for i, article in enumerate(articles_list):
        title = article.get('title', 'No Title')
        body = article.get('body', '')
        if body:
            # Add a clear separator so the AI knows these are different articles
            combined_bodies.append(f"Article Content:\n{body}")
        
    if not combined_bodies:
        return "No content available to summarize."

    full_text_to_summarize = "\n\n---\n\n".join(combined_bodies)

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional news summarizer. Provide a concise summary of the following article body in less than 50 words."},
                {"role": "user", "content": full_text_to_summarize}
                ]
            )
        summary = completion.choices[0].message.content
            
    except Exception as e:
        #print(f"Error summarizing article {i+1}: {e}")
        summary = f"Error generating unified summary: {e}"

    return summary

######################################################################################################
######################################################################################################




@mcp.tool(name="GetNews", description="It should NOT be used for weather updates or weather news.It takes only 1 input which is a keyword pertaining to user query. Basis the user query it retrieves live news using newsapi api and returns a summary in less than 250 words.")
def get_news_summary(query):

    er = EventRegistry(apiKey=YOUR_API_KEY, allowUseOfArchive=False)
    ########################################################
    ####### Fetch first 3 articles from NewsAPI ############
    ########################################################
    q = QueryArticlesIter(
    keywords=query,
    sourceLocationUri=QueryItems.OR([
        "http://en.wikipedia.org/wiki/United_Kingdom",
        "http://en.wikipedia.org/wiki/United_States",
        "http://en.wikipedia.org/wiki/India",
        "http://en.wikipedia.org/wiki/Canada"]),
    ignoreSourceGroupUri="paywall/paywalled_sources",
    dataType=["news", "pr"])
    
    news_data = list(q.execQuery(er, sortBy="date", sortByAsc=False, maxItems=3))

    ########################################################
    ##########Summarizig the articles#######################
    ########################################################    

    result = summarize_news_bodies(news_data)  
    return result 
    

if __name__ == "__main__":
    #mcp.run(transport="streamable-http")
    mcp.run()