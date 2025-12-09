from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Union

from app.core.database import get_db
from app.models import User
from app.schemas.project_steps import (
    ProjectStep0, ProjectStep1, ProjectStep2, ProjectStep3,
    ProjectStep4, ProjectStep5, ProjectStep6, ProjectStep7,
    ProjectStep8, ProjectStep9, ProjectStep10,
    ProjectStepResponse, ProjectProgressResponse
)
from app.schemas.project import ProjectResponse, ProjectListItem
from app.services.project_step_service import ProjectStepService
from app.services.project_service import ProjectService
from app.routers.auth import get_current_user

router = APIRouter(prefix="/projects", tags=["Projects - Step by Step"])


# ============================================================================
# STEP 0: Criar Projeto Inicial
# ============================================================================

@router.post("/", response_model=ProjectStepResponse, status_code=status.HTTP_201_CREATED)
def create_project_step0(
    step_data: ProjectStep0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Step 0: Criar projeto inicial com dados de identificação
    
    Retorna projeto em modo DRAFT com current_step = 0
    """
    service = ProjectStepService(db)
    project = service.create_project_step0(step_data, current_user.id)
    
    return {
        "id": project.id,
        "name": project.name,
        "status": project.status.value,
        "current_step": project.current_step,
        "message": "Projeto criado com sucesso! Prossiga para o Step 1."
    }


# ============================================================================
# ROTA DINÂMICA PARA TODOS OS STEPS (1-10)
# ============================================================================

@router.put("/{project_id}/step/{step}", response_model=ProjectStepResponse)
def update_project_step(
    project_id: int,
    step: int,
    step_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Rota dinâmica para atualizar qualquer step (1-10)
    
    **Exemplos:**
    - PUT /projects/1/step/1 → Step 1: Produção de Biomassa
    - PUT /projects/1/step/5 → Step 5: Consumo de Eletricidade
    - PUT /projects/1/step/10 → Step 10: Volume de Produção
    """
    # Validar step number
    if step < 1 or step > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Step deve estar entre 1 e 10"
        )
    
    # Mapear schemas
    schemas = {
        1: ProjectStep1,
        2: ProjectStep2,
        3: ProjectStep3,
        4: ProjectStep4,
        5: ProjectStep5,
        6: ProjectStep6,
        7: ProjectStep7,
        8: ProjectStep8,
        9: ProjectStep9,
        10: ProjectStep10
    }
    
    # Validar dados contra o schema específico do step
    try:
        schema_class = schemas[step]
        validated_data = schema_class(**step_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

    service = ProjectStepService(db)
    
    # Mapear step para método correto
    step_methods = {
        1: service.update_step1,
        2: service.update_step2,
        3: service.update_step3,
        4: service.update_step4,
        5: service.update_step5,
        6: service.update_step6,
        7: service.update_step7,
        8: service.update_step8,
        9: service.update_step9,
        10: service.update_step10
    }
    
    # Mensagens por step
    step_messages = {
        1: "Step 1 salvo! Dados de produção de biomassa atualizados.",
        2: "Step 2 salvo! Dados de MUT atualizados.",
        3: "Step 3 salvo! Dados de transporte agrícola atualizados.",
        4: "Step 4 salvo! Dados do sistema industrial atualizados.",
        5: "Step 5 salvo! Consumo de eletricidade atualizado.",
        6: "Step 6 salvo! Consumo de combustíveis atualizado.",
        7: "Step 7 salvo! Outros insumos atualizados.",
        8: "Step 8 salvo! Transporte doméstico atualizado.",
        9: "Step 9 salvo! Transporte de exportação atualizado.",
        10: "Step 10 salvo! Volume de produção definido. Pronto para calcular!"
    }
    
    # Executar método do step
    update_method = step_methods[step]
    project = update_method(project_id, current_user.id, validated_data)
    
    return {
        "id": project.id,
        "name": project.name,
        "status": project.status.value,
        "current_step": project.current_step,
        "message": step_messages[step]
    }


# ============================================================================
# FINALIZAÇÃO E CÁLCULO
# ============================================================================

@router.post("/{project_id}/calculate", response_model=ProjectResponse)
def calculate_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Finaliza projeto e executa cálculos de emissões
    
    Só pode ser chamado após completar todos os steps (current_step >= 10)
    """
    service = ProjectStepService(db)
    project = service.finalize_and_calculate(project_id, current_user.id)
    
    return project


# ============================================================================
# CONSULTAS E PROGRESSO
# ============================================================================

@router.get("/{project_id}/progress", response_model=ProjectProgressResponse)
def get_project_progress(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna progresso do projeto
    
    Útil para mostrar barra de progresso no frontend
    """
    service = ProjectStepService(db)
    progress = service.get_project_progress(project_id, current_user.id)
    
    return progress


@router.get("/", response_model=List[ProjectListItem])
def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista todos os projetos do usuário (incluindo drafts)"""
    service = ProjectService(db)
    projects = service.list_user_projects(current_user.id)
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna detalhes completos do projeto"""
    service = ProjectService(db)
    project = service.get_project(project_id, current_user.id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deleta um projeto"""
    service = ProjectService(db)
    success = service.delete_project(project_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return None
