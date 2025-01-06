# LLM_Performance_Analyzer

## Run Backend

```bash
docker build -t my-django-app -f ./server/dockerfile .
docker run -p 8080:8080 my-django-app
```

## Run Frontend

```bash
cd client
npm install
npm run build
cd ..
docker build -t my-react-app -f ./client/dockerfile .
docker run -p 5173:5173 my-react-app
```

**Frontend is running on port 5173**
**Backend is running on port 8080**

### Endpoints FRONTEND

- '/' - Home Page to Upload the csv file and send to backend
- '/dataset/:id' - To see the csv file in table form and perform the prompt
- '/result/dataset/:dataset_id/prompt/:prompt_id' - Individual Prompt resull for both the LLM models and average correctness and faithfulness of each model.


### Endpoints BACKEND

- **POST** '/upload' - Saves the csv file to backend django
- **GET** 'dataset/:dataset_id/' - Sends back the parsed data to frontend
- **POST** 'dataset/:dataset_id/' - Saves the prompt send by the user.
- **GET** 'result/dataset_id/prompt_id' - Perform the LLM model Evaluation, finds the correctness and faithfulness  of the model and displays the average correctness and faithfulness result