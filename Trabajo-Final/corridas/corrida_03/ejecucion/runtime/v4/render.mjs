// Spreadsheet authoring uses the documented @oai/artifact-tool API.
import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';

const [specPath, output] = process.argv.slice(2);
const specs = JSON.parse(await fs.readFile(specPath, 'utf8'));
await fs.mkdir(output, {recursive:true});
const letters = n => {let s=''; for(n++; n; n=Math.floor((n-1)/26)) s=String.fromCharCode(65+(n-1)%26)+s; return s;};
for (const [filename, spec] of Object.entries(specs)) {
  const w = Workbook.create();
  for(const s of spec.sheets) w.worksheets.add(s.name);
  for(const s of spec.sheets) {
    const sheet = w.worksheets.getItem(s.name);
    sheet.showGridLines = false;
    const end = `${letters(s.rows[0].length-1)}${s.rows.length}`;
    sheet.getRange(`A1:${end}`).values = s.rows;
    for(const [cell, formula] of Object.entries(s.formulas)) sheet.getRange(cell).formulas=[[formula]];
    const used=sheet.getRange(`A1:${end}`);
    used.format.font={name:'Arial',size:11,color:'#172B4D'};
    used.format.columnWidth=19;
    used.format.rowHeight=23;
    used.setNumberFormat('#,##0');
    sheet.getRange(`A1:${letters(s.rows[0].length-1)}1`).format={fill:'#243746',font:{bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:64};
    if(s.name==='Summary') {
      used.format.columnWidth=44;
      sheet.getRange('B1:B20').format.columnWidth=76;
      sheet.getRange('B16:B20').format.wrapText=true;
      sheet.getRange('A16:B20').format.rowHeight=34;
      for(const r of [10,12,13,14]) sheet.getRange(`B${r}`).setNumberFormat('0.00%');
      sheet.getRange('B11').conditionalFormats.add('containsText',{text:'EXCEEDED',format:{fill:'#FCE4D6',font:{color:'#9C0006',bold:true}}});
      sheet.getRange('B11').conditionalFormats.add('containsText',{text:'OK',format:{fill:'#E2EFDA'}});
    } else {
      sheet.freezePanes.freezeRows(1);
      for(let j=0;j<s.rows[0].length;j++) {
        const header=s.rows[0][j], col=letters(j), r=sheet.getRange(`${col}2:${col}${s.rows.length}`);
        if(/%|_Pct|^X$|^General_Increase$|^Promotion_Increase$|^Progression_Increase$/.test(header)) r.setNumberFormat('0.00%');
        if(/Compa|Ratio|Weight/.test(header)) r.setNumberFormat('0.000');
        if(/Flags|Flag|Approval|Rank|Market_Job|Population/.test(header)) sheet.getRange(`${col}1:${col}${s.rows.length}`).format.columnWidth=28;
        if(header==='Notes') {
          sheet.getRange(`${col}1:${col}${s.rows.length}`).format.columnWidth=65;
          r.format.wrapText=true;
          r.format.rowHeight=40;
        }
      }
      if(s.name==='Global_Parameters') {
        sheet.getRange(`A1:A${s.rows.length}`).format.columnWidth=32;
        for(let i=1;i<s.rows.length;i++) if(['%','fraction'].includes(s.rows[i][2])) sheet.getRange(`B${i+1}`).setNumberFormat('0.00%');
      }
      if(s.review) {
        sheet.getRange(`R2:R${s.rows.length}`).format.fill='#FFF2CC';
        sheet.getRange(`V2:V${s.rows.length}`).format.columnWidth=38;
        sheet.getRange(`Y2:Y${s.rows.length}`).format.columnWidth=32;
      }
    }
  }
  const errors=await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!',options:{useRegex:true,maxResults:20},maxChars:2000});
  console.log(filename,errors.ndjson);
  if(process.env.SALARY_PREVIEW_DIR) {
    await fs.mkdir(process.env.SALARY_PREVIEW_DIR,{recursive:true});
    for(const s of spec.sheets) {
      const ranges=s.review?['A1:J7','K1:U7','V1:AA7']:[s.name==='Summary'?'A1:B20':`A1:${letters(Math.min(s.rows[0].length-1,8))}${Math.min(s.rows.length,10)}`];
      for(let i=0;i<ranges.length;i++) {
        const img=await w.render({sheetName:s.name,range:ranges[i],scale:1,format:'png'});
        await fs.writeFile(path.join(process.env.SALARY_PREVIEW_DIR,`${filename}-${s.name}-${i}.png`),new Uint8Array(await img.arrayBuffer()));
      }
    }
  }
  const file=await SpreadsheetFile.exportXlsx(w);
  await file.save(path.join(output,filename));
}
