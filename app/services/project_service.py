from sqlalchemy.orm import Session
from app.models import Project, ProjectStatus, User
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.calculation_service import CalculationService
from typing import List, Optional
from fastapi import HTTPException


class ProjectService:
    """Service for project operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.calc_service = CalculationService(db)
    
    def create_project(self, project_data: ProjectCreate, user_id: int) -> Project:
        """Create a new project and calculate results"""
        # Create project
        project = Project(
            user_id=user_id,
            **project_data.model_dump()
        )
        
        self.db.add(project)
        self.db.flush()  # Get ID without committing
        
        # Calculate results
        try:
            results = self.calc_service.calculate_project_results(project)
            
            # Update project with results
            for key, value in results.items():
                setattr(project, key, value)
            
            # Mark as completed
            project.status = ProjectStatus.COMPLETED
            
        except Exception as e:
            # If calculation fails, keep as draft
            project.status = ProjectStatus.DRAFT
            print(f"Calculation error: {e}")
        
        self.db.commit()
        self.db.refresh(project)
        
        return project
    
    def get_project(self, project_id: int, user_id: int) -> Optional[Project]:
        """Get a project by ID"""
        project = self.db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()
        
        return project
    
    def list_user_projects(self, user_id: int) -> List[Project]:
        """List all projects for a user"""
        projects = self.db.query(Project).filter(
            Project.user_id == user_id
        ).order_by(Project.created_at.desc()).all()
        
        return projects
    
    def update_project(self, project_id: int, user_id: int, project_data: ProjectUpdate) -> Project:
        """Update a project and recalculate"""
        project = self.get_project(project_id, user_id)
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Update fields
        update_data = project_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(project, key, value)
        
        # Recalculate
        try:
            results = self.calc_service.calculate_project_results(project)
            
            for key, value in results.items():
                setattr(project, key, value)
            
            project.status = ProjectStatus.COMPLETED
            
        except Exception as e:
            project.status = ProjectStatus.DRAFT
            print(f"Calculation error: {e}")
        
        self.db.commit()
        self.db.refresh(project)
        
        return project
    
    def delete_project(self, project_id: int, user_id: int) -> bool:
        """Delete a project"""
        project = self.get_project(project_id, user_id)
        
        if not project:
            return False
        
        self.db.delete(project)
        self.db.commit()
        
        return True
