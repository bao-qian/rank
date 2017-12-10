# 程序员千人计划

## 特性

- **代码** 贡献 **率** 排名
- 会统计你在其他仓库的贡献，如 org 账户或者其他个人 repo。
- 星星贡献 = commit 所占比率 * 总星星。
- 会移除教程类和资源收集类仓库，这是纯代码排名。
- alpha 地址： http://139.59.106.136

## 本地运行

1. python 要求 3.6。
2. clone 代码。
3. 生成一个 personal access token，并以 `token = 'xxxxxxxxxx'` 形式放在 `misc/secret.py` 中。
4. 运行下面代码

```bash
cp misc/test_config.py misc/config.py
pip install PyQuery SQLAlchemy
python -m source.main 
```

## todo

- [ ] 更好看的 ui
- [ ] 语言排行榜，并在总榜的语言单元格上加上链接
- [ ] debug 页面，含 invalid repo contribution
- [ ] async / multithread
- [ ] 分页

## github error
- error code 202 for v3 statistics api
    - https://developer.github.com/v3/repos/statistics/
    - use last cache if possible otherwise sleep
- error code 451 for DCMA takedown
    - https://developer.github.com/changes/2016-03-17-the-451-status-code-is-now-supported/
    - log and block those users
- [ ] timeout icon in github search page
    - https://help.github.com/articles/troubleshooting-search-queries/
    - use last cache if possible otherwise return empty
    