# Python API Server Development Instructions
## VS Code Extension Backend Server

### 🎯 Project Overview
Welcome to the Instructions for the Agents Manager module, a flexible and dynamic agent management system built on top of Google's Agent Development Kit (ADK).

---

📝 AI Agent Development Instructions
Context

We are building custom modules on top of Google’s AI ADK (Agent Development Kit). Our focus is extending functionality, not altering the base library.

📂 Project Rules

Working Area

Core implementation belongs in:

src/core/


All new logic, services, and managers for our agent live here.

Documentation

For this module: update

docs/agent_manager_docs/


For ADK reference: read only from

docs/agents-adk-docs/


❌ Never modify agents-adk-docs. It is a mirror of upstream library docs, used for learning only.

Development Flow

Step 1: Review ADK patterns and examples (learn, don’t touch).

Step 2: Define small, isolated components in src/core/.
Step 3: Document progress and state changes in agent_manager_docs.
Step 4: Keep modules independent, no global state, always encapsulated.
Coding Principles
Modular, testable units.
Clear boundaries between our code and ADK base.
Always reference ADK APIs, never rewrite them.
Maintain sync between docs and implementation.

⚡ Think of agents-adk-docs as the textbook, and agent_manager_docs as the lab notebook.
All experiments and outputs stay in our notebook, the textbook is never touched.



## 🔗 Related Documents
- Contributor Quickstart: `docs/CONTRIBUTOR_QUICKSTART.md`
- Docs Index: `docs/README.md`
- Project Overview: `README.md`

---

## 📋 Core Development Principles

### 1. 📚 **Always Learn the Codebase First**
```bash
# Before any task, perform these steps:
1. Review the docs/ directory thoroughly
2. Understand the current architecture
3. Map out existing modules and their dependencies
4. Identify affected components before making changes
```
# Before any task, perform these steps:
1. Review the docs/ directory thoroughly
2. Understand the current architecture
3. Map out existing modules and their dependencies
4. Identify affected components before making changes

# After completing any task:
1. Create/update documentation in logs/<module_name>/ folder
2. Document the current working structure of modified modules
3. Include working examples and API endpoints
4. Exclude error logs - focus on final working state only
5. Update feature overview and dependencies


### 2. 🗂️ **Keep Files Small and Focused**
```python
# ✅ GOOD: Single responsibility, <200 lines
# src/services/auth/token_validator.py
from typing import Optional
from jose import jwt

class TokenValidator:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def validate(self, token: str) -> Optional[dict]:
        """Focused logic for token validation only"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.JWTError:
            return None

# ❌ BAD: Multiple responsibilities, >500 lines
# src/services/auth_service.py (handles auth, tokens, sessions, users, etc.)
```

**File Size Guidelines:**
- **Routers**: Max 150 lines
- **Services**: Max 200 lines  
- **Utils**: Max 100 lines
- **Models**: Max 250 lines
- **Schemas**: Max 150 lines

### 3. 🧩 **Split into Reusable Modules**

**Module Structure Rules:**
- Each module is self-contained with clear interfaces
- Break down your FastAPI application into reusable modules to promote code reusability and organization
- Shared utilities in `common/`
- Module-specific tests alongside code
- Each module should have responsibility for only one part of the functionality

### 4. 🚫 **No Big Changes Without Approval**
```bash
# Before implementing major features:
1. Create a design document in docs/proposals/
2. List all affected modules and files
3. Estimate breaking change risk (Low/Medium/High)
4. Get explicit approval before proceeding
```

**What Counts as "Big Changes":**
- New API endpoints or routers
- Database schema changes (Alembic migrations)
- Authentication/security modifications
- Third-party integrations
- Performance optimizations affecting multiple modules
- Changes to core middleware or error handling
- Dependency injection container modifications

### 5  **Use google-adk docs for agents development **
# We are using google-adk python library to manage and create or AI agents teams. 
# use the agents-adk-docs folder to learn about the framework.

### 6. 🎨 Console Output Must Use Rich Library
# All console prints must use the `rich` library for clarity and visual appeal.
# This ensures consistent formatting, better readability, and professional UI.

from rich.console import Console
from rich.table import Table

console = Console()

# Example: Styled log output
console.print("[bold green]Server started successfully[/bold green] 🚀")

# Example: Table display
table = Table(title="Active Connections")
table.add_column("Client ID", style="cyan", no_wrap=True)
table.add_column("Status", style="magenta")
table.add_row("123", "Connected")
table.add_row("456", "Disconnected")
console.print(table)
Rules for Console Output:

✅ Always prefer rich.console.Console.print over print().
✅ Use colors, tables, and panels where appropriate.
✅ Keep logs structured, clean, and visually appealing.
❌ Never use raw print() in production/debug scripts.

---


### **Dependency Injection Pattern**
```python
# core/deps.py
from functools import lru_cache
from fastapi import Depends
from sqlalchemy.orm import Session
from .database import get_db
from ..modules.auth.service import AuthService

@lru_cache()
def get_settings():
    return Settings()

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

# Usage in routers
@router.get("/protected")
async def protected_endpoint(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    return {"user": current_user}
```

### **Error Handling Strategy**
```python
# core/exceptions.py
from fastapi import HTTPException, status

class APIException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)

class AuthenticationError(APIException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)

class NotFoundError(APIException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)

# Global exception handler
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "path": request.url.path}
    )
```

---

## 🔧 Development Workflow

### **Pre-Development Checklist**
- [ ] Read relevant documentation in `docs/`
- [ ] Understand the feature requirements
- [ ] Map out affected modules and dependencies
- [ ] Check for existing similar implementations
- [ ] Estimate complexity and breaking change risk
- [ ] Set up virtual environment: `python -m venv venv`
- [ ] Install dependencies: `poetry install `

### **During Development**
1. **Start with schemas** - Define Pydantic models first
2. **Write tests** - Use pytest with async support
3. **Implement incrementally** - Small, focused commits
4. **Validate continuously** - Run tests and linting
5. **Document as you go** - Update docstrings and docs

### **Code Quality Tools**
```bash

# Testing
pytest tests/ -v --cov=src --cov-report=html
```

### **Code Review Requirements**
- [ ] All tests passing (`pytest`)
- [ ] Type hints present (`mypy` clean)
- [ ] Code formatted (`black`, `isort`)
- [ ] Documentation updated
- [ ] No files exceed size limits
- [ ] Follows established FastAPI patterns
- [ ] Breaking changes clearly marked

---

## 📁 Python Project Structure Standards

### **Directory Organization**
```
api-server/
├── src/
│   └── app/
│       ├── api/              # API route definitions
│       │   └── v1/
│       ├── modules/          # Feature modules
│       │   ├── auth/
│       │   ├── extensions/
│       │   └── common/
│       ├── core/            # Core functionality
│       │   ├── config.py
│       │   ├── database.py
│       │   └── security.py
│       └── main.py          # FastAPI application
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── alembic/                 # Database migrations
├── docs/
│   ├── api-reference.md
│   ├── architecture.md
│   └── modules/
├── scripts/                 # Utility scripts
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── pyproject.toml          # Project configuration
└── README.md
```

### **Python Naming Conventions**
- **Files/Modules**: snake_case (user_controller.py)
- **Directories**: snake_case (user_management/)
- **Classes**: PascalCase (UserService)
- **Functions/Variables**: snake_case (validate_user)
- **Constants**: UPPER_SNAKE_CASE (MAX_RETRY_ATTEMPTS)
- **Private members**: _underscore_prefix

---

## 🔒 Security Guidelines

### **Authentication & Authorization**
```python
# JWT Token handling
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Role-based access control
from enum import Enum
from functools import wraps

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    DEVELOPER = "developer"

def require_role(required_role: UserRole):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user or current_user.role != required_role:
                raise HTTPException(
                    status_code=403, 
                    detail="Insufficient permissions"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### **Input Validation with Pydantic**
```python
from pydantic import BaseModel, EmailStr, validator
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "strongpassword123",
                "full_name": "John Doe"
            }
        }

# Usage in router
@router.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, user)
```

---

## 🧪 Testing Requirements

### **Test Coverage Expectations**
- **Routers**: 100% of endpoints
- **Services**: 90%+ business logic
- **Utils**: 100% of functions
- **Integration**: All API endpoints
- **E2E**: Critical user flows

### **Pytest Structure**
```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db, Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

# tests/test_extensions.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_extension(client: TestClient):
    extension_data = {
        "name": "test-extension",
        "version": "1.0.0",
        "description": "Test extension"
    }
    response = client.post("/api/v1/extensions/", json=extension_data)
    assert response.status_code == 201
    assert response.json()["name"] == extension_data["name"]
```

### **Async Testing**
```python
# For testing async endpoints
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_async_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/extensions/")
    assert response.status_code == 200
```

---

## 🚀 Performance Guidelines

### **FastAPI Optimization**
```python
# Use async/await for I/O operations
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

class ExtensionService:
    async def get_extensions(self, db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(
            select(Extension).offset(skip).limit(limit)
        )
        return result.scalars().all()

# Background tasks for heavy operations
from fastapi import BackgroundTasks

@router.post("/extensions/process")
async def process_extension(
    background_tasks: BackgroundTasks,
    extension_id: int
):
    background_tasks.add_task(heavy_processing_task, extension_id)
    return {"message": "Processing started"}

# Caching with Redis
from redis import Redis
import json

redis_client = Redis(host='localhost', port=6379, decode_responses=True)

async def get_cached_data(key: str):
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    return None

async def set_cache(key: str, data: dict, expire: int = 3600):
    redis_client.setex(key, expire, json.dumps(data, default=str))
```

### **Database Optimization**
```python
# Use indexes and relationships properly
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship

class Extension(Base):
    __tablename__ = "extensions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)  # Indexed for fast lookups
    version = Column(String)
    created_at = Column(DateTime, index=True)  # For time-based queries
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="extensions")
    
    # Composite indexes
    __table_args__ = (
        Index('ix_extension_name_version', 'name', 'version'),
    )
```

---

## 🎯 VS Code Extension Specific Features

### **WebSocket Communication**
```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"Message: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

### **Language Server Protocol Support**
```python
from typing import Dict, List, Optional
import subprocess
import asyncio

class LanguageServerManager:
    def __init__(self):
        self.servers: Dict[str, subprocess.Popen] = {}
    
    async def start_language_server(self, language: str, workspace_path: str):
        """Start language server for specific language"""
        if language in self.servers:
            return
        
        # Example for Python language server
        if language == "python":
            server = await asyncio.create_subprocess_exec(
                "pylsp",  # Python LSP Server
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            self.servers[language] = server
    
    async def send_lsp_request(self, language: str, request: dict):
        """Send LSP request to language server"""
        if language not in self.servers:
            await self.start_language_server(language, "")
        
        # Implement LSP communication protocol
        pass
```

### **Extension Installation & Management**
```python
import zipfile
import json
from pathlib import Path

class ExtensionManager:
    def __init__(self, extensions_dir: str = "extensions/"):
        self.extensions_dir = Path(extensions_dir)
        self.extensions_dir.mkdir(exist_ok=True)
    
    async def install_extension(self, extension_file: bytes, extension_id: str):
        """Install extension from VSIX file"""
        extension_path = self.extensions_dir / extension_id
        
        # Extract VSIX (ZIP format)
        with zipfile.ZipFile(extension_file) as zip_ref:
            zip_ref.extractall(extension_path)
        
        # Read package.json for metadata
        package_json_path = extension_path / "extension" / "package.json"
        with open(package_json_path) as f:
            metadata = json.load(f)
        
        return {
            "id": extension_id,
            "name": metadata.get("displayName"),
            "version": metadata.get("version"),
            "description": metadata.get("description")
        }
    
    async def activate_extension(self, extension_id: str):
        """Activate extension and load its functionality"""
        # Implementation for extension activation
        pass
```

---

## ⚠️ Change Management Process

### **Breaking Change Protocol**
1. **Document the change** in `docs/proposals/`
2. **Create migration guide** for affected clients
3. **Version the API** following semantic versioning
4. **Update OpenAPI schema** for documentation
5. **Deprecate gradually** with clear timelines
6. **Communicate changes** to extension developers

### **Database Migrations (Alembic)**
```python
# Generate migration
alembic revision --autogenerate -m "Add extension table"

# Apply migration
alembic upgrade head

# Migration file example
def upgrade():
    op.create_table(
        'extensions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('version', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_extensions_name', 'extensions', ['name'])

def downgrade():
    op.drop_index('ix_extensions_name', 'extensions')
    op.drop_table('extensions')
```

---

## 📊 Monitoring & Logging

### **Structured Logging**
```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        return json.dumps(log_entry)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)

logger = logging.getLogger(__name__)
logger.handlers[0].setFormatter(JSONFormatter())
```

### **Request Tracking Middleware**
```python
import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class RequestTrackingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Track timing
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log request
        logger.info({
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "duration": duration
        })
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response

# Add to FastAPI app
app.add_middleware(RequestTrackingMiddleware)
```

---

## 🎓 Python/FastAPI Learning Resources

### **Required Reading**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

### **Best Practices**
- Use dependencies for request validation against database constraints
- Design and implement your code in a modular architecture with single responsibility principle
- Follow PEP 8 style guide
- Use type hints consistently
- Implement proper error handling

---

## 🚨 Emergency Procedures

### **Production Issues**
```python
# Health check endpoint
@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {"status": "healthy", "timestamp": datetime.utcnow()}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Service unavailable")

# Graceful shutdown
import signal
import asyncio

def handle_shutdown():
    logger.info("Shutting down gracefully...")
    # Close database connections
    # Stop background tasks
    # Clean up resources

signal.signal(signal.SIGTERM, handle_shutdown)
```

### **Response Times**
- **P0 (Critical)**: 15 minutes
- **P1 (High)**: 2 hours  
- **P2 (Medium)**: 24 hours
- **P3 (Low)**: 72 hours

---

*Remember: When in doubt, ask questions. It's better to clarify requirements than to implement the wrong solution. Python's explicit is better than implicit philosophy applies here - make your intentions clear in code and documentation.*
