from fastapi import APIRouter,HTTPException,Form
from schemas import UserResponse, UserCreate
from services import create_user
router = APIRouter(prefix="/user", tags=["Authentication"])

@router.post("/register",response_model=UserResponse)
async def register_user(user: UserCreate = Form(...)):
    try:
        new_user = await create_user(user)
        return UserResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            fullName=new_user.fullName,
            avatar=new_user.avatar,
            created_at=new_user.created_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating the user: {str(e)}"
        )
