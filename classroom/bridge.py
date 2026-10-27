"""Student-owned bridge: private credential, local consent API, deterministic ZIP and retry."""
from __future__ import annotations
import hashlib
import json
import os
import secrets
import threading
import time
import zipfile
from pathlib import Path
from urllib.parse import urlparse
import httpx
from fastapi import FastAPI, HTTPException, Header, Request
from pydantic import BaseModel
from .common import CATEGORIES, canonical_json, digest, inventory, safe_path

ROOT=Path(os.getenv('CLASSROOM_WORKSPACE','/workspace'))
STATE=Path(os.getenv('CLASSROOM_BRIDGE_STATE','/state'))
HUB=os.getenv('CLASSROOM_HUB_URL','https://classroom.sysml.dev').rstrip('/')
INTERVAL=int(os.getenv('CLASSROOM_POLL_INTERVAL_SECONDS','5'))
CHUNK=int(os.getenv('CLASSROOM_UPLOAD_CHUNK_MIB','8'))*1024*1024
MAX_ZIP=int(os.getenv('CLASSROOM_MAX_ZIP_MIB','250'))*1024*1024
MAX_RAW=int(os.getenv('CLASSROOM_MAX_UNCOMPRESSED_MIB','500'))*1024*1024
app=FastAPI(docs_url=None,redoc_url=None,openapi_url=None)
def validate_hub_url():
    parsed=urlparse(HUB)
    if parsed.scheme!='https' and not (parsed.scheme=='http' and parsed.hostname in ('localhost','127.0.0.1','test')):
        raise RuntimeError('Classroom Hub URL must use HTTPS except for local tests')
lock=threading.RLock()

def state_path():STATE.mkdir(parents=True,exist_ok=True);return STATE/'state.json'
def load():
    p=state_path();return json.loads(p.read_text()) if p.exists() else {'status':'unpaired','requests':{},'pending':{},'online':False}
def save(value):
    p=state_path();tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(value));tmp.chmod(0o600);os.replace(tmp,p)
def call(method,path,body=None,token=None,raw=None,extra=None):
    s=load();token=s.get('credential') if token is None else token
    headers={'Authorization':'Bearer '+token} if token else {}
    headers.update(extra or {})
    with httpx.Client(timeout=120) as client:
        r=client.request(method,HUB+path,headers=headers,json=body if raw is None else None,content=raw)
        r.raise_for_status();return r.json()
def local_auth(value):
    expected=Path(os.getenv('CLASSROOM_LOCAL_SECRET_FILE','/run/classroom/local-secret')).read_text().strip()
    if not expected or not secrets.compare_digest(value or '',expected):raise HTTPException(401,'local service authentication required')
def manifest_for(categories,selected=None):
    entries=inventory(ROOT,categories,selected,max_total=MAX_RAW)
    return {'files':entries,'manifest_hash':digest(entries),'total_bytes':sum(e['size'] for e in entries),'categories':list(categories),'category_counts':{name:sum(e['path'].startswith(name+'/') for e in entries) for name in CATEGORIES},'excluded_summary':'Chats, hidden files, credentials, samples, symlinks and archives are excluded.'}
class Enroll(BaseModel):code:str;alias:str;label:str
class Prepare(BaseModel):categories:list[str]=list(CATEGORIES);selected:list[str]|None=None;message:str=''
class Decision(BaseModel):manifest_hash:str
class Selection(BaseModel):selected:list[str]
class BoardPost(BaseModel):body:str;posted_by:str='human'

@app.on_event('startup')
def startup():
    validate_hub_url()
    STATE.mkdir(parents=True,exist_ok=True)
    if os.getenv('CLASSROOM_MODE','student')=='student':threading.Thread(target=poller,daemon=True).start()
@app.get('/local/status')
def status(x_classroom_local:str|None=Header(None)):
    local_auth(x_classroom_local);s=load();return {k:v for k,v in s.items() if k!='credential'}|{'hub_url':HUB}
@app.post('/local/enroll')
def enroll(body:Enroll,x_classroom_local:str|None=Header(None)):
    local_auth(x_classroom_local)
    with lock:
        response=call('POST','/api/v1/devices/enroll',body.model_dump(),token='')
        s=load();s.update({'device_id':response['device_id'],'claim':response['claim'],'status':'pending'});save(s)
    return {'status':'pending'}
@app.get('/local/requests')
def requests(x_classroom_local:str|None=Header(None)):
    local_auth(x_classroom_local);return list(load()['requests'].values())
@app.post('/local/prepare')
def prepare(body:Prepare,x_classroom_local:str|None=Header(None)):
    local_auth(x_classroom_local)
    with lock:
        r=call('POST','/api/v1/me/workspace-requests',{'message':body.message,'categories':body.categories})
        s=load();s['requests'][r['request_id']]={'id':r['request_id'],'categories':json.dumps(body.categories),'status':'created','initiator':'student','message':body.message};save(s)
        return preview(r['request_id'],body.selected)
@app.get('/local/requests/{ident}/preview')
def preview_route(ident:str,x_classroom_local:str|None=Header(None)):
    local_auth(x_classroom_local);return preview(ident)
def preview(ident,selected=None):
    with lock:
        s=load();r=s['requests'].get(ident)
        if not r:raise HTTPException(404)
        categories=json.loads(r['categories']) if isinstance(r['categories'],str) else r['categories']
        result=manifest_for(categories,selected)
        call('POST',f'/api/v1/workspace-requests/{ident}/preview',{'manifest':result['files'],'manifest_hash':result['manifest_hash']})
        s['pending'][ident]=result;s['requests'][ident]['status']='awaiting_approval';save(s)
        return {'request_id':ident,**result}
@app.post('/local/requests/{ident}/preview')
def selected_preview(ident:str,body:Selection,x_classroom_local:str|None=Header(None)):
    local_auth(x_classroom_local);return preview(ident,body.selected)
@app.post('/local/requests/{ident}/approve')
def approve(ident:str,body:Decision,x_classroom_local:str|None=Header(None)):
    local_auth(x_classroom_local)
    with lock:
        s=load();pending=s['pending'].get(ident)
        if not pending or pending['manifest_hash']!=body.manifest_hash:raise HTTPException(409,'preview required')
        fresh=manifest_for(pending['categories'],[e['path'] for e in pending['files']])
        if fresh['manifest_hash']!=pending['manifest_hash']:
            s['pending'].pop(ident,None);save(s);raise HTTPException(409,'files changed; review again')
        call('POST',f'/api/v1/workspace-requests/{ident}/decision',{'decision':'approve','manifest_hash':body.manifest_hash})
        s['requests'][ident]['status']='approved';save(s)
    threading.Thread(target=transfer,args=(ident,),daemon=True).start()
    return {'status':'approved','request_id':ident}
@app.post('/local/requests/{ident}/decline')
def decline(ident:str,body:Decision,x_classroom_local:str|None=Header(None)):
    local_auth(x_classroom_local)
    with lock:
        s=load();p=s['pending'].get(ident)
        if not p or p['manifest_hash']!=body.manifest_hash:raise HTTPException(409)
        call('POST',f'/api/v1/workspace-requests/{ident}/decision',{'decision':'decline','manifest_hash':body.manifest_hash})
        s['requests'][ident]['status']='declined';s['pending'].pop(ident,None);save(s)
    return {'status':'declined'}
@app.get('/local/submissions')
def submissions(x_classroom_local:str|None=Header(None)):
    local_auth(x_classroom_local);return call('GET','/api/v1/me/submissions')
@app.get('/local/board/threads')
def board_threads(x_classroom_local:str|None=Header(None)):
    local_auth(x_classroom_local);return call('GET','/api/v1/board/threads')
@app.get('/local/board/threads/{ident}/messages')
def board_messages(ident:str,x_classroom_local:str|None=Header(None)):
    local_auth(x_classroom_local);return call('GET',f'/api/v1/board/threads/{ident}/messages')
@app.post('/local/board/threads/{ident}/messages')
def board_post(ident:str,body:BoardPost,x_classroom_local:str|None=Header(None)):
    local_auth(x_classroom_local);return call('POST',f'/api/v1/board/threads/{ident}/messages',{'body':body.body,'posted_by':'human'})
@app.post('/local/agent/board/threads/{ident}/messages')
def agent_board_post(ident:str,body:BoardPost,x_classroom_local:str|None=Header(None)):
    local_auth(x_classroom_local);return call('POST',f'/api/v1/board/threads/{ident}/messages',{'body':body.body,'posted_by':'agent'})

def build_archive(ident,manifest):
    path=STATE/f'{ident}.zip';tmp=STATE/f'{ident}.zip.part'
    with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        z.writestr('manifest.json',canonical_json({'generator':'keio-classroom-1','files':manifest}))
        for e in manifest:
            src=safe_path(ROOT,e['path']);h=hashlib.sha256()
            with src.open('rb') as stream,z.open(e['path'],'w') as out:
                for block in iter(lambda:stream.read(1024*1024),b''):
                    h.update(block);out.write(block)
            if h.hexdigest()!=e['sha256']:raise ValueError('files changed during packaging')
    if tmp.stat().st_size>MAX_ZIP:tmp.unlink();raise ValueError('archive too large')
    os.replace(tmp,path);return path

def transfer(ident):
    with lock:
        s=load();p=s['pending'].get(ident)
        if not p or s['requests'][ident]['status'] not in ('approved','uploading','offline'):return
        try:
            fresh=manifest_for(p['categories'],[e['path'] for e in p['files']])
            if fresh['manifest_hash']!=p['manifest_hash']:
                s['requests'][ident]['status']='review_again';s['pending'].pop(ident,None);save(s);return
            archive=STATE/f'{ident}.zip'
            if not archive.exists():archive=build_archive(ident,p['files'])
            h=hashlib.sha256()
            with archive.open('rb') as f:
                for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
            init=call('POST','/api/v1/submissions/initiate',{'request_id':ident,'manifest':p['files'],'manifest_hash':p['manifest_hash'],'size':archive.stat().st_size,'sha256':h.hexdigest()})
            sid=init['submission_id'];s['requests'][ident]['status']='uploading';s['requests'][ident]['archive_bytes']=archive.stat().st_size;save(s)
            received=set(call('GET',f'/api/v1/submissions/{sid}/upload-state')['received_chunks'])
            with archive.open('rb') as f:
                idx=0
                while block:=f.read(CHUNK):
                    if idx not in received:call('PUT',f'/api/v1/submissions/{sid}/chunks/{idx}',raw=block,extra={'X-Chunk-Sha256':hashlib.sha256(block).hexdigest()})
                    s['requests'][ident]['progress_bytes']=min((idx+1)*CHUNK,archive.stat().st_size);save(s)
                    idx+=1
            receipt=call('POST',f'/api/v1/submissions/{sid}/finalize')
            if receipt['sha256']!=h.hexdigest():raise ValueError('receipt checksum mismatch')
            archive.unlink(missing_ok=True);s['requests'][ident]['status']='received';s['requests'][ident]['receipt']=receipt;s['pending'].pop(ident,None);save(s)
        except (httpx.HTTPError,ValueError,KeyError) as error:
            s['requests'][ident]['status']='offline' if isinstance(error,httpx.HTTPError) else 'review_again'
            s['requests'][ident]['error']=str(error)[:200];save(s)

def poller():
    while True:
        try:
            with lock:
                s=load()
                if s.get('status')=='pending':
                    result=call('POST',f"/api/v1/devices/enroll/{s['device_id']}/claim",{'claim':s['claim']},token='')
                    if result['status']=='active':s['credential']=result['credential'];s.pop('claim',None);s['status']='active';save(s)
                if s.get('status')=='active':
                    call('POST','/api/v1/devices/heartbeat');rows=call('GET','/api/v1/me/workspace-requests')
                    for row in rows:
                        if row['id'] not in s['requests']:s['requests'][row['id']]=row
                        elif row['status'] in ('expired','declined','received'):
                            s['requests'][row['id']]['status']=row['status']
                            if row['status']=='expired':
                                s['pending'].pop(row['id'],None)
                                (STATE/f"{row['id']}.zip").unlink(missing_ok=True)
                        if row['status']=='created':call('POST',f"/api/v1/workspace-requests/{row['id']}/delivery-ack")
                    s['online']=True;s['last_sync']=time.time();save(s)
                    for ident,row in list(s['requests'].items()):
                        if row.get('status') in ('approved','uploading','offline'):transfer(ident)
        except (httpx.HTTPError,KeyError,ValueError) as error:
            with lock:
                s=load();s['online']=False
                if isinstance(error,httpx.HTTPStatusError) and error.response.status_code==401:
                    s['status']='revoked';s.pop('credential',None)
                save(s)
        time.sleep(INTERVAL)
