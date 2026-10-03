class AppException(Exception):
     code = "APPLICATION_ERROR"

class UserAlreadyExistsError(AppException):
     code = "USER_ALREADY_EXISTS"

class UserNotFoundError(AppException):
    code = "USER_NOT_FOUND"

class NoteNotFoundError(AppException):
     code = "NOTE_NOT_FOUND"

class AuthenticationError(AppException):
     code = "AUTHENTICATION_FAILED"

class ConversationNotFoundError(AppException):
     code = "CONVERSATION_NOT_FOUND"

class MessageNotFoundError(AppException):
     code  = "MESSAGE_NOT_FOUND"

class AIServiceUnavailableError(AppException):
     code = "AI_SERVICE_UNAVAILABLE"