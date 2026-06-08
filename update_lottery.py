<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<title>更新開獎</title>

<style>
body{
    background:#062b2f;
    color:white;
    text-align:center;
    font-family: Arial;
}

h2{
    margin-top:30px;
}

.group{
    margin:15px auto;
}

.title{
    margin-bottom:5px;
    color:#aaa;
}

.nums{
    display:flex;
    flex-wrap:wrap;
    justify-content:center;
    gap:8px;
}

.ball{
    width:55px;
    height:55px;
    border-radius:50%;
    background:#123c4a;
    display:flex;
    align-items:center;
    justify-content:center;
    cursor:pointer;
    transition:0.2s;
    font-size:18px;
}

.ball:hover{
    background:#1fa2b8;
}

.ball.active{
    background:#ffb400;
    color:black;
    font-weight:bold;
}

.special{
    background:#444;
}

.special.active{
    background:#ffd700;
    color:black;
}

button{
    margin:10px;
    padding:10px 20px;
    border:none;
    border-radius:8px;
    background:#1fa2b8;
    color:white;
    cursor:pointer;
}

button:hover{
    background:#17c0d6;
}

#counter{
    margin:10px;
    font-size:18px;
    color:#00eaff;
}
</style>
</head>

<body>

<h2>🎯 手動更新開獎</h2>

<form method="POST">

日期：
<input type="date" name="date" required><br><br>

<div id="counter">已選：0 / 6</div>

<!-- 主號區 -->
<div id="mainArea"></div>

<h3>⭐ 特別號</h3>
<div id="specialArea" class="nums"></div>

<br>

<button type="button" onclick="randomPick()">🎲 隨機</button>
<button type="button" onclick="clearAll()">🧹 清空</button>
<br><br>

<input type="hidden" name="numbers" id="numbers">
<input type="hidden" name="special" id="special">

<button type="submit">送出</button>

</form>

<script>
let selected = [];
let special = null;

function createGroup(start, end){
    let div = document.createElement("div");
    div.className = "group";

    let title = document.createElement("div");
    title.className = "title";
    title.innerText = start + " - " + end;

    let nums = document.createElement("div");
    nums.className = "nums";

    for(let i=start;i<=end;i++){
        let b = document.createElement("div");
        b.className = "ball";
        b.innerText = i;

        b.onclick = () => toggleMain(b, i);

        nums.appendChild(b);
    }

    div.appendChild(title);
    div.appendChild(nums);
    return div;
}

// 主號 toggle
function toggleMain(el, num){
    if(selected.includes(num)){
        selected = selected.filter(n=>n!==num);
        el.classList.remove("active");
    }else{
        if(selected.length >= 6){
            alert("最多選6顆");
            return;
        }
        selected.push(num);
        el.classList.add("active");
    }
    updateUI();
}

// 特別號 toggle
function toggleSpecial(el, num){
    document.querySelectorAll("#specialArea .ball")
        .forEach(b=>b.classList.remove("active"));

    if(special === num){
        special = null;
    }else{
        special = num;
        el.classList.add("active");
    }
}

// UI 更新
function updateUI(){
    document.getElementById("counter").innerText =
        "已選：" + selected.length + " / 6";

    document.getElementById("numbers").value =
        selected.join(",");

    document.getElementById("special").value =
        special || "";
}

// 清空
function clearAll(){
    selected = [];
    special = null;

    document.querySelectorAll(".ball")
        .forEach(b=>b.classList.remove("active"));

    updateUI();
}

// 隨機
function randomPick(){
    clearAll();

    while(selected.length < 6){
        let n = Math.floor(Math.random()*49)+1;
        if(!selected.includes(n)) selected.push(n);
    }

    selected.forEach(n=>{
        document.querySelectorAll(".ball")
        .forEach(b=>{
            if(parseInt(b.innerText) === n){
                b.classList.add("active");
            }
        });
    });

    special = Math.floor(Math.random()*49)+1;

    document.querySelectorAll("#specialArea .ball")
    .forEach(b=>{
        if(parseInt(b.innerText) === special){
            b.classList.add("active");
        }
    });

    updateUI();
}

// 初始化
let mainArea = document.getElementById("mainArea");
mainArea.appendChild(createGroup(1,10));
mainArea.appendChild(createGroup(11,20));
mainArea.appendChild(createGroup(21,30));
mainArea.appendChild(createGroup(31,40));
mainArea.appendChild(createGroup(41,49));

// 特別號
let sp = document.getElementById("specialArea");
for(let i=1;i<=49;i++){
    let b = document.createElement("div");
    b.className = "ball special";
    b.innerText = i;

    b.onclick = () => toggleSpecial(b, i);

    sp.appendChild(b);
}
</script>

</body>
</html>