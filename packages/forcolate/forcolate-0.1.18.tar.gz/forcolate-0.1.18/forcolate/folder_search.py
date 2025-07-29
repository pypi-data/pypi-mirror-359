import os
import re
from fastembed.rerank.cross_encoder import TextCrossEncoder
import urllib.parse

from forcolate.document_to_text import convert_documents_to_markdown
from forcolate.query_url_extractor import extract_query_and_folder


def search_folder(query, source_directory, save_directory, threshold=0.0, limit=-1):
    """
    Process documents in a directory to find relevant documents based on a query.

    Parameters:
    - source_directory (str): Directory containing the documents to process.
    - save_directory (str): Directory to save the processed document files.
    - query (str): The search query to match against document content.
    - threshold (float): Minimum score threshold for saving a document.
    - limit (int): Maximum number of documents to assess.

    Returns:
    - List[str]: List of file paths where the processed documents are saved.
    """
    query, folder_list = extract_query_and_folder(query)

    folder_list.append(source_directory)

    os.makedirs(save_directory, exist_ok=True)

    # Load a pre-trained CrossEncoder model
    # Using the HuggingFace model name, fastembed will download/cache the ONNX version.
    model_name_hf = "Xenova/ms-marco-MiniLM-L-6-v2"
    model = TextCrossEncoder(model_name=model_name_hf, max_length=512)

    # List to store file paths
    file_paths = []

    # Convert documents to markdown and process them
    pairs = []
    document_names = []
    document_paths = []
    assess_limit = 0
    for directory in folder_list:
        if not os.path.exists(directory):
            print(f"Folder {directory} does not exist.")
            continue
        else:
            print(f"Processing folder {directory}")
        for filename, filepath,markdown_content in convert_documents_to_markdown(directory):
            if limit > 0 and assess_limit >= limit:
                break
            assess_limit += 1

            document_names.append(filename)
            document_paths.append(filepath)
            pairs.append((query, markdown_content))

            # Predict and save if the batch is large enough or limit is reached
            if len(pairs) >= 100 or (limit > 0 and assess_limit >= limit):
                # Extract document contents for the current query
                doc_contents = [doc_content for _, doc_content in pairs]
                scores = list(model.rerank(query, doc_contents))
                # Need to re-zip with original document_names, document_paths, and pairs for consistency
                # The original `pairs` list stores (query, markdown_content)
                # We need to ensure the order of scores matches the original documents

                # Create a list of original items that were scored
                scored_items = []
                for i in range(len(pairs)):
                    scored_items.append({
                        "name": document_names[i],
                        "path": document_paths[i],
                        "pair_data": pairs[i] # This is (query, markdown_content)
                    })

                ranked_documents = sorted(zip(scores, scored_items), key=lambda x: x[0], reverse=True)

                # Adapt structure for consistency with previous logic: (score, name, path, document_pair)
                # where document_pair is (query, content)
                reconstructed_ranked_documents = []
                for score, item_info in ranked_documents:
                    reconstructed_ranked_documents.append(
                        (score, item_info["name"], item_info["path"], item_info["pair_data"])
                    )
                ranked_documents = reconstructed_ranked_documents

                filtered = [doc for doc in ranked_documents if doc[0] >= threshold]
                for index, document_triple in enumerate(filtered):
                    score, name, path, document = document_triple
                    # Generate a unique filename using a hash of the document content
                    file_name = f"{index}_{name}_{score}.md"
                    file_name = re.sub(r'[^\w_.)( -]', '', file_name)

                    file_path = os.path.join(save_directory, file_name)
                    absolute_path = os.path.abspath(file_path)
                    
                    with open(absolute_path, 'w', encoding='utf-8') as file:
                        file.write(document[1])
                        # original path for user message
                        file_url = urllib.parse.urljoin('file:', urllib.request.pathname2url(path))
                        file_paths.append(file_url)

                # Clear the lists to free up memory
                pairs.clear()
                document_names.clear()
                document_paths.clear()

        # Process any remaining documents
        if pairs:
            doc_contents = [doc_content for _, doc_content in pairs]
            scores = list(model.rerank(query, doc_contents))

            # Create a list of original items that were scored
            scored_items = []
            for i in range(len(pairs)):
                scored_items.append({
                    "name": document_names[i],
                    "path": document_paths[i],
                    "pair_data": pairs[i]
                })

            ranked_documents = sorted(zip(scores, scored_items), key=lambda x: x[0], reverse=True)

            # Adapt structure for consistency
            reconstructed_ranked_documents = []
            for score, item_info in ranked_documents:
                reconstructed_ranked_documents.append(
                    (score, item_info["name"], item_info["path"], item_info["pair_data"])
                )
            ranked_documents = reconstructed_ranked_documents

            filtered = [doc for doc in ranked_documents if doc[0] >= threshold]
            for index, document_triple in enumerate(filtered):
                score, name, path, document = document_triple
                # Generate a unique filename using a hash of the document content
                file_name = f"{index}_{name}_{score}.md"
                file_name = re.sub(r'[^\w_.)( -]', '', file_name)

                file_path = os.path.join(save_directory, file_name)
                absolute_path = os.path.abspath(file_path)
                with open(absolute_path, 'w', encoding='utf-8') as file:
                    file.write(document[1])
                    file_url = urllib.parse.urljoin('file:', urllib.request.pathname2url(absolute_path))
                    file_paths.append(file_url)
            pairs.clear()
            document_names.clear()
            document_paths.clear()

    # Return the list of file paths
    return file_paths
