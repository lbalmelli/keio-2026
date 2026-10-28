"""Authenticated Jupyter Server adapter for the native Classroom panel."""
import json
import os
from pathlib import Path
from urllib.parse import quote
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPClientError
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
from tornado.web import authenticated

BRIDGE=os.getenv('CLASSROOM_LOCAL_BRIDGE','http://classroom-bridge:8767')
SECRET_FILE=Path(os.getenv('CLASSROOM_LOCAL_SECRET_FILE','/run/classroom/local-secret'))

class ClassroomHandler(APIHandler):
    @authenticated
    async def get(self, path=''):
        await self.forward('GET',path)
    @authenticated
    async def post(self,path=''):
        await self.forward('POST',path)
    async def forward(self,method,path):
        # This is an explicit map, never a generic bridge proxy.
        parts=path.strip('/').split('/')
        allowed_get={'status','requests','submissions','board/threads'}
        allowed_post={'enroll','prepare','profile'}
        if method=='GET' and (path in allowed_get or (len(parts)==3 and parts[0]=='requests' and parts[2]=='preview') or (len(parts)==4 and parts[:2]==['board','threads'] and parts[3]=='messages')):
            pass
        elif method=='POST' and (path in allowed_post or (len(parts)==3 and parts[0]=='requests' and parts[2] in ('approve','decline','preview')) or (len(parts)==4 and parts[:2]==['board','threads'] and parts[3]=='messages')):
            pass
        else:
            self.set_status(404);self.finish({'error':'not found'});return
        if '..' in parts or any('/' in p for p in parts):
            self.set_status(400);self.finish({'error':'path'});return
        try:
            secret=SECRET_FILE.read_text().strip()
            request=HTTPRequest(BRIDGE+'/local/'+path,method=method,body=self.request.body if method=='POST' else None,headers={'Content-Type':'application/json','X-Classroom-Local':secret},request_timeout=120)
            response=await AsyncHTTPClient().fetch(request,raise_error=False)
        except (OSError,HTTPClientError):
            self.set_status(503);self.finish({'error':'Classroom bridge unavailable'});return
        self.set_status(response.code);self.set_header('Content-Type','application/json');self.finish(response.body)

def _jupyter_server_extension_points():return [{'module':'classroom.server'}]
def _load_jupyter_server_extension(serverapp):
    pattern=url_path_join(serverapp.web_app.settings['base_url'],'classroom','api','v1','(.*)')
    serverapp.web_app.add_handlers('.*$',[(pattern,ClassroomHandler)])
