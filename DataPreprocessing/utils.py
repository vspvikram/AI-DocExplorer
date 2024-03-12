import os
import io
from PyPDF2 import PdfReader, PdfWriter

def blob_name_from_file_page(filename, page):
    return os.path.splitext(os.path.basename(filename))[0] + f"-{page}" + ".pdf"

def upload_blobs(filename, pages, args, blob_container):
    # blob_service = BlobServiceClient(account_url=f"https://{args.storageaccount}.blob.core.windows.net", credential=storage_creds)
    # blob_container = blob_service.get_container_client(args.container)
    if not blob_container.exists():
        blob_container.create_container()
    for i in range(len(pages)):
        blob_name = blob_name_from_file_page(filename, i)
        if args.verbose: print(f"\tUploading blob for page {i} -> {blob_name}")
        f = io.BytesIO()
        writer = PdfWriter()
        writer.add_page(pages[i])
        writer.write(f)
        f.seek(0)
        blob_container.upload_blob(blob_name, f, overwrite=True)