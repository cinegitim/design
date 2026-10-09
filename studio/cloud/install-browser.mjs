import {createRequire} from 'node:module';
import {dirname, join} from 'node:path';
import {spawnSync} from 'node:child_process';
const require=createRequire(import.meta.url);
// The CLI subpath is not exported in the pinned package; package.json is.
const cli=join(dirname(require.resolve('playwright-core/package.json')),'cli.js');
const r=spawnSync(process.execPath,[cli,'install','--with-deps','chromium'],{stdio:'inherit'});
if(r.error)throw r.error;
process.exit(r.status??1);
