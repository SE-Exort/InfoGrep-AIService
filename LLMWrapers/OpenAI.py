from LLMWrapers.AI import AIWrapper

import openai


class OpenAI(AIWrapper):
    def set_openAIkey(self, api_key):
        openai.api_key = api_key
        return

    def summarize(self, query: str, embedding_model: str, chat_model: str) -> str:
        #get Vectors to search with
        embparams = {
            'model': embedding_model,
            'input': query,
        }

        response = openai.embeddings.create(**embparams)
        vectors = self.getVectors(text=response.data[0].embedding).json()['payload']

        #generate AI response
        sys_prompt = "You will be given a list of text and a query string, your job is to first filter out the most relevant result from the list of input text that answers or relates to the query string, and then summarize the relevant text to answer the query string's question."
        user_query = f"input texts are: {vectors}. the query is {query}"
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_query}
        ]

        params = {
            'model': chat_model,
            'messages': messages,
            'temperature': 0,
            'max_tokens': 2000,
        }
        print(params)
        response = openai.chat.completions.create(**params)
        print(response)
        return response.choices[0].message.content