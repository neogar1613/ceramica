class UserExistsError(Exception):
    def __init__(self, err_msg):
        self.err_msg = err_msg
