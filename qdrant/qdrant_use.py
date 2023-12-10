from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue, Distance, VectorParams, PointStruct
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema import StrOutputParser
from dotenv import load_dotenv, find_dotenv
import os
from airtable import Airtable
from langchain.embeddings import OpenAIEmbeddings


load_dotenv(find_dotenv())

qdrant = QdrantClient("localhost", port=30217)

COLLECTION_NAME = "friends_data"

airtable_token = os.getenv('AIRTABLE_API_TOKEN')
airtable = Airtable('appGWWQkZT6s8XWoj', 'tblRws3jW42T7BteV', airtable_token)

embeddings = OpenAIEmbeddings()


def upsert_data():
    friends = airtable.get_all()

    points = []
    # Generate embeddings and index data
    for friend in friends:
        friend = friend['fields']
        embedding = embeddings.embed_query(friend['Description'])
        points.append({
            'id': friend['id'],
            'payload': {
                'source': COLLECTION_NAME,
                'name': friend['Name'],
                'description': friend['Description'],
                'city': friend['City'],
            },
            'vector': embedding
        })

    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        wait=True,
        points=[
            PointStruct(id=point['id'], vector=point['vector'], payload=point['payload']) for point in points
        ]
    )


def vector_search(query):
    query_embedding = embeddings.embed_query(query)
    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        query_filter=Filter(
            must=[FieldCondition(key="source", match=MatchValue(value=COLLECTION_NAME))]
        ),
        limit=3,
    )
    rerank_results = rerank_filter(query, results)
    print(rerank_results)
    search_output = ''
    for i, result in enumerate(results):
        if int(rerank_results[i]) == 1:
            search_output += f"{result.payload['name']}: {result.payload['description']}"

    if search_output == '':
        search_output = 'Nothig found.'

    return search_output


def rerank_filter(query, results):
    batch = []
    for result in results:
        batch.append({'query': query, 'result': result.payload['description']})
    prompt = "You get query with some information about friend. Check is provided friend descriptionis match for a query.\n###\nQuery:\n'''{query}'''\n\nDescription:\n'''{result}'''\n\nReturn '1' if match or '0' if not and nothing else"
    prompt_template = PromptTemplate.from_template(prompt)
    llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)
    chain = prompt_template | llm | StrOutputParser()
    rerank_result = chain.batch(batch)

    return rerank_result


def create_collection_if_not_indexed():
    is_indexed = next(
        (collection for collection in qdrant.get_collections().collections if collection.name == COLLECTION_NAME), None
    )

    # Create empty collection if not exists
    if not is_indexed:
        qdrant.create_collection(
            COLLECTION_NAME,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            on_disk_payload=True
        )

    collection_info = qdrant.get_collection(COLLECTION_NAME)

    # Add data to collection if empty
    if not collection_info.points_count:
        upsert_data()


if __name__ == '__main__':
    create_collection_if_not_indexed()
