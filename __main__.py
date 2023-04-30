import uvicorn
from settings import SERVER_HOST, SERVER_PORT


uvicorn.run('main:app',
            proxy_headers=True,
            host=SERVER_HOST,
            port=SERVER_PORT,
            timeout_keep_alive=30)