import inspect
import traceback as tb
from fastapi import Request, Response, status
from utils.loggers import get_server_error_logger

server_logger = get_server_error_logger()


async def catch_exceptions_middleware(request: Request, call_next):
    """ Middleware для обработки ошибок. Ловим все ошибки и пишем в logs/server_error.log """
    try:
        return await call_next(request)
    except Exception as err:
        err_func_name: str = inspect.stack()[1][3]
        error_in = f'{__name__} | {err_func_name}'
        error = tb.TracebackException(exc_type=type(err),
                                      exc_traceback=err.__traceback__,
                                      exc_value=err).stack[-1]
        server_logger.error(f'Error in: {error_in},\n\
error in file: {error.filename}, \n\
function_name: {error.name}\nline number: {error.lineno}, \n\
line text: {error.line}, \nerror: "{err}"\n')
        return Response(content='See logs',
                        media_type='plain/text',
                        status_code=status.HTTP_510_NOT_EXTENDED)