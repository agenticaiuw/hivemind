import fs from 'node:fs/promises';
import path from 'node:path';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const root = '/Users/evanliu/agentic-gadget';
const session = path.join(root, 'agent_sessions/2026_09_23_ECE_CLUB_BUDGET');
const out = path.join(root, 'outputs/01a0d046-7d49-7871-8a87-73ebb2cf093f');
const receipts = JSON.parse(await fs.readFile(path.join(session, 'purchase-evidence.json'), 'utf8'));
const wb = Workbook.create();
const budget = wb.worksheets.add('Budget');
const build = wb.worksheets.add('Manufacturing');
const parts = wb.worksheets.add('Parts');
const actuals = wb.worksheets.add('Purchases');
const navy = '#233E52', ink = '#172B3A', muted = '#536773', pale = '#EDF2F5', blue = '#145CAA', green = '#267044';
const money = '$#,##0.00;($#,##0.00);"—"';
const wholeMoney = '$#,##0;($#,##0);"—"';
const num = '#,##0.0;(#,##0.0);"—"';
const val = (s,a,v) => {s.getRange(a).values = [[v]];};
const formula = (s,a,f) => {s.getRange(a).formulas = [[f]]; s.getRange(a).format.font.color = f.includes('!') ? green : ink;};
function base(s, end, widths) {
  s.showGridLines = false;
  s.getRange(`A1:J${end}`).format.font = {name:'Arial',size:10,color:ink};
  s.getRange(`A1:J${end}`).format.rowHeight = 24;
  s.getRange(`A1:J${end}`).format.verticalAlignment = 'center';
  s.getRange(`A1:A${end}`).format.columnWidth = 3;
  for (const [c,w] of Object.entries(widths)) s.getRange(`${c}1:${c}${end}`).format.columnWidth = w;
  s.tabColor = navy;
}
function title(s,t,sub) {
  val(s,'B2',t);s.getRange('B2').format.font = {size:16,bold:true,color:navy};
  val(s,'B3',sub);s.getRange('B3').format.font.color=muted;
}
function header(s,range,labels) {
  s.getRange(range).values=[labels];
  s.getRange(range).format={fill:navy,font:{color:'#FFFFFF',bold:true},horizontalAlignment:'center',verticalAlignment:'center',wrapText:true,rowHeight:30};
}
function section(s,row,label,last='F') {
  val(s,`B${row}`,label);s.getRange(`B${row}:${last}${row}`).format={fill:pale,font:{bold:true,color:navy},rowHeight:28};
}
function total(s,row,last='F') {
  s.getRange(`B${row}:${last}${row}`).format.font.bold=true;
  s.getRange(`B${row}:${last}${row}`).format.borders={top:{style:'thin',color:'#A5B5C0'}};
}
function editable(s,address,fmt) {
  s.getRange(address).format.fill='#FFF3D1';s.getRange(address).format.font.color=blue;
  if(fmt)s.getRange(address).setNumberFormat(fmt);
}
function sumGuard(s,address,start,end,column='F') {
  const span=`${column}${start}:${column}${end}`;
  formula(s,address,`=IF(COUNT(${span})=${end-start+1},SUM(${span}),NA())`);
}

base(budget,66,{B:51,C:18,D:3,E:87,F:3});
title(budget,'Agentic AI UW | 30-device development budget','Funding request to UW–Madison ECE · September 23, 2026 · USD');
val(budget,'B4','Student-led wearable research and manufacturing pilot');
header(budget,'B6:C6',['Cash budget','Amount']);
const summary=[
 [7,'Final pilot manufacturing',"='Manufacturing'!F18",'Includes extra assembly starts; student final assembly has no wage charge.'],
 [8,'Development and prototype revisions',"='Manufacturing'!F34",'Two small engineering runs, test materials and outside engineering review.'],
 [9,'Campus access fees',"='Manufacturing'!F38",'Base assumes eligible access; edit the number of paid passes below.'],
 [10,'New spending before contingency','=SUM(C7:C9)',''],
 [11,'Contingency reserve','=IF(COUNT(C31)<>1,NA(),C10*C31)','20% planning reserve for quote changes and rework beyond the spare starts.'],
 [12,'New funding requirement','=SUM(C10:C11)','Excludes prior purchases and volunteer wages.'],
 [13,'ECE request, rounded up','=IF(OR(COUNT(C32)<>1,C32<=0),NA(),ROUNDUP((C12+C15)/C32,0)*C32)','Rounded to the funding increment below; includes reimbursement only if selected.'],
 [15,'Prior-purchase reimbursement requested','=IF(C33="",NA(),\'Purchases\'!F34*C33)','Default is no reimbursement. Prior spending is documented separately.'],
 [16,'Documented prior prototype spending',"='Purchases'!F34",'Personal development spending; contribution/ownership transfer not assumed.'],
 [18,'Manufacturing cost per accepted device','=IF(OR(COUNT(C25)<>1,C25<=0),NA(),C7/C25)','Final batch only, including batch setup and fixture; excludes development/reserve.'],
 [19,'New program cost per accepted device','=IF(OR(COUNT(C25)<>1,C25<=0),NA(),C12/C25)','Includes development and contingency; not a recurring unit production price.'],
 [20,'Estimated volunteer contribution (hours)','=C49','Planning workload, not confirmed member commitments; no wages requested.']
];
for(const [r,l,f,n] of summary){val(budget,`B${r}`,l);formula(budget,`C${r}`,f);val(budget,`E${r}`,n);}
budget.getRange('C7:C19').setNumberFormat(money);budget.getRange('C13').setNumberFormat(wholeMoney);budget.getRange('C20').setNumberFormat(num);
budget.getRange('B7:E20').format.rowHeight=27;
budget.getRange('E7:E20').format.font.color=muted;budget.getRange('E7:E20').format.wrapText=true;
for(const r of [7,11,13,16,18,19,20])budget.getRange(`B${r}:E${r}`).format.rowHeight=35;
for(const r of [10,12,13])total(budget,r,'C');
budget.getRange('B13:C13').format.fill=pale;budget.getRange('C13').format.font.size=16;
budget.getRange('C7:C20').format.font.color=ink;
section(budget,23,'Editable planning assumptions','C');
val(budget,'E23','Amber cells are editable. Formulas update costs and quantities.');
const assumptions=[
 [25,'Accepted devices',30,'Usable devices delivered to the club.'],
 [26,'Extra assembly starts',0.2,'20% extra starts creates six additional units at the base target; no yield guarantee.'],
 [27,'Final assembly starts',null,'Rounded up from target × (1 + extra-start percentage).'],
 [28,'Engineering prototype runs',2,'Separate boards made before committing to the final batch.'],
 [29,'Prototype starts per run',5,'Small first and second revisions.'],
 [30,'Total prototype starts',null,'Additional to final assembly starts; not counted as delivered devices.'],
 [31,'Contingency rate',0.2,'Applied to all new cash costs; no contingency on old receipts.'],
 [32,'Funding rounding increment',100,'Round the requested amount up to this number of dollars.'],
 [33,'Reimburse prior purchases? (1=yes)',0,'Leave at 0 for new funding only; 1 adds $331.60 before rounding.'],
 [34,'Prototype parts price premium',0.2,'Small orders and part substitutions versus final-batch component allowances.'],
 [35,'Non-CoE semester access passes',0,'0 assumes eligible campus access. Confirm all participating members before ordering.'],
 [36,'Price per non-CoE semester pass',150,'UW DI Lab published M-Pass rate; materials are charged separately.']
];
for(const [r,l,v,n] of assumptions){val(budget,`B${r}`,l);if(v!==null){val(budget,`C${r}`,v);editable(budget,`C${r}`);}val(budget,`E${r}`,n);}
formula(budget,'C27','=IF(OR(COUNT(C25:C26)<>2,C25<=0,C26<0),NA(),ROUNDUP(C25*(1+C26),0))');
formula(budget,'C30','=IF(OR(COUNT(C28:C29)<>2,C28<0,C29<0),NA(),C28*C29)');
for(const r of [26,31,34])budget.getRange(`C${r}`).setNumberFormat('0.0%');
budget.getRange('C32').setNumberFormat(wholeMoney);budget.getRange('C36').setNumberFormat(wholeMoney);
budget.getRange('E25:E36').format.wrapText=true;budget.getRange('B25:E36').format.rowHeight=32;
budget.getRange('C33').dataValidation={rule:{type:'list',values:['0','1']}};
for(const r of [25,28,29,35])budget.dataValidations.add({range:`C${r}`,rule:{type:'whole',operator:'between',formula1:r===25?1:0,formula2:1000}});
for(const r of [26,31,34])budget.dataValidations.add({range:`C${r}`,rule:{type:'decimal',operator:'between',formula1:0,formula2:1}});

section(budget,39,'Volunteer effort estimate','C');
header(budget,'B40:C40',['Workstream','Hours']);
const work=[[41,'PCB schematic, layout and supplier files',100],[42,'Firmware, audio and power integration',160],[43,'Phone relay and application integration',120],[44,'Enclosure design and fit iterations',50],[45,'Reliability testing and documentation',70],[46,'Project coordination and purchasing',40]];
for(const [r,l,h] of work){val(budget,`B${r}`,l);val(budget,`C${r}`,h);editable(budget,`C${r}`,num);}
val(budget,'B47','Prototype assembly and testing');formula(budget,'C47','=IF(COUNT(C30,C51)<>2,NA(),C30*C51)');
val(budget,'B48','Final assembly, programming and testing');formula(budget,'C48','=IF(COUNT(C27,C52)<>2,NA(),C27*C52)');
val(budget,'B49','Total volunteer hours');sumGuard(budget,'C49',41,48,'C');total(budget,49,'C');budget.getRange('C47:C49').setNumberFormat(num);
val(budget,'B51','Hands-on hours per prototype start');val(budget,'C51',1.5);editable(budget,'C51',num);
val(budget,'B52','Hands-on hours per final assembly start');val(budget,'C52',2);editable(budget,'C52',num);
budget.getRange('C51:C52').setNumberFormat('0.00');
val(budget,'E41','Task-hour allowances cover development of the existing platform, not a new operating system.');
val(budget,'E44','Two hours per final start: wiring/touch-up, case assembly, firmware loading, test and rework allowance.');
val(budget,'E47','Outsourced SMT placement is a cash service in Manufacturing; student work is additional.');
budget.getRange('E41:E48').format.wrapText=true;budget.getRange('B41:E48').format.rowHeight=30;
section(budget,55,'Scope and production gates','C');
const notes=[
 'Basis: nRF5340 BLE pendant with a phone relay. Existing development hardware supports learning and bring-up.',
 'Pilot assumes an available protected LiPo and a printable enclosure adjusted to fit. A fixed miniature round case is not costed.',
 'Before ordering: finish PCB routing/DFM, select battery and speaker, validate phone relay, and obtain BOM/CPL/Gerber-based quotes.',
 'Campus enclosure allowance is $12 per set. It is not a commercial SLS quote; replace it if campus fabrication is unavailable.',
 'Excluded: commercial certification, injection tooling, custom battery NRE/MOQ, phones, computers and ongoing AI/hosting/cellular service.',
 'Access rates: UW DI Lab, https://making.engr.wisc.edu/access/. Printing: https://making.engr.wisc.edu/3dprint-cost/. Checked September 23, 2026.'
];
notes.forEach((t,i)=>{val(budget,`B${57+i}`,t);budget.getRange(`B${57+i}:E${57+i}`).merge();});
budget.getRange('B57:E62').format.wrapText=true;budget.getRange('B57:E62').format.rowHeight=33;

base(parts,32,{B:35,C:11,D:15,E:16,F:26,G:3,H:80});
title(parts,'Candidate component bill of materials','Editable pilot allowances · one assembled device · no cellular modem');
header(parts,'B5:F5',['Component','Qty / device','Unit allowance','Device cost','Price status']);
const bom=[
 ['nRF5340 aQFN MCU',1,10,'Spec-based allowance','Pendant v2 §2.1: Aug 7 indicative @1 $9.74. Requote aQFN stock; HDI/WLCSP is outside this allowance.'],
 ['PDM MEMS microphones',2,3.25,'Spec-based allowance','Respin BOM SPH0641LU4H-1 recorded at $3.22; T5838 remains an alternative. Prior Adafruit PDM breakout $4.95 is a different assembly.'],
 ['BMI270 inertial sensor',1,4.5,'Spec-based allowance','Pendant v2 §2.1 @1 $4.23. Adafruit LSM6DSOX development breakout $11.95 is a different assembly.'],
 ['DRV2605L haptic driver IC',1,2,'Spec-based allowance','Pendant v2 §2.1 unverified estimate ~$1.90. Adafruit breakout receipt $7.95.'],
 ['Haptic actuator',1,3,'Unquoted allowance','Select compatible LRA. Original Adafruit $1.95 vibrating motor is a prototype reference, not final selection.'],
 ['Touch/squeeze or button input',1,2,'Unquoted allowance','Input sensing not finalized; allowance assumes simple button/polymer sensing, not custom metal sensing.'],
 ['256 MB serial NAND flash',1,18.5,'Spec-based allowance','Pendant v2 §2.1 W25N02KV @1 $18.40, then out of stock. Availability and substitute need confirmation.'],
 ['Charger/power management IC',1,3.5,'Spec-based allowance','Pendant v2 §2.1 nPM1304 @1 $2.95; package and charge current need review.'],
 ['Protected LiPo battery',1,12,'Unquoted allowance','Pilot stock-cell allowance. Adafruit historical 500 mAh cell $7.95. Round semi-custom cell NRE/MOQ excluded.'],
 ['Speaker amplifier IC',1,4,'Spec-based allowance','Later respin records MAX98357A at $3.96 @1; prior Adafruit breakout $5.95. Requote stock and packaging.'],
 ['Small speaker',1,4.5,'Spec-based allowance','Respin candidate AS01308MR-2-R recorded at $4.46 @1. Final fit/acoustic selection remains open.'],
 ['Indicator LEDs',1,0.5,'Unquoted allowance','Discrete indicator allowance; current design requires live microphone-state indication.'],
 ['Antenna and RF matching parts',1,0.75,'Unquoted allowance','Pendant v2 antenna estimate ~$0.35 plus matching components; RF layout must be validated.'],
 ['Device charging contacts',1,3,'Unquoted allowance','Pendant v2 magnetic pogo estimate ~$2.50. Mating cable is included in Manufacturing accessories.'],
 ['Crystal pair',1,1.5,'Unquoted allowance','32 MHz and 32.768 kHz pair, small-lot procurement allowance.'],
 ['Passives and load switching',1,4,'Unquoted allowance','Caps, resistors, rail switching and bulk storage; subject to completed schematic.'],
 ['Board connectors/test hardware',1,1,'Unquoted allowance','Small connector/test-interface allowance. External straps and fasteners priced separately.'],
 ['Physical microphone mute switch',1,2,'Unquoted allowance','Separate from user input button. Respin calls for two-pole isolation; candidate SPDT is insufficient. Final switch/boot quote pending.']
];
bom.forEach((r,i)=>{const n=i+6;parts.getRange(`B${n}:D${n}`).values=[[r[0],r[1],r[2]]];formula(parts,`E${n}`,`=IF(COUNT(C${n}:D${n})<>2,NA(),C${n}*D${n})`);val(parts,`F${n}`,r[3]);val(parts,`H${n}`,r[4]);});
val(parts,'B25','Components per assembled device');sumGuard(parts,'E25',6,23,'E');total(parts,25);
editable(parts,'C6:D23');parts.getRange('D6:E25').setNumberFormat(money);
parts.getRange('B6:H23').format.rowHeight=48;parts.getRange('B6:H23').format.wrapText=true;
parts.getRange('F6:F23').setNumberFormat('  @');
val(parts,'B27','All forward component prices are estimates, not verified supplier quotes.');
val(parts,'B28','Sources: Pendant v2 §2.1 (Aug. 7, 2026), speaker/mute respin BOM §2, and historical receipts in Purchases.');
val(parts,'B29','Quantity-100 prices in the old specification are not assumed available for this 36-start pilot.');
parts.freezePanes.freezeRows(5);

base(build,44,{B:43,C:10,D:13,E:17,F:17,G:3,H:76});
title(build,'Manufacturing and development costs','New cash spending only · unit prices are editable planning allowances');
header(build,'B5:F5',['Cost item','Quantity','Unit','Unit cost','Extended cost']);
section(build,6,'Final pilot manufacturing');
const jlc='https://jlcpcb.com/help/article/pcb-assembly-price';
const print='https://making.engr.wisc.edu/3dprint-cost/';
function line(r,desc,q,u,rate,basis) {
  val(build,`B${r}`,desc);val(build,`D${r}`,u);
  if(typeof q==='string')formula(build,`C${r}`,q);else{val(build,`C${r}`,q);editable(build,`C${r}`);}
  if(typeof rate==='string')formula(build,`E${r}`,rate);else{val(build,`E${r}`,rate);editable(build,`E${r}`,money);}
  formula(build,`F${r}`,`=IF(COUNT(C${r},E${r})<>2,NA(),C${r}*E${r})`);val(build,`H${r}`,basis);
}
line(7,'Electronic components',"='Budget'!C27",'device',"='Parts'!E25",'Itemized in Parts. Extra starts buy full part sets; no historical receipt is multiplied by 30.');
line(8,'Four-layer bare PCBs',"='Budget'!C27",'board',8,'Planning allowance: routed aQFN board, conventional four-layer stack. Gerber-based quote required.');
line(9,'Outsourced SMT placement/inspection',"='Budget'!C27",'board',15,`Allowance, not a vendor quote. Setup is separate. Cost structure: ${jlc}`);
line(10,'3D-printed enclosure sets',"='Budget'!C27",'set',12,`Campus fabrication allowance for a complete shell set. Exact geometry quote pending. ${print}`);
line(11,'Strap, charging cable and fit materials',"='Budget'!C27",'kit',18,'Per kit: charging cable $8, strap $4, fasteners $2, acoustic vent/adhesive/gasket $4. Planning allowances.');
line(12,'Final soldering/cleaning consumables',"='Budget'!C27",'device',4,'Solder, flux, braid and cleaning allocation; volunteer touch-up labor is in Budget hours.');
line(13,'SMT setup, stencil and feeder allowance',1,'batch',250,`Fixed small-batch allowance; actual cost depends on assembly sides, feeders and inspection. ${jlc}`);
line(14,'Programming and test fixture',1,'fixture',350,'Pogo fixture, harness and adapters; no new oscilloscope or bench power supply assumed.');
line(15,'Final-batch freight, tax and tariff reserve',1,'batch',400,'Unquoted landed-cost allowance. No sales-tax exemption or specific tariff rate assumed.');
val(build,'B18','Final pilot manufacturing total');sumGuard(build,'F18',7,15);total(build,18);
section(build,20,'Development and prototype revisions');
line(21,'Prototype electronic components',"='Budget'!C30",'device',"=IF(COUNT('Budget'!C34)<>1,NA(),'Parts'!E25*(1+'Budget'!C34))",'Same candidate BOM with editable small-lot price premium in Budget.');
line(22,'Prototype bare PCBs',"='Budget'!C30",'board',25,'Allowance for small four-layer runs, including supplier minimum charges; quote both revisions.');
line(23,'Prototype SMT setup and stencils',"='Budget'!C28",'run',250,`Separate setup for each revision; excludes per-board assembly below. ${jlc}`);
line(24,'Prototype SMT assembly/inspection',"='Budget'!C30",'board',18,'Small-run placement/inspection allowance; specialist manual rework may require reserve.');
line(25,'Prototype printed enclosure sets',"='Budget'!C30",'set',12,`Same campus fabrication allowance as final shells. ${print}`);
line(26,'Prototype bench consumables',"='Budget'!C28",'run',75,'Per run: 2 reusable charge cables × $8 plus $59 wiring, solder, connectors and temporary fixture materials.');
line(27,'Prototype freight, tax and tariffs',"='Budget'!C28",'run',150,'Separate shipping and landed-cost allowance for each revision and component order.');
line(28,'BLE development boards/modules',2,'board',75,'Unquoted nRF5340 evaluation allowance. Existing nRF9160 kit does not substitute for a BLE test platform.');
line(29,'Battery samples and fit evaluation',1,'lot',250,'Sample cells and test materials. Custom battery NRE/minimum order not funded.');
line(30,'Additional enclosure fit-test materials',1,'lot',100,'Extra print iterations beyond the ten functional prototype enclosure sets.');
line(31,'External PCB/RF engineering review',5,'hour',100,'Optional paid specialist review allowance; replace with a firm quote or $0 for donated review.');
val(build,'B34','Development and prototypes total');sumGuard(build,'F34',21,31);total(build,34);
section(build,36,'Conditional campus access');
line(37,'Non-CoE semester access passes',"=IF(COUNT('Budget'!C35)<>1,NA(),'Budget'!C35)",'pass',"=IF(COUNT('Budget'!C36)<>1,NA(),'Budget'!C36)",'UW DI Lab M-Pass access: confirm club/member eligibility. Consumables priced separately.');
val(build,'B38','Campus access fees');formula(build,'F38','=F37');total(build,38);
val(build,'B41','All services and fabrication amounts are planning allowances; obtain supplier quotes after design release.');
build.getRange('B41:H41').merge();build.getRange('B41:H41').format.wrapText=true;
build.getRange('E7:F38').setNumberFormat(money);build.getRange('H6:H38').format.wrapText=true;
for(const [a,b] of [[7,15],[21,31],[37,37]])build.getRange(`B${a}:H${b}`).format.rowHeight=45;
build.getRange('B7:B38').format.wrapText=true;build.freezePanes.freezeRows(5);
build.getRange('D7:D38').format.horizontalAlignment='center';

base(actuals,40,{B:40,C:23,D:11,E:15,F:17,G:3,H:70});actuals.tabColor='#C4B79C';
title(actuals,'Historical prototype purchases','Receipt actuals · July 2026 · excluded from new funding by default');
header(actuals,'B5:F5',['Receipt / item','Purchase date','Quantity','Unit price','Amount']);
const receiptTotalRows=[];let rr=7;
for(const rec of receipts.receipts){
  section(actuals,rr,`${rec.vendor} invoice ${rec.invoice_number}`);rr++;
  const first=rr;
  for(const it of rec.items){val(actuals,`B${rr}`,it.description);val(actuals,`C${rr}`,new Date(rec.order_date+'T12:00:00Z'));val(actuals,`D${rr}`,it.quantity);val(actuals,`E${rr}`,it.unit_usd);formula(actuals,`F${rr}`,`=D${rr}*E${rr}`);val(actuals,`H${rr}`,`${path.basename(rec.source)}; ${it.product_id?'Adafruit #'+it.product_id:it.part_number}. Historical actual, not a current quote.`);rr++;}
  for(const [label,key] of [['Shipping','shipping_usd'],['Tariffs','tariff_usd'],['Sales tax','sales_tax_usd']]){val(actuals,`B${rr}`,label);val(actuals,`F${rr}`,rec[key]);rr++;}
  val(actuals,`B${rr}`,'Invoice total');formula(actuals,`F${rr}`,`=SUM(F${first}:F${rr-1})`);total(actuals,rr);receiptTotalRows.push(rr);rr+=2;
}
// Receipt blocks end at rows 18, 25, 34; keep consolidated total below the blocks.
const historicalRow=rr;
val(actuals,`B${historicalRow}`,'Total documented prior spending');formula(actuals,`F${historicalRow}`,'='+receiptTotalRows.map(r=>`F${r}`).join('+'));total(actuals,historicalRow);
// Link summary to the actual generated total location, avoiding hardcoded block-length assumptions.
formula(budget,'C15',`=IF(COUNT(C33)<>1,NA(),'Purchases'!F${historicalRow}*C33)`);
formula(budget,'C16',`='Purchases'!F${historicalRow}`);
budget.getRange('C15:C16').format.font.color=ink;
actuals.getRange(`C8:C${historicalRow}`).setNumberFormat('mmm d, yyyy');actuals.getRange(`E8:F${historicalRow}`).setNumberFormat(money);
actuals.getRange(`B8:H${historicalRow}`).format.wrapText=true;actuals.getRange(`B8:H${historicalRow}`).format.rowHeight=38;
actuals.freezePanes.freezeRows(5);
const footer=historicalRow+2;val(actuals,`B${footer}`,'Receipts support development history. Ownership, reimbursement eligibility and remaining usable inventory are not inferred.');
actuals.getRange(`B${footer}:H${footer}`).merge();actuals.getRange(`B${footer}:H${footer}`).format.wrapText=true;actuals.getRange(`B${footer}:H${footer}`).format.rowHeight=32;

await fs.mkdir(out,{recursive:true});
wb.recalculate();
const inspect=await wb.inspect({kind:'table',range:'Budget!B6:C20',include:'values,formulas',tableMaxRows:15,tableMaxCols:2,maxChars:6000});
console.log(inspect.ndjson);
const baseAsk=budget.getRange('C13').values[0][0];
const baseCost=budget.getRange('C12').values[0][0];
const prior=actuals.getRange(`F${historicalRow}`).values[0][0];
if(Math.abs(prior-331.60)>0.001)throw new Error('Receipt reconciliation failed');
const expectedParts=bom.reduce((a,x)=>a+x[1]*x[2],0);
const expectedFinal=36*(expectedParts+8+15+12+18+4)+250+350+400;
const expectedDev=10*(expectedParts*1.2+25+18+12)+2*(250+75+150)+150+250+100+500;
const expectedTotal=(expectedFinal+expectedDev)*1.2;
if(typeof baseCost!=='number'||Math.abs(baseCost-expectedTotal)>0.001)throw new Error(`Total mismatch ${baseCost} vs ${expectedTotal}`);
// Input changes exercise recalculation, restoration and unavailable-input behavior.
val(budget,'C25',40);wb.recalculate();
if(budget.getRange('C27').values[0][0]!==48 || budget.getRange('C12').values[0][0]<=baseCost)throw new Error('Quantity sensitivity failed');
val(budget,'C25',30);val(budget,'C33',1);wb.recalculate();
if(Math.abs(budget.getRange('C15').values[0][0]-331.6)>0.001)throw new Error('Reimbursement toggle failed');
val(budget,'C33',0);val(build,'E10',0);wb.recalculate();
if(Math.abs(budget.getRange('C12').values[0][0]-(baseCost-432*1.2))>0.001)throw new Error('Zero-cost donation override failed');
val(build,'E10',null);wb.recalculate();
const missing=String(budget.getRange('C12').values[0][0]);
if(!missing.includes('#'))throw new Error('Missing price failed to invalidate result: '+missing);
val(build,'E10',12);val(budget,'C35',2);wb.recalculate();
if(Math.abs(budget.getRange('C12').values[0][0]-(baseCost+360))>0.001)throw new Error('Access fees sensitivity failed');
val(budget,'C35',0);wb.recalculate();
if(budget.getRange('C13').values[0][0]!==baseAsk)throw new Error('Restoration failed');
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},summary:'Final formula error scan'});
console.log(errors.ndjson);
await fs.writeFile(path.join(session,'verification.json'),JSON.stringify({parts_per_device:expectedParts,final_batch:expectedFinal,development:expectedDev,new_requirement:baseCost,rounded_request:baseAsk,historical_actuals:prior,volunteer_hours:budget.getRange('C49').values[0][0],checks:['independent totals','receipt reconciliation','40-unit sensitivity','prior reimbursement toggle','zero price donation','blank price invalidation','campus access fees','restored inputs'],formula_scan:errors.ndjson},null,2));
for(const [name,range,filename] of [['Budget','B2:E20','budget-summary.png'],['Budget','B23:E52','budget-inputs.png'],['Budget','B55:E62','budget-scope.png'],['Manufacturing','B2:H18','manufacturing-final.png'],['Manufacturing','B20:H41','manufacturing-development.png'],['Parts','B2:H29','parts.png'],['Purchases',`B2:H${footer}`,'purchases.png']]){
 const blob=await wb.render({sheetName:name,range,scale:1.5,format:'png'});
 await fs.writeFile(path.join(session,filename),new Uint8Array(await blob.arrayBuffer()));
}
const xlsx=await SpreadsheetFile.exportXlsx(wb);await xlsx.save(path.join(out,'Agentic_AI_UW_ECE_30_Device_Budget.xlsx'));
console.log(JSON.stringify({baseAsk,baseCost,expectedFinal,expectedDev,expectedParts,historicalRow,output:path.join(out,'Agentic_AI_UW_ECE_30_Device_Budget.xlsx')}));
