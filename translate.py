import asyncio


async def sample_translation_async():
    import os
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.translation.document.aio import DocumentTranslationClient

    endpoint = "https://arabic2english.cognitiveservices.azure.com/"
    key = "02e8845ff9a5477cb62b48386923f93c"
    source_container_url = "https://lawdataenar.blob.core.windows.net/inputfiles?sp=racwdli&st=2024-07-02T06:53:27Z&se=2024-07-02T14:53:27Z&spr=https&sv=2022-11-02&sr=c&sig=oyzJLyH%2BPuci7puWwEjQiyT%2BZKTyS4UikZwLsVP5%2BS0%3D"
    target_container_url = "https://lawdataenar.blob.core.windows.net/outputfiles?sp=racwdli&st=2024-07-02T06:54:34Z&se=2024-07-02T14:54:34Z&spr=https&sv=2022-11-02&sr=c&sig=30bwKBMnAnad1GjsbzV6fea0jZwODY68G3bSDTGNeZA%3D"
    
    client = DocumentTranslationClient(endpoint, AzureKeyCredential(key))
    
    async with client:
        poller = await client.begin_translation(source_container_url, target_container_url, "fr")
        result = await poller.result()

        print(f"Status: {poller.status()}")
        print(f"Created on: {poller.details.created_on}")
        print(f"Last updated on: {poller.details.last_updated_on}")
        print(f"Total number of translations on documents: {poller.details.documents_total_count}")

        print("\nOf total documents...")
        print(f"{poller.details.documents_failed_count} failed")
        print(f"{poller.details.documents_succeeded_count} succeeded")

        async for document in result:
            print(f"Document ID: {document.id}")
            print(f"Document status: {document.status}")
            if document.status == "Succeeded":
                print(f"Source document location: {document.source_document_url}")
                print(f"Translated document location: {document.translated_document_url}")
                print(f"Translated to language: {document.translated_to}\n")
            else:
                print(f"Error Code: {document.error.code}, Message: {document.error.message}\n")
    # [END begin_translation_async]


async def main():
    await sample_translation_async()

if __name__ == '__main__':
    asyncio.run(main())