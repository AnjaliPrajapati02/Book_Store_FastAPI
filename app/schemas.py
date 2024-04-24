from pydantic import BaseModel,validator
from  typing import Union,List,Optional


class add_book_request(BaseModel):
    title: str
    author: str
    price: int
    year_published: int
    department: str


    @validator("title")
    def validate_title(cls, value):
        if not value or not value.strip():
            raise ValueError("Title cannot be empty or whitespace.")
        return value

    @validator("author")
    def validate_author(cls, value):
        if not value or not value.strip():
            raise ValueError("Author cannot be empty or whitespace.")
        return value

    @validator("price")
    def validate_price(cls, value):
        if value <= 0:
            raise ValueError("Price must be greater than zero.")
        return value

    @validator("year_published")
    def validate_year_published(cls, value):
        current_year = 2024  # Update with the current year or get it dynamically
        if value < 0 or value > current_year:
            raise ValueError(f"Invalid year. Year must be between 0 and {current_year}.")
        return value
    
    @validator('department',pre=True)
    def validate_department(cls, value):
        department = ["Engineering","Arts","Commerce"]       # Define valid roles
        if value not in department:
            raise ValueError("Invalid role")
        return value
    

######################## signup _user ########################


class signup(BaseModel):
    username: str
    password: str
    role:str
    department:Union[str, List[str]] = None  # Make department a Union of str or List[str]

    @validator("username" , pre=True)
    def validate_username(cls, value):
        if len(value) < 3:
            raise ValueError('Username must be at least 3 characters long')
        return value

    @validator("password" , pre=True)
    def validate_password(cls, value):
        if len(value) < 3:
            raise ValueError('Password must be at least 3 characters long')
        return value
    
    @validator('role',pre=True)
    def validate_role(cls, value):
        role = {"admin","student","prajapati"}  # Define valid roles
        if value not in role:
            raise ValueError("Invalid role")
        return value
    

    @validator("department")
    def validate_department(cls, value, values):
        valid_departments = ["admin", "Engineering", "Art", "Commerce"]

        # If a single value is provided, convert it to a list
        if isinstance(value, str):
            value = [value]

        # Check if the role is admin or prajapati
        if values.get("role") in {"admin", "prajapati"}:
            return None  # Set department to None for admin and prajapati

        # Validate each department value for other roles
        for dep in value:
            if dep not in valid_departments:
                raise ValueError(
                    f"Invalid Department! '{dep}' is not a valid department. Valid departments are: {', '.join(valid_departments)}")

        return value

# login
class login(BaseModel):
    username: str
    password: str
    role:str

#Edit
class EditUserForm(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None