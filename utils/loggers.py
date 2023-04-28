import logging
import os
import settings


def get_logger_for_module(module_name: str) -> logging.Logger:
    """ Логгер для конкретного модуля (логи в отдельном файле с названием модуля) """
    logger = logging.getLogger(module_name)
    logger.setLevel(settings.LOGGER_DEFAULT_LEVEL)
    handler = logging.FileHandler(os.path.join(settings.LOGDIR, module_name))
    handler.setFormatter(settings.LOGGER_DEFAULT_FORMAT)
    logger.addHandler(handler)
    return logger


def get_server_error_logger() -> logging.Logger:
    """ Общий логгер, используется в middleware для отлова всех ошибок """
    logger = logging.getLogger('server_error.log')
    logger.setLevel(settings.LOGGER_DEFAULT_LEVEL)
    handler = logging.FileHandler(os.path.join(settings.LOGDIR, 'server_error.log'))
    handler.setFormatter(settings.LOGGER_DEFAULT_FORMAT)
    logger.addHandler(handler)
    return logger
