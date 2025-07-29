"""
Tool Selector Module

This module provides functionality to select the most appropriate tool based on a given message.
It uses a pre-trained CrossEncoder model to compute similarity scores between the message and available tools.
"""

from fastembed.rerank.cross_encoder import TextCrossEncoder
from forcolate import search_outlook_emails, search_folder, convert_folders_to_markdown, summarize_documents, summarize_folder, convert_URLS_to_markdown

import os

DEFAULT_TOOLS = [
    (
        "Search in Folders",
        "Search in Local Folders and Documents: This tool allows you to search for files and documents within your local directories. You can find items by their names, content, or metadata across various file types, including text documents, spreadsheets, and presentations.",
        search_folder
    ),
    (
        "Search in Outlook",
        "Search in Outlook Email: This tool enables you to search through your Outlook emails. You can filter emails based on criteria such as sender, recipient, subject, date, and content. It can search across different email folders, including the inbox and sent items.",
        search_outlook_emails
    ),
    (
        "Convert to text",
        "Convert Documents to Text: This tool converts documents from various formats into plain text. It supports formats like PDF and Word documents, extracting the textual content while removing formatting elements.",
        convert_folders_to_markdown
    ),
    (
        "Summarize Documents",
        "Summarize Documents: This tool summarizes the content of each individual documents within a specified directory. It processes each file, generates a summary using a language model, and saves the summaries in a designated output directory.",
        summarize_documents
    ),
    (
        "Summarize Folder",
        "Summarize Folder: This tool generates a single summary from all the information. It reads each document, combines their contents, and produces a cohesive summary that encapsulates the main points across all files.",
        summarize_folder
    ),
    (
        "Download URL to text",
        "Download URL to Text: This tool download a document or web page from the enternet and convert the content into plain text. It fetches the webpage, extracts the textual content, and removes any HTML formatting.",
        convert_URLS_to_markdown
    )
]

def select_tool(message: str, available_tools: list = None, additional_tools: list = None) -> tuple:
    """
    Select the most appropriate tool based on the input message.

    Args:
        message (str): The input message to analyze.
        available_tools (list, optional): A list of default tools to consider. Defaults to DEFAULT_TOOLS.
        additional_tools (list, optional): A list of additional tools to include in the selection.

    Returns:
        tuple: A tuple containing the name, description, and function of the selected tool.
    """
    if available_tools is None:
        available_tools = DEFAULT_TOOLS

    # Merge additional tools if provided
    if additional_tools:
        available_tools = available_tools + additional_tools

    # Load the pre-trained model
    # Using the HuggingFace model name, fastembed will download/cache the ONNX version.
    model_name_hf = "Xenova/ms-marco-MiniLM-L-6-v2"
    print(f"Loading model {model_name_hf} using fastembed")
    model = TextCrossEncoder(model_name=model_name_hf, max_length=512)

    # Prepare the input pairs for the model
    # fastembed's rerank_pairs expects list of tuples: [(query, text), (query, text)]
    input_pairs = [(message, tool_description) for _, tool_description, _ in available_tools]

    # Compute similarity scores
    # The output of rerank_pairs is a list of scores
    similarity_scores = list(model.rerank_pairs(input_pairs))

    # Find the tool with the highest similarity score
    # We need to find the index of the max score in the list
    best_tool_index = similarity_scores.index(max(similarity_scores))
    best_tool = available_tools[best_tool_index]

    # Return the selected tool  

    return best_tool
