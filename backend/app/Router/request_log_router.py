# app/Router/request_log_router.py
from fastapi import APIRouter, Depends, status
from app.Controllers.request_log_controller import RequestLogController
from app.Schemas.request_log import PaginatedRequestLogResponse
from app.Router.auth import require_roles

# Tutti gli endpoint in questo router richiedono il ruolo 'admin'
router = APIRouter(
    prefix="/api/v1/request-logs",
    tags=["Request Logs"],
    dependencies=[Depends(require_roles(["admin"]))],
)

controller = RequestLogController()

@router.get(
    "/",
    response_model=PaginatedRequestLogResponse,
    summary="Recupera i log delle richieste API",
    description="Restituisce un elenco paginato di tutte le richieste registrate dal middleware, con opzioni di ordinamento e filtro."
)
async def list_request_logs(
    # I parametri della funzione vengono passati direttamente da FastAPI al controller
    # grazie a Depends() che risolve i parametri della richiesta (query params)
    # e li inietta nel metodo del controller.
    response: PaginatedRequestLogResponse = Depends(controller.list_logs)
):
    return response

@router.delete(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Cancella tutti i log delle richieste",
    description="Svuota la tabella dei log delle richieste. L'operazione è irreversibile."
)
async def clear_request_logs(
    response: dict = Depends(controller.clear_logs)
):
    return response