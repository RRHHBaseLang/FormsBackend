from fastapi import HTTPException, APIRouter
from adapters.db import session
from Models.codigos import CodigosDb, testModel
import functools
from sqlalchemy import exc

router = APIRouter(prefix="/SecPersona", tags=["CodigosAcceso"])


def handle_database_errors(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except (exc.OperationalError, exc.IntegrityError) as e:
            session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Database error: {str(e)}"
            ) from e
    return wrapper

def is_test_started(user, test_id):
    try:
        comentarios = user.respComent
        print(comentarios)
        print(comentarios.get(test_id).get('status'))
        if comentarios.get(test_id).get('status') == None:
            return False
        print(comentarios.get(test_id).get('status') != "")
        return comentarios.get(test_id).get('status') != ""
    except:
        print("Error al leer los comentarios")
        return False

def confirm_user_authorization(usable_id, test_id):
    user = session.query(CodigosDb).filter_by(_id=usable_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    userForms = user.formIds
    print(userForms)
    print(str(test_id))
    print(str(test_id) in userForms)
    if not str(test_id) in userForms:
        raise HTTPException(
            status_code=401, detail="No está autorizado a realizar esta prueba")

    if is_test_started(user, test_id):
        raise HTTPException(
            status_code=401, detail="Ya realizaste esta prueba v2")

    return user

def confirm_user_authorization2(usable_id, test_id):
    user = session.query(CodigosDb).filter_by(_id=usable_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    if not test_id in user.formIds:
        raise HTTPException(
            status_code=401, detail="No está autorizado a realizar esta prueba")

    coments = user.respComent.get(test_id).get('status')
    if coments == 'Time over' or coments == 'finished' or coments == 'out of page':
        raise HTTPException(
            status_code=401, detail="Ya realizaste esta prueba"
        )
    return user


@router.post("/login")
@handle_database_errors
async def login(usable_id, test_id):
    user = confirm_user_authorization(usable_id, test_id)
    lastcoments = user.respComent
    try:
        lastcoments[test_id] = {'comentario': '', 'status': ''}
    except:
        lastcoments = {test_id: {'comentario': '', 'status': ''}}

    session.query(CodigosDb).filter_by(_id=usable_id).update(
        {CodigosDb.respComent: lastcoments})
    session.commit()

    return {"token": user._id}

def update_test_status(usable_id, data, status):
    form_id, response_id = data.formId, data.responseId
    user = confirm_user_authorization(usable_id, form_id)

    new_comments = {'response': response_id, 'status': status}
    user.respComent[form_id] = new_comments

    session.query(CodigosDb).filter_by(_id=usable_id).update(
        {CodigosDb.respComent: user.respComent})
    session.commit()

def update_test_status2(usable_id, data, status):
    form_id, response_id = data.formId, data.responseId
    user = confirm_user_authorization2(usable_id, form_id)

    new_comments = {'response': response_id, 'status': status}
    user.respComent[form_id] = new_comments

    session.query(CodigosDb).filter_by(_id=usable_id).update(
        {CodigosDb.respComent: user.respComent})
    session.commit()


@router.post("/start")
@handle_database_errors
async def start_test(usable_id, data: testModel):
    update_test_status(usable_id, data, 'comenzado')


@router.post("/over")
@handle_database_errors
async def time_over(usable_id, data: testModel):
    update_test_status2(usable_id, data, 'Time over')


@router.post("/out")
@handle_database_errors
async def out_of_page(usable_id, data: testModel):
    update_test_status2(usable_id, data, 'out of page')


@router.post("/finish")
@handle_database_errors
async def finish_test(usable_id, data: testModel):
    update_test_status2(usable_id, data, 'finished')
