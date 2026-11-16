"""Transport-transparent launcher of pinned originals with saved tool paths."""
import os
from pathlib import Path
import sys

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from reverse_fusion.provider_runtime import launch_environment
from reverse_fusion.runtime import node_runtime
from reverse_fusion.craft_mcp import mcp_binary
from reverse_fusion.mcp_process import McpProcess

try:
    arguments=sys.argv[1:]
    if not arguments or (arguments[0] not in {'rea','craft','rea-cli'}) or (arguments[0]!='rea-cli' and len(arguments)!=1):
        raise ValueError('Expected rea, craft or rea-cli followed by official CLI arguments')
    environment=launch_environment(root)
    if arguments[0] in {'rea','rea-cli'}:
        node,_=node_runtime(root)
        if not node:raise ValueError('Pinned REA Node runtime missing')
        command=[node,str(root/'vendor/rea/package/scripts/rea.mjs'),*(['mcp'] if arguments[0]=='rea' else arguments[1:])]
    else:
        command=[str(mcp_binary(root)),'--all-tools','--deep-mode','--allow-run','--state-dir',str(root/'state/craft-mcp')]
    # Windows CRT execve cannot safely replace an interactive redirected process.
    # Inherit the original protocol handles without parsing/re-serializing MCP,
    # and own the actual server plus its children until shutdown.
    owner=McpProcess(command,cwd=Path.cwd() if arguments[0]=='rea-cli' else root,env=environment,stdio={
        'stdin':sys.stdin.buffer,'stdout':sys.stdout.buffer,'stderr':sys.stderr.buffer})
    try: code=owner.process.wait()
    finally: owner.close(grace_seconds=0)
    raise SystemExit(code)
except (OSError,ValueError,KeyError) as error:
    print(f'Reverse Fusion MCP launch: {error}',file=sys.stderr)
    raise SystemExit(2)
