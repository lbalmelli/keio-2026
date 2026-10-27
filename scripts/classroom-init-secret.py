#!/usr/bin/env python3
from pathlib import Path
import secrets
p=Path('.local/classroom-local-secret');p.parent.mkdir(exist_ok=True);p.parent.chmod(0o700)
if not p.exists():
    p.write_text(secrets.token_urlsafe(48))
    p.chmod(0o644)
    print('Created local bridge secret file')
else:print('Local bridge secret exists')
