from deeprag import vector_db
from deeprag.agent import generate_sub_queries, generate_gap_queries, generate_final_answer
from deeprag.agent.search_vdb import search_chunks_from_vectordb
from deeprag.configuration import Configuration, ModuleFactory
# from deeprag.tools import search_chunks_from_vectordb


def query(original_query: str, config: Configuration = None) -> str:
    module_factory = ModuleFactory(config)
    llm = module_factory.create_llm()
    embedding_model = module_factory.create_embedding()
    vector_db = module_factory.create_vector_db()
    
    print(f"Original query: {original_query}")
    all_chunks = []
    all_sub_queries = []

    ### SUB QUERIES ###
    sub_queries = generate_sub_queries(llm, original_query)
    if not sub_queries:
        print("No sub queries were generated by the LLM. Exiting.")
        return
    all_sub_queries.extend(sub_queries)
    sub_gap_queries = sub_queries

    for iter in range(config.query_settings["max_iter"]):
        print(f"Iteration: {iter + 1}")
        chunks_from_vectordb = []
        chunks_from_internet = []#TODO
        for query in sub_gap_queries:
            chunks_from_vectordb.extend(search_chunks_from_vectordb(query, vector_db, llm, embedding_model))
            # chunks_from_internet.extend(search_chunks_from_internet(query))# TODO
        all_chunks.extend(chunks_from_vectordb + chunks_from_internet)

        ### REFLECTION & GET GAP QUERIES ###
        sub_gap_queries = generate_gap_queries(original_query, all_sub_queries, all_chunks)
        if not sub_gap_queries:
            print("No new search queries were generated. Exiting.")
            break
        else:
            print("New search queries:", sub_gap_queries)
            all_sub_queries.extend(sub_gap_queries)


    ### GENERATE FINAL ANSWER ###
    print("Generating final answer...")
    final_answer = generate_final_answer(original_query, all_chunks)
    print("==== FINAL ANSWER====")
    print(final_answer)
    return final_answer
