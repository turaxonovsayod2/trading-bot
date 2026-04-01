from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Trade, ReferralEarning, PartnerBalance, AdminBalance
from admin.auth import verify_admin
import os

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = Jinja2Templates(directory="admin/templates")

@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, admin=Depends(verify_admin)):
    session = SessionLocal()
    try:
        total_users = session.query(User).count()
        active_users = session.query(User).filter(User.auto_trade_enabled == True).count()
        total_revenue = session.query(AdminBalance).with_entities(AdminBalance.total_earned).all()
        revenue = sum(r[0] for r in total_revenue) if total_revenue else 0
        context = {
            "request": request,
            "total_users": total_users,
            "active_users": active_users,
            "total_revenue": revenue
        }
        return templates.TemplateResponse("dashboard.html", context)
    finally:
        session.close()
