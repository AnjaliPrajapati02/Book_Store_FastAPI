from fastapi import HTTPException, Depends,APIRouter,requests,Request,Form
from sqlalchemy.orm import Session
from models import Book,User
from database import SessionLocal,engine,Base
from schemas import add_book_request,signup,login,EditUserForm
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt




templates = Jinja2Templates(directory="templates")

# JWT settings
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 password bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

routes = APIRouter()


@routes.post("/add_book")
async def add_book(
    request: add_book_request,
    db: Session = Depends(get_db)):
    try:
        print(request.title)
        new_book = Book(
            title=request.title,
            author=request.author,
            price=request.price,
            year_published=request.year_published,
            department=request.department
        )
        db.add(new_book)
        db.commit()
        db.refresh(new_book)
        return {"message": "Book added successfully", "book_id": new_book.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    

    ### get all the book list show here ###
@routes.get("/get_all_books/")
async def get_all_books(db: Session = Depends(get_db)):
    books = db.query(Book).all()
    return {
        "books": [
            {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "price": book.price,
                "year_published": book.year_published,
                "department":book.department
            }
            for book in books
        ]
    }

# @routes.get("/get_all_books/", response_class=HTMLResponse)
# async def get_all_books(request: Request, db: Session = Depends(get_db)):
#     books = db.query(Book).all()
#     return templates.TemplateResponse("table.html", {"request": request, "books": books})


@routes.get("/signup",response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@routes.post("/signup",response_class=HTMLResponse)
async def signup_route(request: Request,username: str = Form(...), password: str = Form(...), role: str = Form(...), department: str = Form(None)):
    # Check if the role is admin or prajapati
    if role in {"admin", "prajapati"}:
        department = None  # Set department to None for admin and prajapati
    
    new_user = User(username=username, password=password, role=role, department=department)
    db = SessionLocal()
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()
    
    return templates.TemplateResponse("signup.html", {"request": request,"message": "Signup successful"})

@routes.get("/users")
def get_all_users():
    db = SessionLocal()
    users = db.query(User).all()
    db.close()

    # Convert user objects to dictionaries
    user_data = [{"id": user.id, "username": user.username, "password": user.password,"role": user.role, "department": user.department} for user in users]
    
    return {"users": user_data}  # Return the list of user data

@routes.get("/profile.html", response_class=HTMLResponse)
async def profile(request: Request, db: Session = Depends(get_db)):
    user = db.query(User).all()
    return templates.TemplateResponse("profile.html", {"request": request, "users": user})

@routes.get("/login",response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@routes.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Retrieve the user from the database based on the provided username
    db = SessionLocal()
    user = db.query(User).filter(form_data.username==User.username).first()
    print(user)
    db.close()

    # Check if the user exists and the password matches
    # if user is None or form_data.password != user.password:
    #     raise HTTPException(status_code=401, detail="Invalid username or password")
        # return templates.TemplateResponse("login.html", {"request": Request})
        # return HTMLResponse(content="Invalid username or password", status_code=401)

    if user is None or form_data.password != user.password:
        print("Invalid username or password")
        return RedirectResponse(url="/login", status_code=302)



    # Determine the redirect URL based on the user's role
    redirect_url = ''
    if user.role == "admin":
        redirect_url = "/admin.html"
    elif user.role == "student":
        redirect_url = "/student.html"  # Change this to the actual URL for the student page
    else:
        raise HTTPException(status_code=401, detail="Unauthorized role")
    # Generate JWT token          
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_payload = {
        "sub": user.username,   
        "role": user.role,
        "exp": datetime.utcnow() + access_token_expires
    }
    access_token = jwt.encode(access_token_payload, SECRET_KEY, algorithm=ALGORITHM)

    # Append the access token to the redirect URL
    redirect_url += f"?access_token={access_token}"
    return RedirectResponse(url=redirect_url)

@routes.post("/admin.html", response_class=HTMLResponse)
async def admin(request: Request, db: Session = Depends(get_db)):
    books = db.query(Book).all()
    users = db.query(User).all()
    return templates.TemplateResponse("admin.html", {"request": request,"users": users, "books": books})

@routes.get("/student.html",response_class=HTMLResponse)
async def student(request: Request, db: Session = Depends(get_db)):
    books = db.query(Book).all()
    return templates.TemplateResponse("student.html", {"request": request, "books": books})

@routes.post("/student.html", response_class=HTMLResponse)
async def student(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    
    # Retrieve the user from the database based on the provided username and password
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or form_data.password != user.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Determine the department based on the user's role
    department = user.department

    # If department is not provided, determine it based on the user's role
    if not department:
        if user.role == "admin":         # Admin can access all departments
            department = "All Departments"
        elif user.role == "student":     # Students can access their own department
            department = user.department

    # Fetch data based on the determined department
    books = db.query(Book).filter(Book.department == department).all()
    
    db.close()

    return templates.TemplateResponse("student.html", {"request": request, "books": books})


@routes.get("/edit/{user_id}")
async def get_user_for_edit(user_id: int, request: Request, db: Session = Depends(get_db)):
    # Fetch the user from the database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Render the edit user form with the user data
    return templates.TemplateResponse(
        "edit.html", 
        {"request": request, "user": user}
    )


@routes.post("/edit/{user_id}")
async def edit_user(
    user_id: int,
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    department: str = Form(...),
    db: Session = Depends(get_db)
):
    # Fetch the user from the database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update user data with the new values
    user.username = username
    user.password = password
    user.role = role
    user.department = department

    db.commit()

    # Redirect to admin page after successfully updating the user
    return RedirectResponse(url="/profile.html", status_code=303)


@routes.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    # Fetch the user from the database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Delete the user
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}




@routes.get("/edit-book/{book_id}")
async def get_book_for_edit(book_id: int, request: Request, db: Session = Depends(get_db)):
    # Fetch the book from the database
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Render the edit book form with the book data
    return templates.TemplateResponse(
        "book.html", 
        {"request": request, "book": book}
    )

@routes.post("/edit-book/{book_id}")
async def edit_book(
    book_id: int,
    title: str = Form(...),
    author: str = Form(...),
    price: float = Form(...),
    year_published: int = Form(...),
    department: str = Form(...),
    db: Session = Depends(get_db)
):
    # Fetch the book from the database
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Update book data with the new values
    book.title = title
    book.author = author
    book.price = price
    book.year_published = year_published
    book.department = department

    db.commit()

    # Redirect to the admin page after successfully updating the book
    return RedirectResponse(url="/admin.html", status_code=303)

@routes.get("/admin.html", response_class=HTMLResponse)
async def admin(request: Request, db: Session = Depends(get_db)):
    books = db.query(Book).all()
    users = db.query(User).all()
    return templates.TemplateResponse("admin.html", {"request": request,"users": users, "books": books})


@routes.delete("/books/{book_id}")
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    # Fetch the book from the database
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Delete the book
    db.delete(book)
    db.commit()
    
    return {"message": "Book deleted successfully"}