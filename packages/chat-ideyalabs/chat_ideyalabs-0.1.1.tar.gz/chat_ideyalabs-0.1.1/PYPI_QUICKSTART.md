# 🚀 **Quick PyPI Publishing Guide**

## **Step 1: Secure Your Code**
```bash
# Environment variables are now configured in chat_ideyalabs/config.py
# Sensitive data is hidden from logs via chat_ideyalabs/utils/log_sanitizer.py
# .gitignore updated to prevent committing secrets
```

## **Step 2: Build Package**
```bash
pip install build twine
rm -rf dist/ build/ *.egg-info/
python -m build
```

## **Step 3: Test & Publish**
```bash
# Test on TestPyPI first (optional)
python -m twine upload --repository testpypi dist/*

# Publish to PyPI
python -m twine upload dist/*
```

## **Step 4: User Installation**
```bash
pip install chat-ideyalabs
```

## **Step 5: User Setup**
Users set environment variables:
```bash
export CHATIDEYALABS_LLM_BASE_URL=https://your-llm-endpoint.com
export CHATIDEYALABS_LLM_API_KEY=your-llm-api-key-here
export CHATIDEYALABS_VALIDATION_ENDPOINT=https://your-api-server.com
```

## **Step 6: Usage**
```python
from chat_ideyalabs import ChatIdeyalabs

chat = ChatIdeyalabs(api_key="user-api-key")
response = chat.invoke("Hello!")
print(response.content)
```

## **🔒 Security Features**
✅ All secrets in environment variables  
✅ Sensitive data masked in logs  
✅ No hardcoded credentials  
✅ Safe for public PyPI distribution  

See `PYPI_PUBLISHING_GUIDE.md` for full details. 