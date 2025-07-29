from pydantic import BaseModel
from uuid import UUID
from extopy.com.extopy.models.posts.Post import Post
from typing import Optional
from extopy.com.extopy.models.users.User import User

class LikeInPost(BaseModel):
    postId: UUID
    userId: UUID
    post: Optional[Post] = None
    user: Optional[User] = None
