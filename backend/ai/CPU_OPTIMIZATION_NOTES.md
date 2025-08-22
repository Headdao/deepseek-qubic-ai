
# CPU 優化建議

## 已實施的優化：
1. 使用 float32 而非 float16（CPU 友善）
2. 啟用 low_cpu_mem_usage
3. 設置較保守的生成參數
4. 添加 Qubic 知識庫增強

## 性能提升技巧：
- 使用 max_new_tokens 而非 max_length
- 降低 temperature 提高一致性
- 使用 torch.no_grad() 進行推理
- 預熱模型（首次推理較慢）

## 監控指標：
- 推理時間：目標 < 10 秒
- 記憶體使用：監控 RAM 消耗
- 回應品質：使用 Qubic 知識驗證
