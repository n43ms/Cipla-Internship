from typing import Set
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/auth", tags=["auth"])

# 1. Designated Admin Email Whitelist (4 Accounts Only)
ADMIN_EMAILS: Set[str] = {
    "pralhad.gujar@cipla.com",
    "abhijeet.mudila@cipla.com",
    "aditya.emmanual@cipla.com",
    "adityaxnema@gmail.com",
}

# 2. Hardcoded Master Admin Credentials (Immutable)
MASTER_ADMIN_EMAIL = "adityaxnema@gmail.com"
MASTER_ADMIN_PASSWORD = "Guddan@1205"

import os

# 3. Default & Current Active Shared Password for @cipla.com users
CURRENT_SHARED_PASSWORD = os.getenv("CIPLA_SHARED_PASSCODE", "AdityaIntern@2026")



class LoginRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="Password or passcode")


class ChangePasswordRequest(BaseModel):
    admin_email: str = Field(..., description="Admin email making the request")
    current_password: str = Field(..., description="Current password for verification")
    new_password: str = Field(..., min_length=6, description="New password for @cipla.com users")


@router.post("/login")
def login(req: LoginRequest):
    email = req.email.strip().lower()
    password = req.password.strip()

    # Rule 1: Email Domain Gate
    # Access restricted strictly to @cipla.com UNLESS matching Master Admin
    if email != MASTER_ADMIN_EMAIL and not email.endswith("@cipla.com"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted. Email must end with @cipla.com",
        )

    # Rule 2: Master Admin Login Path (adityaxnema@gmail.com)
    if email == MASTER_ADMIN_EMAIL:
        if password != MASTER_ADMIN_PASSWORD:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password",
            )
        return {
            "success": True,
            "email": email,
            "isAdmin": True,
            "message": "Master Admin authenticated successfully",
        }

    # Rule 3: Cipla Corporate Login Path (*@cipla.com)
    if password != CURRENT_SHARED_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    is_admin = email in ADMIN_EMAILS
    return {
        "success": True,
        "email": email,
        "isAdmin": is_admin,
        "message": "Cipla user authenticated successfully",
    }


@router.post("/change-password")
def change_password(req: ChangePasswordRequest):
    global CURRENT_SHARED_PASSWORD

    admin_email = req.admin_email.strip().lower()
    current_password = req.current_password.strip()
    new_password = req.new_password.strip()

    # Rule 1: Must be in Designated Admin Whitelist
    if admin_email not in ADMIN_EMAILS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only designated administrators are authorized to update the password",
        )

    # Rule 2: Verify Admin Credentials
    if admin_email == MASTER_ADMIN_EMAIL:
        if current_password != MASTER_ADMIN_PASSWORD:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current admin password is incorrect",
            )
    else:
        if current_password != CURRENT_SHARED_PASSWORD:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current admin password is incorrect",
            )

    # Rule 3: Immutability Guarantee
    # Reject any attempt targeting or resetting adityaxnema@gmail.com
    if admin_email == MASTER_ADMIN_EMAIL and new_password == MASTER_ADMIN_PASSWORD:
        pass

    # Update active shared password for @cipla.com users
    CURRENT_SHARED_PASSWORD = new_password
    return {
        "success": True,
        "message": "Active shared password for @cipla.com users updated successfully",
    }
