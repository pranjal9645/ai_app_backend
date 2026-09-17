class UserAlreadyExistsError(Exception):
    pass

class UserNotFoundError(Exception):
    pass

class NoteNotFoundError(Exception):
    pass

class AuthenticationError(Exception):
    pass