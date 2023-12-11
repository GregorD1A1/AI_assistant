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

memory_collection = "Memory"
tools_collection = "tools"


airtable_token = os.getenv('AIRTABLE_API_TOKEN')
friends_table = Airtable('appGWWQkZT6s8XWoj', 'tblRws3jW42T7BteV', airtable_token)

embeddings = OpenAIEmbeddings()


def create_collection_and_upsert(collection, type):
    is_indexed = next(
        (collection for collection in qdrant.get_collections().collections if collection.name == collection), None
    )

    # Create empty collection if not exists
    if not is_indexed:
        qdrant.create_collection(
            collection,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
            on_disk_payload=True
        )

    collection_info = qdrant.get_collection(collection)

    # Add data to collection if empty
    if not collection_info.points_count:
        upsert_data(collection, type)


def upsert_data(collection, type):
    rows = friends_table.get_all()

    points = []
    # Generate embeddings and index data
    for row in rows:
        row = row['fields']
        row['type'] = type
        embedding = embeddings.embed_query(row['content'])
        points.append({
            'id': row['id'],
            'payload': row,
            'vector': embedding
        })

    qdrant.upsert(
        collection_name=collection,
        wait=True,
        points=[
            PointStruct(id=point['id'], vector=point['vector'], payload=point['payload']) for point in points
        ]
    )


def vector_search(query, type):
    query_embedding = embeddings.embed_query(query)
    results = qdrant.search(
        collection_name=memory_collection,
        query_vector=query_embedding,
        query_filter=Filter(
            must=[FieldCondition(key="type", match=MatchValue(value=type))]
        ),
        limit=3,
    )
    rerank_results = rerank_filter(query, results)
    print(rerank_results)
    search_output = ''
    for i, result in enumerate(results):
        if int(rerank_results[i]) == 1:
            search_output += f"{result.payload['name']}: {result.payload['content']}"

    if search_output == '':
        search_output = 'Nothing found.'

    return search_output


def rerank_filter(query, results):
    batch = []
    for result in results:
        batch.append({'query': query, 'result': result.payload['content']})
    prompt = "You get query with some information about friend. Check is provided friend descriptionis match for a query.\n###\nQuery:\n'''{query}'''\n\nDescription:\n'''{result}'''\n\nReturn '1' if match or '0' if not and nothing else"
    prompt_template = PromptTemplate.from_template(prompt)
    llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)
    chain = prompt_template | llm | StrOutputParser()
    rerank_result = chain.batch(batch)

    return rerank_result


if __name__ == '__main__':
    #create_collection_and_upsert(memory_collection, 'friend')
    print(vector_search('AI devs course', 'friend'))
