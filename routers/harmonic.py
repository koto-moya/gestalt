import pandas as pd
from fastapi import HTTPException, Depends, status, Request
from datetime import timedelta
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm


from config import limiter, TOKEN_EXPIRY
from modules.utils import authenticate_user, create_access_token, get_current_user_internal, match_pod_names
from modules.types import User, DataPayload, Token
from modules.db import get_brands, get_scope, get_codes, get_podcasts, get_code_performance, get_survey_performance, get_podscribe_performance

router  = APIRouter(prefix= "/harmonic")
# B sure to add get_current_user to all endpoints except for signing in of course

@router.post("/token")
@limiter.limit("100/minute")
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    user = authenticate_user(form_data.username, form_data.password) # datatype: UserInDB
    if not user:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers ={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=TOKEN_EXPIRY/200)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")

@router.get("/getbrands")
@limiter.limit("10/minute")
async def get_brands_e(request: Request, current_user: User =  Depends(get_current_user_internal)):
    scope = get_scope(current_user.id)
    if scope != "internal":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect Scope")
    else:
        brands = get_brands()
        return brands

@router.get("/getcodes")
@limiter.limit("10/minute")
async def get_codes_e(request: Request, current_user: User =  Depends(get_current_user_internal)):
    scope = get_scope(current_user.id)
    if scope != "internal":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect Scope")
    else:
        codes = get_codes()
        return codes

@router.get("/getpodcasts")
@limiter.limit("100/minute")
async def get_codes_e(request: Request, current_user: User =  Depends(get_current_user_internal)):
    scope = get_scope(current_user.id)
    if scope != "internal":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect Scope")
    else:
        podcasts = get_podcasts()
        return podcasts
        
@router.get("/getperformance")
@limiter.limit("100/minute")
async def get_performance_e(request: Request, current_user: User =  Depends(get_current_user_internal)) -> list:
    '''
    This endpoint contains a bunch of business logic.  not super pretty, i know, but I don't really feel like soving the
    variable podcast name dilema right now
    '''
    scope = get_scope(current_user.id)
    if scope != "internal":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect Scope")
    else:
        query_params = request.query_params
        startdate = query_params.get("startdate")
        enddate = query_params.get("enddate")
        brand = query_params.get("brand")
        podcasts = get_podcasts()

        survey_headers, survey_performance = get_survey_performance(startdate, enddate, brand)
        podscribe_headers, podscribe_performance = get_podscribe_performance(startdate, enddate, brand)
        survey_performance_df = pd.DataFrame(survey_performance,columns=survey_headers)
        podscribe_performance_df = pd.DataFrame(podscribe_performance,columns=podscribe_headers)
      
        # fix the podcast names
        survey_performance_df["podcast"] = survey_performance_df["podcast"].apply(lambda x: match_pod_names(x, podcasts))
        podscribe_performance_df["podcast"] = podscribe_performance_df["podcast"].apply(lambda x: match_pod_names(x, podcasts))
        
        # we groupby here as a redundancy, podcasts that have multiple entries under different names in the database
        survey_performance_df = survey_performance_df.groupby("podcast", as_index=False).sum()
        podscribe_performance_df = podscribe_performance_df.groupby("podcast", as_index=False).sum()
        
        # codes are retrieved here to capture any new pod names that may exist even though the chances of the codes data having an
        # unknow pod name is basically 0 given the codes pod names are directly linked to the source of truth
        code_headers, code_performance = get_code_performance(startdate, enddate, brand)
        code_performance_df = pd.DataFrame(code_performance,columns=code_headers)
        out = code_performance_df.merge(survey_performance_df, on="podcast", how="outer")
        out = out.merge(podscribe_performance_df,on="podcast", how="outer")
        # I hate this
        out = [out.columns.to_list()] + out.values.tolist()
        return out

        


