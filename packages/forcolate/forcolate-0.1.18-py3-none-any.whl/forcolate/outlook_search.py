import shutil
import sys
import platform

# Check the operating system
is_windows = platform.system() == 'Windows'

if is_windows:
    try:
        import win32com.client
    except ImportError:
        win32com = None
        print("win32com not found. Some features may be unavailable.")


import os
import re
from fastembed.rerank.cross_encoder import TextCrossEncoder
import urllib.parse

from forcolate.common import copy_files_in_directory



def search_outlook_emails(query, in_directory="", save_directory="",  threshold=0.0, limit=-1):
    """
    Process Outlook emails to find relevant documents based on a query.

    Parameters:
    - query (str): The search query to match against email content.
    - in_directory (str): Directory used as input for the searc (not used in this function).
    - save_directory (str): Directory to save the processed email files.
    - threshold (float): Minimum score threshold for saving a document.
    - limit (int): Maximum number of emails to assess.

    Returns:
    - str : List of file paths where the processed emails are saved.
    """
    if not is_windows:
        return "This function is only available on Windows."
    
    # Initialize Outlook application
    outlook = win32com.client.Dispatch('Outlook.Application').GetNamespace('MAPI')

    os.makedirs(save_directory, exist_ok=True)

    # Load a pre-trained CrossEncoder model
    # Using the HuggingFace model name, fastembed will download/cache the ONNX version.
    model_name_hf = "Xenova/ms-marco-MiniLM-L-6-v2"
    model = TextCrossEncoder(model_name=model_name_hf, max_length=512)

    # List to store file paths
    file_paths = []

    # Iterate through accounts and folders
    messageNames = []
    pairs = []

    assess_limit = 0
    for account in outlook.Folders:
        for folder in account.Folders:
            for message in folder.Items:
                if limit > 0 and assess_limit > limit:
                    break
                assess_limit += 1

                messageNames.append(message.Subject)
                pairs.append((query, message.Body)) # query is the same for all items in this list

    if not pairs: # Handle case where no emails are processed
        print("No emails found or processed.")
        return ""

    # Extract email bodies for reranking
    email_bodies = [body for _, body in pairs]
    scores = list(model.rerank(query, email_bodies))

    # Combine scores with original message details
    # The original `pairs` list stores (query, message_body)
    # We need to ensure the order of scores matches the original messages

    # Create a list of original items that were scored
    scored_items = []
    for i in range(len(pairs)):
        scored_items.append({
            "name": messageNames[i], # This was message.Subject
            "pair_data": pairs[i]    # This is (query, message.Body)
        })

    ranked_documents = sorted(zip(scores, scored_items), key=lambda x: x[0], reverse=True)

    # Adapt structure for consistency with previous logic: (score, name, document_pair)
    # where document_pair is (query, content)
    reconstructed_ranked_documents = []
    for score, item_info in ranked_documents:
        reconstructed_ranked_documents.append(
            (score, item_info["name"], item_info["pair_data"])
        )
    ranked_documents = reconstructed_ranked_documents

    filtered = [doc for doc in ranked_documents if doc[0] >= threshold]
    for index, message_triple in enumerate(filtered):
        score, name, message = message_triple
        # Generate a unique filename using a hash of the email body
        file_name = f"{index}_{name}_{score}.txt"
        file_name = re.sub(r'[^\w_.)( -]', '', file_name)

        file_path = os.path.join(save_directory, file_name)
        absolute_path = os.path.abspath(file_path)
        with open(absolute_path, 'w', encoding='utf-8') as file:
            file.write(message[1])
            file_url = urllib.parse.urljoin('file:', urllib.request.pathname2url(absolute_path))
            file_paths.append(file_url)

    # Return the list of file paths as a string
    user_message = '\n'.join(file_paths)

    print(f"Found {len(file_paths)} emails matching the query.")
  
    # Copy in folder to out folder
    in_directory = os.path.abspath(in_directory)
    save_directory = os.path.abspath(save_directory)

    if os.path.isdir(in_directory) and not save_directory.startswith(in_directory):
        copy_files_in_directory(in_directory, save_directory)
        #shutil.copy(in_directory, save_directory)

    

    return user_message
