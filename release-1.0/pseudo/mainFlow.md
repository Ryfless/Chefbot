# Main Flow of Application

1. **Landing Page_Guest Session (UI) Setup:**
    - Show homepage with guest session
    - Displays a button to navigate to the login page
    - Displays a button to navigate to start new topic of conversation

2. **Login Proccess: (HTML/JS/MySql):**
    - **Landing Page:** 
    User reaches the landing page.

    - **Check Existing Account:** 
    User is prompted to check if they already have an account.
        - Yes: User proceeds to log in.
        - No: User proceeds to create a new account (registration).

    - **Login:**
        - User enters login credentials.
        - Credentials are validated against the database.
        - Valid: User is logged in.
        - Invalid: Login attempt fails.
    - **Registration:**
        - User fills in registration information.
        - Information is saved to the database.
        - Data Valid: User account is created, and the user can log in.
        - Data Invalid: Registration fails.
    - **User Account Activation:**
        - The user may need to activate their account via an email link.
        - After activation, the user can log in.

3. **Landing Page_Logged-in Session (UI) Setup:**
    - Show user icon to indicate the user has logged in
    - Display menu box that contains history chat data from user database (mysql)
    - Show search box to search history chat from recent conversation
    - Also Displays a button to navigate to start new topic of conversation

4. **Conversation Page (UI) Setup:**
    - **Chatbot Prompt:** 
        - Greetings: Display `"Ada yang bisa saya bantu?"`
        - Display a menu box containing suggested questions
    - **Side Bar:**
        - Show timestamp for each chat
        - Display each chat history that fetch from user database
    - **Space of Conversation:**
        - **Chatbox:**
            - Fetch all `content` from memory buffer
            - Display each conversation in chat field
        - **Input Field:**
            - Display input text with placeholder
            - dropdown menu to add achieve document, also export  chat to pdf format
            - Button to send user input to chat's memory buffer
        - **Exporting Chat:**
            - Display export icon to download chat history
            - User requested to naming the file before exporting
            - export chat content from memory buffer

5. **Conversation Backend (HTML/JS):**
    - **Suggestion Box:**
        - Input field fetch template prompt with `onClick()` function
    - **Side Bar:**
        - Retrieve all chat history from memory buffer:
            - Fetch the list of chats from `chatBuffer`.
        - For each chat in the chat history:
            - Get the chat's timestamp.
            - Calculate the difference between the current time and the chat's timestamp in hours.
        - Determine the time category for each chat:
            - If the difference < 24:
                - Set the time category to "Today".
            - Else if the difference >= 24 and < 48:
                - Set the time category to "Yesterday".
            - Else:
                - Calculate the number of days by dividing the difference by 24.
                - Set the time category to "x days ago" (where x is the number of days).
        - Display the chat history:
            - Group chats under their respective time categories (Today, Yesterday, x days ago).
            - Render the chats along with their timestamps and time categories.
    - **Input Proccess:**
        - Define the API endpoint:
            - POST /message: For text user input.
            - POST /upload: For file uploads.
        - Initialize memory buffer:
             - Create an array `messageBuffer` in json file to store both text messages and files.
        - Handle text input:
            - When a request is received at `/message`:
                - Extract the text content from the request payload.
                - Generate a unique ID for the message.
                - Add the text message to the `messageBuffer` with the following structure:
                    ```
                    {
                        id: "unique-id",
                        type: "text",
                        content: "user-input-text",
                        timestamp: "current-timestamp"
                    }
                - Return a success response with the message ID and metadata:
                ```
                    {
                        status: "success",
                        message: "Text message stored successfully",
                        data: {
                            id: "unique-id",
                            type: "text",
                            content: "user-input-text",
                            timestamp: "current-timestamp"
                        }
                    }
        - Handle file upload:
            - When a request is received at `/upload`:
                - Extract the file from the request payload.
                - Validate the file type:
                    - If the file is not PDF or DOCX, return an error response (e.g., "Invalid file type").
                - Generate a unique ID for the document (e.g., using a UUID library or timestamp).
                    - Read the file content and convert it to a binary or base64 format.
                    - Add the document to the `documentBuffer` with the following structure:
                        ```
                        {
                            id: "unique-id",
                            name: "filename.pdf",
                            type: "PDF",
                            content: "binary-or-base64-content",
                            timestamp: "current-timestamp"
                        }
                - Return a success response with the document ID and metadata:
                    ```
                    {
                        status: "success",
                        message: "File uploaded successfully",
                        document: {
                            id: "unique-id",
                            name: "filename.pdf",
                            type: "PDF",
                            timestamp: "current-timestamp"
                        }
                    }
        - Example usage:
            - Client sends a POST request to `/message` with text input.
            - Client sends a POST request to `/upload` with a PDF or DOCX file.
            - Server processes the requests, stores the data in memory, and returns success responses.
    - **Displaying Conversation:**
        - Define the API endpoint:
            - GET /conversation
        - Fetch conversation from memory buffer:
            - Retrieve all entries from the `messageBuffer` array.
            - Format the data for display:
                - For text messages:
                    - Display the content in a text bubble.
                - For files:
                    - Display the file name.
        - Example usage:
            - Client sends a GET request to `/conversation`.
            - Server returns the entire conversation from the memory buffer.
            - Client renders the conversation in the chatbox.
    - **Export Chat:**
        - Export chat data:
            - Create a Blob object containing the formatted `exportData`.
            - Create a downloadable link for the Blob.
            - Trigger the download when the export button is clicked.
        - Example usage:
            - User clicks the "Export Chat" button.
            - The chat data is fetched, formatted, and exported as a text file.

---

# API Endpoint Pseudocode (Flask)

## 1. Initialization and Configuration
- **Import Libraries:** `Flask`, `requests`, `json`, `os`, `PyPDF2`, `docx`, etc.
- **Initialize Flask App:** `app = Flask(__name__)`
- **Enable CORS:** `CORS(app)` for cross-origin requests.
- **Configuration Settings:**
  - `UPLOAD_FOLDER`: Directory for file uploads.
  - `ALLOWED_EXTENSIONS`: Allowed file types (`pdf`, `docx`).
  - `MAX_FILE_SIZE`: File size limit (10MB).
- **Load System Prompt:** Read `preset.txt` for system instructions.
- **Load Conversation History:** Read from `history.json`.

## 2. Helper Functions

### `setup_environment()`
- Create the `uploads` folder if it doesn’t exist.

### `allowed_file(filename)`
- Validate file extension (`pdf` or `docx`).

### `read_pdf(file_path)`
- Open and read content from a PDF file.
- Handle errors gracefully.

### `read_docx(file_path)`
- Open and read content from a DOCX file.
- Handle errors gracefully.

### `process_llm_response(response)`
- Process response from the LLM API.
- Handle HTTP errors and invalid JSON formats.

### `chat_with_llm(content, is_file)`
- Send a POST request to the LLM API with content.
- Include system prompt and user message.
- Handle request errors, such as timeouts.

### `save_conversation(role, content)`
- Save conversation history to `history.json`.
- Append user and assistant messages.

## 3. API Endpoints

### `/api/chat` (POST)
- Receive user input (JSON format).
- Save user message to conversation history.
- Send message to LLM and retrieve response.
- Save LLM response to conversation history.
- Return the response as JSON.

### `/api/upload` (POST)
- Receive and validate uploaded files.
- Save the file securely.
- Read file content (PDF/DOCX).
- Send content to LLM for processing.
- Save upload event and LLM response to history.
- Return LLM response and content preview.
- Delete uploaded file after processing.

### `/api/conversation` (GET)
- Retrieve conversation history from `history.json`.
- Return the history as JSON.

## 4. Application Entry Point

### `if __name__ == "__main__":`
- Run `setup_environment()` to prepare the environment.
- Start the Flask app in debug mode on port `5000`.

```python
if __name__ == "__main__":
    setup_environment()
    app.run(debug=True, port=5000)
```

