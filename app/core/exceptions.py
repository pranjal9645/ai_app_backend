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

class RateLimitExceededError(AppException):

     code = "RATE_LIMIT_EXCEEDED"

     def __init__(self, retry_after : int):
          self.retry_after = max(retry_after , 1)
          super().__init__(  "Too many requests. Please try again later.")
          
class RateLimitServiceUnavailableError(AppException):
     code = "RATE_LIMIT_SERVICE_UNAVAILABLE"

     def __init__(self):
          super().__init__("Rate-limiting service unavailable.")