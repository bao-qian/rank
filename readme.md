# 程序员千人计划

## 特性

- **代码** 贡献 **率** 排名
- 会统计你在其他仓库的贡献，如 org 账户或者其他个人 repo。
- 星星贡献 = commit 所占比率 * 总星星。
- 会移除教程类和资源收集类仓库，这是纯代码排名。
- alpha 地址： http://139.59.106.136

## 本地运行

python 要求 3.6

```bash
git clone https://github.com/happlebao/rank.git
cd rank
cp misc/test_config.py misc/config.py
pip install Fabric3 PyQuery SQLAlchemy
python -m source.main 
```

## todo

- [x] github 中国区用户数据
   - [x] location 含有 china。
   - [x] 先爬 100 个，排序。
   - [x] 测试成功再爬1000个，再爬所有（2000）。
   - [x] 可以追加没有写 location 的进列表。
- [x] 统计 pinned repo，没有的话就 popular repo。org 不自己挂出来的就不管了，太多了。
- [x] 贡献率等于 commit 在整个 repo 中占的比重
    - https://github.com/Wox-launcher/Wox/graphs/contributors
    - https://developer.github.com/v3/repos/statistics/#get-contributors-list-with-additions-deletions-and-commit-counts
    - v4 没有这个 api
- [x] 贡献数=repo 星星 * 贡献率
- [x] 移除 markdown 工程师。
    - repo 语言是代码，即 https://api.github.com/repos/xx/xx/languages
    - 且该语言的文件在所有文件中占比超过50%，即 https://github.com/Wox-launcher/Wox/search?l=C%23
    - 需要新写个 网页爬虫 api，专门用来爬 repo search 的数据。v3 v4 都没有这个数据。
- [x] 贡献考虑当前时间段，比如过去三年的 commit
- [x] ui 抄 http://ghrc.babits.top/
- [x] 定时爬虫和自动重启爬虫
- [x] v4 api 自动翻页
- [x] v4 api rate limit 超了后会 sleep。
- [x] 自动翻页的时候考虑 hasnextpage 和 endcursor。
- [x] log http error
- [x] error message for v3 v4
- [x] user_query 变成一个数组 比如 skywind3000 就是 PRC 而不是 china
- [x] 更详尽的 api 报错
- [x] contribute api 202 问题需要单独处理
- [x] 拉黑有 451 问题的用户 
- [x] 查询用户数量最多只有1000 https://github.com/search?p=100&q=location%3Achina&ref=simplesearch&type=Users&utf8=%E2%9C%93
- [x] v4 api error response with 200 status code
- [ ] 贡献考虑当前时间段对应的 star，比如过去三年的 star，而不是总 star
    - https://developer.github.com/v3/activity/starring/#alternative-response-with-star-creation-timestamps
    - https://developer.github.com/v4/reference/interface/starrable/
- [ ] 语言排行榜，并在总榜的语言单元格上加上链接
- [ ] 更好看的 ui
- [ ] debug 页面，含 invalid repo contribution
- [ ] async
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
    