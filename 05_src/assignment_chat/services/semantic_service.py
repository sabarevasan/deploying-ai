from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import chromadb
from chromadb.config import Settings
from openai import OpenAI
import os

load_dotenv('../.secrets')

# Initialize OpenAI client
client_openai = OpenAI(base_url='https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1', 
                api_key='any value',
                default_headers={"x-api-key": os.getenv('API_GATEWAY_KEY')})

# Initialize ChromaDB (persistent)
chroma_client = chromadb.Client(
    Settings(persist_directory="./chroma_db")
)

collection = chroma_client.get_or_create_collection(name="python101")


# -----------------------------
# STEP 1: SCRAPE DATA
# -----------------------------
def fetch_page_text(url: str) -> str:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.get_text(separator=" ", strip=True)

# -----------------------------
# STEP 2: CHUNK TEXT
# -----------------------------
def chunk_text(text, chunk_size=400, overlap=50):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - overlap):
        chunk = words[i:i + chunk_size]
        chunks.append(" ".join(chunk))

    return chunks

# -----------------------------
# STEP 3: BUILD DATABASE
# Run ONCE
# -----------------------------
def build_database():
    urls = [
        "https://python101.pythonlibrary.org/intro.html",
        "https://python101.pythonlibrary.org/part_i.html",
        "https://python101.pythonlibrary.org/chapter1_idle.html",
        "https://python101.pythonlibrary.org/chapter2_variables.html",
        "https://python101.pythonlibrary.org/chapter3_loops.html",
        "https://python101.pythonlibrary.org/chapter4_functions.html",
        "https://python101.pythonlibrary.org/chapter5_loops.html",
        "https://python101.pythonlibrary.org/chapter6_comprehensions.html",
        "https://python101.pythonlibrary.org/chapter7_exception_handling.html",
        "https://python101.pythonlibrary.org/chapter8_file_io.html",
        "https://python101.pythonlibrary.org/chapter9_imports.html",
        "https://python101.pythonlibrary.org/chapter10_functions.html",
        "https://python101.pythonlibrary.org/chapter11_classes.html",
        "https://python101.pythonlibrary.org/part_ii.html",
        "https://python101.pythonlibrary.org/chapter12_introspection.html",
        "https://python101.pythonlibrary.org/chapter13_csv.html",
        "https://python101.pythonlibrary.org/chapter14_config_parser.html",
        "https://python101.pythonlibrary.org/chapter15_logging.html",
        "https://python101.pythonlibrary.org/chapter16_os.html",
        "https://python101.pythonlibrary.org/chapter17_smtplib.html",
        "https://python101.pythonlibrary.org/chapter18_sqlite.html",
        "https://python101.pythonlibrary.org/chapter19_subprocess.html",
        "https://python101.pythonlibrary.org/chapter20_sys.html",
        "https://python101.pythonlibrary.org/chapter21_thread.html",
        "https://python101.pythonlibrary.org/chapter22_time.html",
        "https://python101.pythonlibrary.org/chapter23_xml.html",
        "https://python101.pythonlibrary.org/part_iii.html",
        "https://python101.pythonlibrary.org/chapter24_debugging.html",
        "https://python101.pythonlibrary.org/chapter25_decorators.html",
        "https://python101.pythonlibrary.org/chapter26_lambda.html",
        "https://python101.pythonlibrary.org/chapter27_profiling.html",
        "https://python101.pythonlibrary.org/chapter28_testing.html",
        "https://python101.pythonlibrary.org/part_iv.html",
        "https://python101.pythonlibrary.org/chapter29_pip.html",
        "https://python101.pythonlibrary.org/chapter30_configobj.html",
        "https://python101.pythonlibrary.org/chapter31_lxml.html",
        "https://python101.pythonlibrary.org/chapter32_pylint.html",
        "https://python101.pythonlibrary.org/chapter33_requests.html",
        "https://python101.pythonlibrary.org/chapter34_sqlalchemy.html",
        "https://python101.pythonlibrary.org/chapter35_virtualenv.html",
        "https://python101.pythonlibrary.org/part_v.html",
        "https://python101.pythonlibrary.org/chapter36_creating_modules_and_packages.html",
        "https://python101.pythonlibrary.org/chapter37_pypi_packaging.html",
        "https://python101.pythonlibrary.org/chapter38_eggs.html",
        "https://python101.pythonlibrary.org/chapter39_wheels.html",
        "https://python101.pythonlibrary.org/chapter40_py2exe.html",
        "https://python101.pythonlibrary.org/chapter41_bb_freeze.html",
        "https://python101.pythonlibrary.org/chapter42_cx_freeze.html",
        "https://python101.pythonlibrary.org/chapter43_PyInstaller.html",
        "https://python101.pythonlibrary.org/chapter44_creating_an_installer.html"
    ]

    all_chunks = []
    metadatas = []
    ids = []

    counter = 0

    for url in urls:
        print(f"Scraping: {url}")
        text = fetch_page_text(url)
        chunks = chunk_text(text)

        for chunk in chunks:
            all_chunks.append(chunk)
            metadatas.append({"source": url})
            ids.append(f"id_{counter}")
            counter += 1

    # Generate embeddings
    embeddings = client_openai.embeddings.create(
        model="text-embedding-3-small",
        input=all_chunks
    ).data

    embedding_vectors = [e.embedding for e in embeddings]

    # Store in Chroma
    collection.add(
        documents=all_chunks,
        embeddings=embedding_vectors,
        metadatas=metadatas,
        ids=ids
    )

    print("✅ Database built and persisted.")

# -----------------------------
# STEP 4: QUERY FUNCTION
# -----------------------------
def query_knowledge_base(user_query: str, k=3):
    # Embed query
    query_embedding = client_openai.embeddings.create(
        model="text-embedding-3-small",
        input=user_query
    ).data[0].embedding

    # Search Chroma
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )

    documents = results["documents"][0]
    sources = results["metadatas"][0]

    return documents, sources

# -----------------------------
# STEP 5: GENERATE ANSWER
# -----------------------------
def generate_answer(user_query: str):
    docs, sources = query_knowledge_base(user_query)

    context = "\n\n".join(docs)

    response = client_openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Answer ONLY using the provided context. If unsure, say you don't know."
            },
            {
                "role": "user",
                "content": f"""
Context:
{context}

Question:
{user_query}
"""
            }
        ],
        temperature=0.3
    )

    answer = response.choices[0].message.content

    return answer


# -----------------------------
# OPTIONAL: QUICK TEST
# -----------------------------
if __name__ == "__main__":
    choice = input("Type 'build' to create DB or 'chat' to query: ")

    if choice == "build":
        print("\nBuilding DB......\n")
        build_database()
    else:
        while True:
            q = input("\nAsk something about Python: ")
            print(generate_answer(q))