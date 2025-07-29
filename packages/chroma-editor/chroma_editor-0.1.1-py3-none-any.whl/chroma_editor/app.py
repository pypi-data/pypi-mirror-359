import ast
import streamlit as st
import argparse
import sys
import chromadb
import pandas as pd
from .pagination import init as init_pager, ui as pager_ui
from .search_utils import search as semantic_search,get_embedding_function
import json
def app_run():
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            min-width: 100px;
            max-width: 280px;
        }
        .block-container {
            max-width: 1600px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    def parse_args(args):
        parser = argparse.ArgumentParser(description='ChromaDB Editor')
        parser.add_argument(
            '--db-path',
            default='./chroma',
            help='Path to ChromaDB database directory (default: ./chroma)'
        )
        return parser.parse_args(args)

    args = parse_args(sys.argv[1:])

    # Connect directly to ChromaDB
    client = chromadb.PersistentClient(path=args.db_path)

    # Select or create a collection
    collections = client.list_collections()
    col_names = [c.name for c in collections] + ["new"]
    col_name = st.sidebar.selectbox("Select / Create collection", col_names)

    if col_name == "<new>":
        new_name = st.sidebar.text_input("New collection name")
        if st.sidebar.button("Create") and new_name:
            client.create_collection(new_name)
            st.experimental_rerun()
        st.stop()

    coll = client.get_or_create_collection(col_name,embedding_function=get_embedding_function())

    # Semantic search block
    st.sidebar.markdown("### Semantic search")
    st.sidebar.caption(f"Database path: {args.db_path}")
    query_text = st.sidebar.text_input("Enter query text")
    top_k = st.sidebar.number_input("Top-K", 1, 50, 5)

    if query_text:
        result_df = semantic_search(coll, query_text, top_k)
        st.subheader(f"🔍 Top {top_k} results for `{query_text}`")
        st.dataframe(result_df)
        st.divider()

    # Load full collection and build the paginated table
    data = coll.get()
    total_rows = len(data["ids"])

    page_size = st.sidebar.number_input("Rows per page", 10, 200, 20)
    init_pager(total_rows, page_size)
    start, end = pager_ui(page_size)

    page_df = {
        "id": data["ids"][start:end],
        "document": data["documents"][start:end],
        "metadata": data["metadatas"][start:end],
    }

    # Editable DataFrame
    st.subheader(f"Collection: {col_name}")
    edited_df = st.data_editor(pd.DataFrame(page_df).astype({
        "id": "string",
        "document": "string",
        "metadata": "string"
    }), num_rows="dynamic", key="editor")

    if st.button("💾 Save this page"):
        # 1. Convert edited_df to lists for easier handling
        ids = edited_df["id"].tolist()
        documents = edited_df["document"].tolist()
        metadatas = edited_df["metadata"].tolist()

        # 2. Type validation and conversion
        try:
            # Ensure IDs and Documents are strings
            ids = [str(id_) for id_ in ids]
            documents = [str(doc) for doc in documents]

            # Ensure Metadatas are dicts; try to parse string as JSON if needed
            for i, meta in enumerate(metadatas):
                if isinstance(meta, str):
                    try:
                        if meta == "":
                            metadatas[i] = {"fromWebUI":True}
                        else:
                            metadatas[i] = ast.literal_eval(meta)
                    except json.JSONDecodeError:
                        st.error(f"Metadata at index {i} is not a valid JSON string: {meta}")
                        st.stop()
                elif not isinstance(meta, dict):
                    st.error(f"Metadata at index {i} is not a dict: {meta}")
                    st.stop()
                else:
                    st.error(f"Metadata at index {i} is not a dict: {meta}")
            # 3. Delete old data if present
            if len(page_df["id"]) > 0:
                try:
                    coll.delete(ids=page_df["id"])
                except Exception as e:
                    st.error(f"Failed to delete old data: {e}")
                    st.stop()

            # 4. Add new data
            coll.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
            )
            st.success("Saved!")

        except Exception as e:
            st.error(f"Error during save: {e}")

    all_data = coll.get()
    export_json = json.dumps({
        "ids": all_data["ids"],
        "documents": all_data["documents"],
        "metadatas": all_data["metadatas"],
    }, indent=2, ensure_ascii=False)
    if st.download_button(
        label="⬇️ Export All to JSON",
        data=export_json,
        file_name=f"{col_name}_export.json",
        mime="application/json"
    ):
        pass



