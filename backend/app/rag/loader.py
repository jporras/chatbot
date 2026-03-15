from langchain_community.document_loaders import PyPDFLoader
from langchain.document_loaders import TextLoader


def load_document(path):

    if path.endswith(".pdf"):
        loader = PyPDFLoader(path)

    elif path.endswith(".md"):
        loader = TextLoader(path)

    else:
        raise Exception("Unsupported file type")

    return loader.load()