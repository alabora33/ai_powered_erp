from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models import MappingTemplate
from backend.schemas import MappingTemplateCreate, MappingTemplateOut

router = APIRouter(prefix="/api/templates", tags=["Templates"])

@router.get("", response_model=list[MappingTemplateOut])
async def list_templates(db: AsyncSession = Depends(get_db)):
    """Get all available mapping templates."""
    result = await db.execute(select(MappingTemplate).order_by(MappingTemplate.created_at.desc()))
    return result.scalars().all()

@router.post("", response_model=MappingTemplateOut)
async def create_template(template: MappingTemplateCreate, db: AsyncSession = Depends(get_db)):
    """Create a new mapping template."""
    db_template = MappingTemplate(
        name=template.name,
        description=template.description,
        target_schema=template.target_schema
    )
    db.add(db_template)
    await db.commit()
    await db.refresh(db_template)
    return db_template
