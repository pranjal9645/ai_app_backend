class UserAlreadyExistsError(Exception):
     code = "USER_ALREADY_EXISTS"

class UserNotFoundError(Exception):
    code = "USER_NOT_FOUND"

class NoteNotFoundError(Exception):
     code = "NOTE_NOT_FOUND"

class AuthenticationError(Exception):
     code = "AUTHENTICATION_FAILED"