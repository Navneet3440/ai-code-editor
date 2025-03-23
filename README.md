# Collaborative Code Editor

A real-time collaborative code editor with user and session management, AI-powered debugging, and code generation. Multiple users can join a session, and the owner can invite others to view or edit the code. Two or more users can simultaneously edit code in a session using WebSocket. Integrated AI tools provide debugging and code generation capabilities.

---

## Features

1. **User Management**:

   - User authentication and authorization using JWT.
   - Role-based access control (owner, editor, viewer).

2. **Session Management**:

   - Create, update, and delete sessions.
   - Invite users to sessions with specific roles (owner, editor, viewer).

3. **Real-Time Collaboration**:

   - WebSocket-based real-time code editing.
   - Multiple users can edit the same session simultaneously.
   - Locking mechanism to prevent conflicts during AI operations.

4. **AI Integration**:

   - **AI Debugger**: Analyzes code for syntax errors, bugs, performance issues, and security vulnerabilities.
   - **AI Code Generator**: Generates complete, working code based on user instructions.

5. **Database**:

   - PostgreSQL for storing user, session, and code data.
   - SQLAlchemy ORM for database interactions.

---

## Installation

### Prerequisites

- Python 3.9+
- PostgreSQL
- OpenAI API Key

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repo/ai-code-editor.git
   cd ai-code-editor
   ```

2. Set up environment variables:

   - Copy `set_env.sh.example` to `set_env.sh`.
   - Update `set_env.sh` with your PostgreSQL and OpenAI API credentials.
   - Run `source set_env.sh`.

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:

   ```bash
   uvicorn app.main:app --reload
   ```

---

## API Endpoints

### User Management

- **POST** `/register`: Register a new user.
- **POST** `/login`: Authenticate and get a JWT token.

### Session Management

- **POST** `/sessions`: Create a new session.
- **PUT** `/sessions/{session_id}`: Update a session.
- **POST** `/sessions/invite`: Invite a user to a session.
- **PUT** `/sessions/access`: Update a user's role in a session.

### Editor

- **POST** `/ai/code-debugger`: Analyze code for errors and improvements.
- **POST** `/ai/code-generator`: Generate code based on instructions.
- **WebSocket** `/ws/{session_id}`: Real-time collaborative editing.

---

## Usage

### Real-Time Collaboration

- Open a WebSocket connection to `/ws/{session_id}`.
- Send and receive code updates in real-time.

### AI Debugger

- Send a **POST** request to `/ai/code-debugger` with the session ID.
- Receive a detailed analysis of the code.

### AI Code Generator

- Send a **POST** request to `/ai/code-generator` with the session ID and instructions.
- Receive the generated code.

---

## Technologies Used

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Real-Time Communication**: WebSocket
- **AI Integration**: OpenAI GPT
- **Authentication**: JWT

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a pull request.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

