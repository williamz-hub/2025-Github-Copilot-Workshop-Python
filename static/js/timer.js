let timer = 1500;
let interval = null;
const timerDisplay = document.getElementById('timer');
const startBtn = document.getElementById('start');
const resetBtn = document.getElementById('reset');

function updateDisplay() {
    const min = String(Math.floor(timer / 60)).padStart(2, '0');
    const sec = String(timer % 60).padStart(2, '0');
    timerDisplay.textContent = `${min}:${sec}`;
}

startBtn.onclick = function() {
    if (interval) return;
    interval = setInterval(() => {
        if (timer > 0) {
            timer--;
            updateDisplay();
        } else {
            clearInterval(interval);
            interval = null;
        }
    }, 1000);
};

resetBtn.onclick = function() {
    clearInterval(interval);
    interval = null;
    timer = 1500;
    updateDisplay();
};

updateDisplay();
