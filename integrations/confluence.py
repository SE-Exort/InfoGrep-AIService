from langchain_community.document_loaders import ConfluenceLoader

from integrations.integration import Integration

class Confluence(Integration):
    def parse(self):
        loader = ConfluenceLoader(url=self.config['url'], username=self.config['username'], api_key=self.config['api_key'])
        documents = loader.load(space_key=self.config['space_key'], include_attachments=False)
        for doc in documents:
            doc.metadata['page'] = 0
            doc.metadata['chatroom'] = self.chatroom_uuid
        return documents
