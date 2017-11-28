# 新坑

- [ ] github 中国区用户数据
   - [x] location 含有 china。
   - [x] 先爬 100 个，排序。
   - [ ] 测试成功再爬1000个，再爬所有（2000）。
   - [ ] 可以追加没有写 location 的进列表。
- [x] 统计 pinned repo，没有的话就 popular repo。org 不自己挂出来的就不管了，太多了。
- [x] 贡献率等于 commit 在整个 repo 中占的比重
    - https://github.com/Wox-launcher/Wox/graphs/contributors
    - https://developer.github.com/v3/repos/statistics/#get-contributors-list-with-additions-deletions-and-commit-counts
- [x] 贡献数=repo 星星 * 贡献率
- [ ] 移除 markdown 工程师。
    - repo 语言是代码，即 https://api.github.com/repos/xx/xx/languages
    - 且该语言的文件在所有文件中占比超过50%，即 https://github.com/Wox-launcher/Wox/search?l=C%23
    - 需要新写个 网页爬虫 api，专门用来爬 repo search 的数据。v3 v4 都没有这个数据。
- [ ] ui 抄 http://ghrc.babits.top/





