# 新坑

- [ ] github 中国区用户数据
   - [x] location 含有 china。
   - [x] 先爬 100 个，排序。
   - [ ] 测试成功再爬1000个，再爬所有（2000）。
   - [x] 可以追加没有写 location 的进列表。
- [x] 统计 pinned repo，没有的话就 popular repo。org 不自己挂出来的就不管了，太多了。
- [x] 贡献率等于 commit 在整个 repo 中占的比重
    - https://github.com/Wox-launcher/Wox/graphs/contributors
    - https://developer.github.com/v3/repos/statistics/#get-contributors-list-with-additions-deletions-and-commit-counts
- [x] 贡献数=repo 星星 * 贡献率
- [x] 移除 markdown 工程师。
    - repo 语言是代码，即 https://api.github.com/repos/xx/xx/languages
    - 且该语言的文件在所有文件中占比超过50%，即 https://github.com/Wox-launcher/Wox/search?l=C%23
    - 需要新写个 网页爬虫 api，专门用来爬 repo search 的数据。v3 v4 都没有这个数据。
- [x] 贡献考虑当前时间段，比如过去三年的 commit
- [ ] 贡献考虑当前时间段对应的 star，比如过去三年的 star，而不是总 star
    - https://developer.github.com/v3/activity/starring/#alternative-response-with-star-creation-timestamps
    - https://developer.github.com/v4/reference/interface/starrable/
- [x] ui 抄 http://ghrc.babits.top/
- [x] 定时爬虫和自动重启爬虫

# 本地运行

下载 vagrant 并运行：
```bash
vagrant up
```

能看见如下输出，打开其中正确地址：
```bash
==> default: http://10.0.2.15
==> default: http://192.168.0.122
```

手动安装自行参照 `misc/provision.sh` 中的命令

# 参数

本地开发自行调整
1. `config.py` 中的
    - `user_count` 抓多少个用户的信息
    - `count_per_request` 抓所有用户信息的时候每次请求多少条数据
    - `cache_time` 缓存多久失效
2. `rank.timer` 中的
    - `OnUnitInactiveSec`  多久程序运行一次







