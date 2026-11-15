// Use the official MCP comparison with the exact retained source records.
// REA's path-based CLI builds internal member records without exporting them;
// those hidden IDs cannot form a portable, closed Evidence archive.
import fs from 'node:fs';
import path from 'node:path';
import { Client } from '../vendor/rea/package/node_modules/@modelcontextprotocol/client/dist/index.mjs';
import { StdioClientTransport } from '../vendor/rea/package/node_modules/@modelcontextprotocol/client/dist/stdio.mjs';
import { readEvidence } from './proof-support.mjs';

const [leftFile, rightFile, output] = process.argv.slice(2);
if (![leftFile, rightFile, output].every(Boolean)) throw new Error('usage: compare-managed-evidence.mjs left-members.json right-members.json output.json');
const transport = new StdioClientTransport({
  command: process.execPath, args: [path.resolve('vendor/rea/package/scripts/rea.mjs'), '--mcp'],
  cwd: process.cwd(), env: { ...process.env, REA_MCP_TOOL_CATALOG_PROFILE: 'full', REA_MCP_MAX_INPUT_ELEMENTS: '16384' }, stderr: 'pipe',
});
let diagnostics = '';
transport.stderr?.on('data', (chunk) => { diagnostics = (diagnostics + chunk.toString()).slice(-2000); });
const client = new Client({ name: 'reverse-fusion-managed-comparison', version: '1.0.0' });
try {
  await client.connect(transport, { timeout: 30000 });
  const catalog = await client.listTools(undefined, { timeout: 30000 });
  const tool = catalog.tools.find(({ name }) => name === 'compare_managed_members');
  if (!tool?.inputSchema?.properties?.left || !tool.inputSchema.properties.right) throw new Error('Official managed comparison schema unavailable');
  const result = await client.callTool({ name: tool.name, arguments: { left: readEvidence(leftFile), right: readEvidence(rightFile) } }, { timeout: 30000, toolDefinition: tool });
  if (result.isError) throw new Error(JSON.stringify(result.structuredContent ?? result.content));
  const evidence = result.structuredContent;
  // Validate the response before writing an envelope consumed by later stages.
  const { parseEvidence } = await import('../vendor/rea/package/dist/domain/evidence.js');
  parseEvidence(evidence);
  fs.writeFileSync(output, JSON.stringify({ ok: true, data: evidence }, null, 2) + '\n', 'utf8');
  console.log(JSON.stringify({ status: 'pass', evidence_id: evidence.evidence_id, sources: evidence.evidence_links }));
} catch (error) {
  throw new Error(`${error.message}\n${diagnostics}`, { cause: error });
} finally {
  await client.close();
  await transport.close();
}
