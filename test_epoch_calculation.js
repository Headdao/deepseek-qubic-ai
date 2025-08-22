// 測試 Epoch 進度計算邏輯
const statsData = {
    currentTick: 31584874,
    ticksInCurrentEpoch: 84874,
    epochTickQuality: 92.080025,
    emptyTicksInCurrentEpoch: 6722,
    epoch: 175
};

console.log('=== Epoch 進度計算測試 ===');
console.log('原始數據:', statsData);

// 計算 Initial Tick
const initialTick = statsData.currentTick - statsData.ticksInCurrentEpoch;
console.log('Initial Tick:', initialTick.toLocaleString());

// 計算預估總長度
const estimatedTotalTicks = Math.round(statsData.ticksInCurrentEpoch * (100 / Math.max(statsData.epochTickQuality, 1)));
console.log('預估總 Ticks:', estimatedTotalTicks.toLocaleString());

// 進度百分比
const progressPercentage = Math.min(statsData.epochTickQuality, 100);
console.log('進度百分比:', progressPercentage.toFixed(1) + '%');

// 剩餘 Ticks
const remainingTicks = Math.max(0, estimatedTotalTicks - statsData.ticksInCurrentEpoch);
console.log('剩餘 Ticks:', remainingTicks.toLocaleString());

// 預估剩餘時間 (假設每 tick 1 秒)
const remainingSeconds = remainingTicks * 1;
if (remainingSeconds > 3600) {
    const hours = Math.floor(remainingSeconds / 3600);
    const minutes = Math.floor((remainingSeconds % 3600) / 60);
    console.log('預估剩餘時間:', `${hours}h ${minutes}m`);
} else if (remainingSeconds > 60) {
    const minutes = Math.floor(remainingSeconds / 60);
    console.log('預估剩餘時間:', `${minutes}m`);
} else {
    console.log('預估剩餘時間:', `${remainingSeconds}s`);
}

console.log('=== 計算完成 ===');
