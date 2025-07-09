## Run the app
Create environment:

    python3 -m venv st

Activate environment:

    source st2/bin/activate

Install dependencies:

    pip3 install -r requirements.txt

Run app:

    streamlit run main.py
   Once the previous step is completed, the app will be open the default browser.

## Customize RAG endpoint
If you need to customize the RAG endpoint where the chat will address every query, please define a environment variable called **"RAG_API_URL"** before to run the app.

    export RAG_API_URL=http://localhost:8000/tfm/service/getAnswer
By default, the URL is *http://localhost:8000/tfm/service/getAnswer*
