# TSST 回測模組 Version 2
與第一版的差異在於，第一版將整個回測模組抽出來包成 exe
而這一版的是改用 Cython 撰寫主要的驗證模組與入口模組，最後打包成 pyd 後再讓使用者使用
並且棄用 Redis 改用 Queue 與執行緒進行程式間的訊號溝通

## 打包指令
```bash
# 生成 pyd 放在 example 下，主要用於測試
python setup.py build_ext --build-lib  example --inplace
```

```bash
# 包成 wheel 檔
python -m build
```