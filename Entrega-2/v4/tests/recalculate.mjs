// Independently evaluate the exported Excel formulas after a human-style edit.
import {FileBlob, Workbook, SpreadsheetFile} from '@oai/artifact-tool';
const [source,target]=process.argv.slice(2);
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(source));
w.worksheets.getItem('Detail').getRange('R2').values=[[0.01]];
console.log((await w.inspect({kind:'table',range:'Summary!A4:B11',include:'values,formulas',tableMaxRows:8,tableMaxCols:2,maxChars:2000})).ndjson);
await (await SpreadsheetFile.exportXlsx(w)).save(target);
