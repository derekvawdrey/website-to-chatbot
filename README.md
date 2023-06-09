
# Website to chatbot
This tool allows you to create a chatbot for your website by converting each page into embeddings and storing them in a Vector database. The embeddings are then used to give OpenAI’s GPT access to information on your website. When a user types in relevant information, their input is converted into embeddings and fed to the vector database. Once the closest matches are found, GPT analyzes the information from the user and the vector database to return a response.

This project was designed for the McKay School of Education at BYU. Developed by Derek Vawdrey.

# How to use
1. Download the repository
2. Install requirements.txt (python3 -m pip install -r ./requirements.txt)
3. Migrate the database (python3 manage.py migrate)
4. Create a pinecone.io free database (and OpenAI API account not free)
5. Create a .env file in the webtochatbot folder
```
    SECRET_KEY=anything_good_here
    OPENAI_API_KEY=xxx
    OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
    OPENAI_CHAT_MODEL=gpt-3.5-turbo
    PINECONE_INDEX=xxx
    PINECONE_API_KEY=xxx
    PINECONE_ENVIRONMENT=xxx
```
6. Run the commands in the Commands section
7. Start up the server (python manage.py runserver)
8. Navigate to the web app and start chatting

# Commands
### Convert website into database entries

python manage.py scrape --base-url https://education.byu.edu --html-elements-to-gather div.dept-name,section#content --html_elements_to_ignore span.visually-hidden

--base-url (required): The base where you would like the scrapper to start.
--html-elements-to-gather (required): Which html elements should the scraper pull data from? seperated by commas
--html_elements_to_ignore (optional): Which html elements should be ignored?
### Convert database entries into embeddings
python manage.py embed --base-url https://education.byu.edu --max-tokens 350
### Upload embeddings to Vector Database
This will delete your pinecone index vectors! Do not run if you don't want your pinecone index vectors deleted.

python manage.py upload --base-url https://education.byu.edu