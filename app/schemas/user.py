from pydantic import BaseModel , EmailStr , Field , field_validator

class UserCreate(BaseModel):
    name : str = Field(min_length=2 , max_length=100)
    email : EmailStr
    password : str = Field(min_length=8 , max_length=128)

    @field_validator("name")
    @classmethod
    def validate_name(cls ,value : str ) -> str:
        value = value.strip()

        if not value:
             raise ValueError("Name cannot be blank")

        return value
    


class UserResponse(BaseModel):
    id : int
    name : str
    email : EmailStr

    model_config = {
        "from_attributes": True
    }

class UserUpdate(BaseModel):
    name : str = Field(min_length=2 , max_length=100)
    email : EmailStr 

    @field_validator("name")
    @classmethod
    def validate_name(cls ,value : str ) -> str:
            value = value.strip()
    
            if not value:
                 raise ValueError("Name cannot be blank")
    
            return value
        


