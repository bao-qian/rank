# 新坑

1. 改成 github 中国区代码贡献排名
  1. location 含有 china
  2. 先爬 100 个，排序。测试成功再爬1000个，再爬所有（2000）。
  3. 可以追加没有写 location 的进列表
2. 要统计 org 账户
3. 贡献等于 commit 在整个 repo 中占的比重
    - https://github.com/Wox-launcher/Wox/graphs/contributors
    - https://developer.github.com/v3/repos/statistics/#get-contributors-list-with-additions-deletions-and-commit-counts
4. 星星数=repo 星星 * 贡献率
5. 移除 markdown 工程师。
  1. repo 语言是代码，即 https://api.github.com/repos/xx/xx/languages
  2. 且该语言的文件在所有文件中占比超过50%，即 https://github.com/Wox-launcher/Wox/search?l=C%23
6. ui 抄 http://ghrc.babits.top/





