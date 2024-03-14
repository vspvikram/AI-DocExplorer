import os
import glob
import boto3
import pinecone
from sentence_transformers import SentenceTransformer
# from spacy.lang.en import English
import argparse
from PyPDF2 import PdfReader, PdfWriter
import io

SECTION_OVERLAP = 100 
MAX_SECTION_LENGTH = 1000
SENTENCE_SEARCH_LIMIT = 100

# Pinecone setup
def get_index(args):
    pc = pinecone.Pinecone(api_key=args.pineconekey)
    index_name = args.index
    # if index_name not in pc.list_indexes():
    #     pc.create_index(index_name)
    index = pc.Index(index_name)
    return index

# AWS S3 setup
def get_storage_client(args):
    s3_client = boto3.client('s3', aws_access_key_id=args.s3accesskey, aws_secret_access_key=args.s3secretkey)
    bucket_name = args.bucketname
    return s3_client, bucket_name

# Embedding model setup
def get_embed_model(args):
    model = SentenceTransformer(args.embedmodel) #'thenlper/gte-large'
    return model


def split_text(filename, pages):
    SENTENCE_ENDINGS = [".", "!", "?"]
    WORDS_BREAKS = [",", ";", ":", " ", "(", ")", "[", "]", "{", "}", "\t", "\n"]
    if args.verbose: print(f"Splitting '{filename}' into sections")

    page_map = []
    offset = 0
    for i, p in enumerate(pages):
        text = p.extract_text()
        page_map.append((i, offset, text))
        offset += len(text)

    def find_page(offset):
        l = len(page_map)
        for i in range(l - 1):
            if offset >= page_map[i][1] and offset < page_map[i + 1][1]:
                return i
        return l - 1

    all_text = "".join(p[2] for p in page_map)
    length = len(all_text)
    start = 0
    end = length
    while start + SECTION_OVERLAP < length:
        last_word = -1
        end = start + MAX_SECTION_LENGTH

        if end > length:
            end = length
        else:
            # Try to find the end of the sentence
            while end < length and (end - start - MAX_SECTION_LENGTH) < SENTENCE_SEARCH_LIMIT and all_text[end] not in SENTENCE_ENDINGS:
                if all_text[end] in WORDS_BREAKS:
                    last_word = end
                end += 1
            if end < length and all_text[end] not in SENTENCE_ENDINGS and last_word > 0:
                end = last_word # Fall back to at least keeping a whole word
        if end < length:
            end += 1

        # Try to find the start of the sentence or at least a whole word boundary
        last_word = -1
        while start > 0 and start > end - MAX_SECTION_LENGTH - 2 * SENTENCE_SEARCH_LIMIT and all_text[start] not in SENTENCE_ENDINGS:
            if all_text[start] in WORDS_BREAKS:
                last_word = start
            start -= 1
        if all_text[start] not in SENTENCE_ENDINGS and last_word > 0:
            start = last_word
        if start > 0:
            start += 1

        yield (all_text[start:end], find_page(start))
        start = end - SECTION_OVERLAP
        
    if start + SECTION_OVERLAP < end:
        yield (all_text[start:end], find_page(start))

def create_sections(base_filename, pages, model):
    for i, (section, pagenum) in enumerate(split_text(base_filename, pages)):
        
        metadata = {
            "content": section,
            "sourcepage": blob_name_from_file_page(base_filename, pagenum),
            "sourcefile": base_filename
        }
        embedding = convert_to_embeddings(model, section)
        yield (
            f"{base_filename}-{i}".replace(".", "_").replace(" ", "_"),
            embedding,
            metadata
        )

def index_sections(index, filename, sections):
    if args.verbose: print(f"Indexing sections from '{filename}' into search index '{args.index}'")
    
    i = 0
    vectors = []
    for s in sections:
        vectors.append(s)
        i += 1
        if i % 1000 == 0:
            # results = search_client.index_documents(vectors=vectors)
            results = index.upsert(vectors=vectors, namespace='aichatbot')
            if 'upserted_count' in results:
                if args.verbose: print(f"\tIndexed {results['upserted_count']} sections, {results['upserted_count']} succeeded")

    if len(vectors) > 0:
        results = index.upsert(vectors=vectors, namespace='aichatbot')
        if 'upserted_count' in results:
            if args.verbose: print(f"\tIndexed {results['upserted_count']} sections, {results['upserted_count']} succeeded")
        

def upload_file_to_s3(s3_client, bucket_name, file_name, object_name=None):
    if object_name is None:
        object_name = os.path.basename(file_name)
    s3_client.upload_file(file_name, bucket_name, object_name)

def blob_name_from_file_page(filename, page):
    return os.path.splitext(os.path.basename(filename))[0] + f"-{page}" + ".pdf"


def upload_blobs(filename, pages, args, s3_client, bucket_name):
    for i in range(len(pages)):
        blob_name = blob_name_from_file_page(filename, i)
        if args.verbose: print(f"\tUploading blob for page {i} -> {blob_name}")
        f = io.BytesIO()
        writer = PdfWriter()
        writer.add_page(pages[i])
        writer.write(f)
        f.seek(0)
        
        # Upload the BytesIO object to S3
        s3_client.put_object(Bucket=bucket_name, Key=blob_name, Body=f.getvalue())

        f.close()

def upload_to_pinecone(index, chunks, embeddings, filename):
    filename_without_extension = os.path.splitext(filename)[0]
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        chunk_id = f"{filename_without_extension}_{i}"
        metadata = {'filename': filename, 'text': chunk}
        index.upsert(vectors=[(chunk_id, embedding, metadata)])

def convert_to_embeddings(model, chunks):  #Default 'thenlper/gte-large' model generates vectors of dim 1024
    embeddings = model.encode(chunks)
    return embeddings

def process_documents(args):
    index = get_index(args)
    s3_client, bucket_name = get_storage_client(args)
    model = get_embed_model(args)

    # if args.deleteall:
        # index.delete(delete_all=True)
        # objects = s3_client.list_objects_v2(Bucket=bucket_name)
        # if 'Contents' in objects:
        #     for obj in objects:
        #         s3_client.delete_object(Bucket=bucket_name, Key=obj['Key'])

    # else:
    for filename in glob.glob(args.files):
        if args.verbose: print(f"Processing '{filename}'")
        if filename.endswith(".pdf"):
            
            reader = PdfReader(filename)
            pages = reader.pages

            # Upload the original document as individual page files to S3
            upload_blobs(filename, pages, args, s3_client, bucket_name)

            sections = create_sections(os.path.basename(filename), pages, model)
            index_sections(index, os.path.basename(filename), sections)
                
                

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Prepare documents by extracting content from PDFs, splitting content into sections, uploading to cloud storage, and indexing in a search index.",
        epilog="Example: prepdocs.py '../data/*' --storageaccount myaccount --container mycontainer --searchservice mysearch --index myindex -v",
    )
    parser.add_argument("files", nargs="?", help="Files to be processed")
    parser.add_argument("--pineconekey", required=True, help="API key to connect to Pinecone")
    parser.add_argument("--index", required=True, help="Name of the index where the chunks with vectors will be upserted")
    parser.add_argument("--s3accesskey", required=True, help="AWS access key")
    parser.add_argument("--s3secretkey", required=True, help="AWS secret key")
    parser.add_argument("--bucketname", required=True, help="AWS bucket name")
    parser.add_argument("--embedmodel", required=False, help="AWS bucket name", default="thenlper/gte-large")
    parser.add_argument("--deleteall", required=False, help="AWS bucket name", default="False")

    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    process_documents(args)

