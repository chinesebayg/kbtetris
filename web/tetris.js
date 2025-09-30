// Small Tetris for Canvas
const COLS = 10, ROWS = 20, CELL = 30;
const canvas = document.getElementById('board');
const ctx = canvas.getContext('2d');
canvas.width = COLS * CELL; canvas.height = ROWS * CELL;

const COLORS = ['cyan','blue','orange','yellow','green','purple','red'];

const SHAPES = {
  I: [
    [[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]],
    [[0,0,1,0],[0,0,1,0],[0,0,1,0],[0,0,1,0]]
  ],
  J: [
    [[1,0,0],[1,1,1],[0,0,0]],
    [[0,1,1],[0,1,0],[0,1,0]],
    [[0,0,0],[1,1,1],[0,0,1]],
    [[0,1,0],[0,1,0],[1,1,0]]
  ],
  L: [
    [[0,0,1],[1,1,1],[0,0,0]],
    [[0,1,0],[0,1,0],[0,1,1]],
    [[0,0,0],[1,1,1],[1,0,0]],
    [[1,1,0],[0,1,0],[0,1,0]]
  ],
  O: [ [[1,1],[1,1]] ],
  S: [ [[0,1,1],[1,1,0],[0,0,0]], [[0,1,0],[0,1,1],[0,0,1]] ],
  T: [ [[0,1,0],[1,1,1],[0,0,0]], [[0,1,0],[0,1,1],[0,1,0]], [[0,0,0],[1,1,1],[0,1,0]], [[0,1,0],[1,1,0],[0,1,0]] ],
  Z: [ [[1,1,0],[0,1,1],[0,0,0]], [[0,0,1],[0,1,1],[0,1,0]] ]
};
const KEYS = Object.keys(SHAPES);

function makeGrid(){
  return Array.from({length:ROWS},()=>Array.from({length:COLS},()=>null));
}

class Piece{
  constructor(type){
    this.type = type;
    this.rot = 0;
    this.shape = SHAPES[type][this.rot];
    this.x = Math.floor(COLS/2 - this.shape[0].length/2);
    this.y = 0;
    this.color = COLORS[KEYS.indexOf(type)];
  }
  rotate(grid){
    const old = this.rot;
    this.rot = (this.rot+1)%SHAPES[this.type].length;
    this.shape = SHAPES[this.type][this.rot];
    if(!valid(this,grid,this.x,this.y)){
      for(const dx of [-1,1,-2,2]){ if(valid(this,grid,this.x+dx,this.y)){ this.x+=dx; return true }}
      this.rot = old; this.shape = SHAPES[this.type][this.rot]; return false
    }
    return true
  }
  cells(){
    const out=[];
    for(let r=0;r<this.shape.length;r++)for(let c=0;c<this.shape[r].length;c++)if(this.shape[r][c])out.push([this.x+c,this.y+r]);
    return out;
  }
}

function valid(piece,grid,x,y){
  for(let r=0;r<piece.shape.length;r++)for(let c=0;c<piece.shape[r].length;c++){
    if(!piece.shape[r][c]) continue;
    const gx=x+c, gy=y+r;
    if(gx<0||gx>=COLS||gy<0||gy>=ROWS) return false;
    if(grid[gy][gx]!=null) return false;
  }
  return true;
}

function lock(piece,grid){
  for(const [x,y] of piece.cells()) if(y>=0) grid[y][x]=piece.color;
}

function clearLines(grid){
  const newGrid = grid.filter(row=>row.some(c=>c==null));
  const cleared = ROWS - newGrid.length;
  while(newGrid.length<ROWS) newGrid.unshift(Array.from({length:COLS},()=>null));
  return [newGrid,cleared];
}

// game state
let grid = makeGrid();
let current = new Piece(KEYS[Math.floor(Math.random()*KEYS.length)]);
let next = new Piece(KEYS[Math.floor(Math.random()*KEYS.length)]);
let fall=0, fallSpeed=0.5, score=0, lines=0, level=1;
let moveLeft=false, moveRight=false, rotate=false, soft=false;
let running=true, paused=false;

function draw(){
  ctx.clearRect(0,0,canvas.width,canvas.height);
  // grid
  for(let y=0;y<ROWS;y++)for(let x=0;x<COLS;x++){
    ctx.fillStyle = grid[y][x]||'#000';
    ctx.fillRect(x*CELL,y*CELL,CELL,CELL);
    ctx.strokeStyle='#222'; ctx.strokeRect(x*CELL,y*CELL,CELL,CELL);
  }
  // piece
  for(const [x,y] of current.cells()){
    if(y>=0){ ctx.fillStyle = current.color; ctx.fillRect(x*CELL,y*CELL,CELL,CELL); ctx.strokeStyle='#fff'; ctx.strokeRect(x*CELL,y*CELL,CELL,CELL); }
  }
  document.getElementById('score').innerText = 'Score: '+score;
  document.getElementById('lines').innerText = 'Lines: '+lines;
  document.getElementById('level').innerText = 'Level: '+level;
}

let last = performance.now();
function loop(now){
  const dt = (now-last)/1000; last=now; fall+=dt;
  if(!paused){
    if(moveLeft){ if(valid(current,grid,current.x-1,current.y)) current.x--; moveLeft=false }
    if(moveRight){ if(valid(current,grid,current.x+1,current.y)) current.x++; moveRight=false }
    if(rotate){ if(current.rotate(grid)){} rotate=false }
    let speed = fallSpeed/(1+(level-1)*0.1);
    if(soft) speed = Math.max(0.02, speed/5);
    if(fall>=speed){ fall=0; if(valid(current,grid,current.x,current.y+1)) current.y++; else { lock(current,grid); [grid,cleared]=clearLines(grid); if(cleared){ score+=cleared*100; lines+=cleared; level = 1+Math.floor(lines/10) } current=next; next=new Piece(KEYS[Math.floor(Math.random()*KEYS.length)]); if(!valid(current,grid,current.x,current.y)){ alert('Game Over! Score:'+score); running=false } } }
  }
  draw(); if(running) requestAnimationFrame(loop);
}
requestAnimationFrame(loop);

window.addEventListener('keydown',e=>{
  if(e.key==='Escape' || e.key.toLowerCase()==='q') running=false;
  if(e.key==='p') paused=!paused;
  if(e.key==='ArrowLeft') moveLeft=true;
  if(e.key==='ArrowRight') moveRight=true;
  if(e.key==='ArrowUp' || e.key.toLowerCase()==='x') rotate=true;
  if(e.key==='ArrowDown') soft=true;
  if(e.code==='Space'){
    while(valid(current,grid,current.x,current.y+1)) current.y++;
    lock(current,grid); [grid,cleared]=clearLines(grid); if(cleared){ score+=cleared*100; lines+=cleared; level = 1+Math.floor(lines/10) } current=next; next=new Piece(KEYS[Math.floor(Math.random()*KEYS.length)]);
  }
});
window.addEventListener('keyup',e=>{ if(e.key==='ArrowDown') soft=false; if(e.key==='ArrowLeft') moveLeft=false; if(e.key==='ArrowRight') moveRight=false; if(e.key==='ArrowUp' || e.key.toLowerCase()==='x') rotate=false });
