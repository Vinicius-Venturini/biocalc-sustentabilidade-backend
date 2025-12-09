from sqlalchemy.orm import Session
from app.models import Project, ProjectStatus
from app.schemas.project_steps import (
    ProjectStep0, ProjectStep1, ProjectStep2, ProjectStep3,
    ProjectStep4, ProjectStep5, ProjectStep6, ProjectStep7,
    ProjectStep8, ProjectStep9, ProjectStep10
)
from app.services.calculation_service import CalculationService
from typing import Optional
from fastapi import HTTPException


class ProjectStepService:
    """Service for step-by-step project creation"""
    
    def __init__(self, db: Session):
        self.db = db
        self.calc_service = CalculationService(db)
    
    def create_project_step0(self, step_data: ProjectStep0, user_id: int) -> Project:
        """
        Step 0: Criar projeto inicial com dados de identificação
        Retorna projeto em modo DRAFT com current_step = 0
        """
        project = Project(
            user_id=user_id,
            status=ProjectStatus.DRAFT,
            current_step=0,
            **step_data.model_dump()
        )
        
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        
        return project
    
    def update_step(self, project_id: int, user_id: int, step_number: int, step_data: dict) -> Project:
        """
        Atualiza um step específico do projeto
        Valida ownership e atualiza current_step se avançou
        """
        project = self.db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Atualiza campos do step
        for key, value in step_data.items():
            if hasattr(project, key):
                setattr(project, key, value)
        
        # Atualiza current_step se avançou
        if step_number > project.current_step:
            project.current_step = step_number
        
        self.db.commit()
        self.db.refresh(project)
        
        return project
    
    def update_step1(self, project_id: int, user_id: int, step_data: ProjectStep1) -> Project:
        """Step 1: Produção de Biomassa"""
        return self.update_step(project_id, user_id, 1, step_data.model_dump())
    
    def update_step2(self, project_id: int, user_id: int, step_data: ProjectStep2) -> Project:
        """Step 2: Mudança de Uso da Terra"""
        return self.update_step(project_id, user_id, 2, step_data.model_dump(exclude_unset=True))
    
    def update_step3(self, project_id: int, user_id: int, step_data: ProjectStep3) -> Project:
        """Step 3: Transporte da Biomassa"""
        return self.update_step(project_id, user_id, 3, step_data.model_dump(exclude_unset=True))
    
    def update_step4(self, project_id: int, user_id: int, step_data: ProjectStep4) -> Project:
        """Step 4: Dados do Sistema Industrial"""
        return self.update_step(project_id, user_id, 4, step_data.model_dump(exclude_unset=True))
    
    def update_step5(self, project_id: int, user_id: int, step_data: ProjectStep5) -> Project:
        """Step 5: Consumo de Eletricidade"""
        return self.update_step(project_id, user_id, 5, step_data.model_dump(exclude_unset=True))
    
    def update_step6(self, project_id: int, user_id: int, step_data: ProjectStep6) -> Project:
        """Step 6: Consumo de Combustíveis"""
        return self.update_step(project_id, user_id, 6, step_data.model_dump(exclude_unset=True))
    
    def update_step7(self, project_id: int, user_id: int, step_data: ProjectStep7) -> Project:
        """Step 7: Outros Insumos"""
        return self.update_step(project_id, user_id, 7, step_data.model_dump(exclude_unset=True))
    
    def update_step8(self, project_id: int, user_id: int, step_data: ProjectStep8) -> Project:
        """Step 8: Transporte Doméstico"""
        return self.update_step(project_id, user_id, 8, step_data.model_dump(exclude_unset=True))
    
    def update_step9(self, project_id: int, user_id: int, step_data: ProjectStep9) -> Project:
        """Step 9: Transporte Exportação"""
        return self.update_step(project_id, user_id, 9, step_data.model_dump(exclude_unset=True))
    
    def update_step10(self, project_id: int, user_id: int, step_data: ProjectStep10) -> Project:
        """Step 10: Volume de Produção"""
        return self.update_step(project_id, user_id, 10, step_data.model_dump())
    
    def finalize_and_calculate(self, project_id: int, user_id: int) -> Project:
        """
        Finaliza projeto e executa cálculos
        Só pode ser chamado se current_step >= 10
        """
        project = self.db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        if project.current_step < 10:
            raise HTTPException(
                status_code=400,
                detail=f"Projeto incompleto. Step atual: {project.current_step}/10"
            )
        
        # Validar campos obrigatórios
        if not project.biomass_type:
            raise HTTPException(status_code=400, detail="Tipo de biomassa é obrigatório")
        
        if not project.production_volume:
            raise HTTPException(status_code=400, detail="Volume de produção é obrigatório")
        
        # Executar cálculos
        try:
            results = self.calc_service.calculate_project_results(project)
            
            # Atualizar projeto com resultados
            for key, value in results.items():
                setattr(project, key, value)
            
            # Marcar como completo
            project.status = ProjectStatus.COMPLETED
            
            self.db.commit()
            self.db.refresh(project)
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao calcular resultados: {str(e)}"
            )
        
        return project
    
    def get_project_progress(self, project_id: int, user_id: int) -> dict:
        """Retorna progresso do projeto"""
        project = self.db.query(Project).filter(
            Project.id == project_id,
            Project.user_id == user_id
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        total_steps = 10
        progress_percentage = (project.current_step / total_steps) * 100
        
        # Verifica se pode calcular (steps obrigatórios completos)
        can_calculate = (
            project.current_step >= 10 and
            project.biomass_type is not None and
            project.production_volume is not None
        )
        
        return {
            "id": project.id,
            "name": project.name,
            "status": project.status.value,
            "current_step": project.current_step,
            "total_steps": total_steps,
            "progress_percentage": progress_percentage,
            "can_calculate": can_calculate
        }
