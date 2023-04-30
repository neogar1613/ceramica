import inspect
import traceback as tb
from fastapi import HTTPException, status
from typing import Optional
from utils.loggers import get_server_error_logger


server_logger = get_server_error_logger()


class BaseErrorServer(Exception):
    def __init__(self, err, error_in):
        self.error_in = error_in
        error = tb.TracebackException(exc_type=type(err),
                                      exc_traceback=err.__traceback__,
                                      exc_value=err).stack[-1]
        server_logger.error(f'Error in: {self.error_in},\n\
error in file: {error.filename}, \n\
function_name: {error.name}\nline number: {error.lineno}, \n\
line text: {error.line}, \nerror: "{err}"\n')
        raise HTTPException(status_code=status.HTTP_510_NOT_EXTENDED,
                            detail='Внутренняя ошибка сервера.')


# class BaseError(Exception):
#     def __init__(self, err, error_in, msg):
#         self.error_in = error_in
#         self.msg = msg
#         error = tb.TracebackException(exc_type=type(err),
#                                       exc_traceback=err.__traceback__,
#                                       exc_value=err).stack[-1]
#         server_logger.error(f'Error in: {self.error_in},\n\
# error in file: {error.filename}, \n\
# function_name: {error.name}\nline number: {error.lineno}, \n\
# line text: {error.line}, \nerror: "{err}"\n')
#         raise HTTPException(status_code=status.HTTP_510_NOT_EXTENDED,
#                             detail=f'{self.msg}')


class RaisebleError(Exception):
    def __init__(self, msg):
        self.msg = msg
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f'{self.msg}')


class RaisebleDetailError(Exception):
    def __init__(self, obj):
        self.obj = obj
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=self.obj)

class DefaultCustomError(RaisebleError):
    """ """


def raise_custom_exception(err = None,
                           custom_exception = DefaultCustomError,
                           msg = 'Network error',
                           error_type = 'Raisable'):
    # Имя вызывающей функции
    err_func_name: str = inspect.stack()[1][3]
    error_in = f'{__name__} | {err_func_name}'
    if error_type == 'Base':
        raise custom_exception(err=err, error_in=error_in)
    elif error_type == 'Raisable':
        raise custom_exception(msg=msg)


# def raise_main_exception(err, msg: str):
#     # Имя вызывающей функции
#     err_func_name: str = inspect.stack()[1][3]
#     error_in = f'{__name__} | {err_func_name}'
#     raise BaseError(err=err, error_in=error_in, msg=msg)
