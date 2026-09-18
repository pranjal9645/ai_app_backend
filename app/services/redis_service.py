from app.db.redis import redis_client
import json

class RedisService:

    def get(self , key : str):
       value = redis_client.get(key)

       if value is None:
           return None

       return json.loads(value)
    

    def set(self , key : str , value : str , ex : int | None = None):
       serialized_value = json.dumps(value)

       return redis_client.set(key , serialized_value , ex=ex)
    

    def delete(self , key : str):
       return redis_client.delete(key)

    def exists(self , key : str) :
        return redis_client.exists(key)

    def get_int(self ,key : str):
        value = redis_client.get(key)

        if value is None:
            return None

        return int(value)

    def increment(self , key : str):
        return redis_client.incr(key)
    


