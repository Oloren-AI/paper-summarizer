import oloren as olo
from pyzotero import zotero
import pypdf
import openai

"""Copy pasted from Chat with Papers"""
def parse_pdf(path, chunk_chars=2000, overlap=50):
    pdfFileObj = open(path, "rb")
    pdfReader = pypdf.PdfReader(pdfFileObj)
    splits = []
    split = ""
    pages = []
    metadatas = []
    for i, page in enumerate(pdfReader.pages):
        split += page.extract_text()
        pages.append(str(i + 1))
        while len(split) > chunk_chars:
            splits.append(split[:chunk_chars])
            pg = "-".join([pages[0], pages[-1]])
            split = split[chunk_chars - overlap :]
            pages = [str(i + 1)]

    if len(split) > overlap:
        splits.append(split[:chunk_chars])
        pg = "-".join([pages[0], pages[-1]])

    pdfFileObj.close()

    return splits, metadatas

@olo.register(description="Scrape zotero library to text")
def run_zotero(api_key = olo.String(secret=True), library_id = olo.String(), library_type = olo.Choice(choices=["user", "group"]),
           collection=olo.Option(olo.String())):
    zot = zotero.Zotero(library_id, library_type, api_key)

    ret = []

    if collection is not None:
        collection_key = None
        for col in zot.collections():
            if collection == col["data"]["name"]:
                collection_key = col["key"]

        if collection_key is None:
            raise ValueError(f"Collection {collection} not found.")

        items = zot.everything(zot.collection_items(collection_key))
    else:
        items = zot.everything(zot.top(limit=10))

    for item in items:
        if "attachment" not in item["links"]:
            continue

        attachment = item["links"]["attachment"]

        if attachment["attachmentType"] == "application/pdf":
            key = attachment["href"].split("/")[-1]

            with open(f"{key}.pdf", "wb") as f:
                f.write(zot.file(key))

            splits, _ = parse_pdf(f"{key}.pdf", chunk_chars=2000, overlap=0)

            ret.append("".join(splits)[:2000])

    return ret

@olo.register(description="Summarize a list of inputs with GPT")
def summarize(openai_key=olo.String(secret=True), inputs=olo.String()):
    openai.api_key = openai_key

    ret = []

    for input in inputs:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                    {"role": "system", "content": "Summarize the user entered text into 1-2 sentences."},
                    {"role": "user", "content": input},
                ]
        )
        ret.append(completion.choices[0]['message']['content'])
    return ret


if __name__ == "__main__":
    olo.run("summarizepaper", port=4824)