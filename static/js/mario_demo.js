const rewards = [
    "🥈 大銀袋",
    "🥇 大金袋",
    "✨ 準提銀袋",
    "🔥 準提金袋"
];

function randomReward() {
    return rewards[Math.floor(Math.random() * rewards.length)];
}

function playMario() {

    const slot1 = document.getElementById("slot1");
    const slot2 = document.getElementById("slot2");
    const slot3 = document.getElementById("slot3");

    const result = document.getElementById("result");

    result.innerHTML = "轉動中...";

    let count = 0;

    const timer = setInterval(() => {

        slot1.innerHTML = randomReward();
        slot2.innerHTML = randomReward();
        slot3.innerHTML = randomReward();

        count++;

        if (count > 20) {

            clearInterval(timer);

            const finalReward = randomReward();

            slot1.innerHTML = finalReward;
            slot2.innerHTML = finalReward;
            slot3.innerHTML = finalReward;

            result.innerHTML =
                `🎉 恭喜獲得：${finalReward}`;

        }

    }, 100);

}