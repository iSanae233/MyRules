# 维护与校验

```sh
# Python 3.10+，只使用标准库，无需 pip install。
python3 scripts/update_rules.py
python3 scripts/sync_rules.py
git diff -- Rules/ sources.lock.json rules.lock.json
```

关键文件：

| 文件 | 用途 |
| --- | --- |
| `scripts/update_rules.py` | 数据源、格式转换、IP 筛选与更新保护；关键判断附注释 |
| `scripts/sync_rules.py` | 同步 Apple 规则，转换域名集并保留上游 IP、ASN、User-Agent 规则 |
| `rule_sources.json` | 分类、上游仓库与文件路径；新增服务时先修改此文件 |
| `Rules/` | 存放所有 `.list` 规则文件，每个分类包含同名 `.list` |
| `sources.lock.json` | 来源 URL、上游 commit、输入哈希、按服务分类的规则和跳过条目 |
| `rules.lock.json` | Apple 上游 commit、文件 URL、输入哈希和规则数量 |
| `.github/workflows/update-rules.yml` | 定时/手动获取并提交更新 |

**添加 AI 服务商：** 在 `scripts/update_rules.py` 的 `PROVIDERS` 中增加显示名称和上游 `data/` 文件名，确认来源确实属于目标服务，再运行生成脚本、检查差异，最后提交。若需要新增 AI 服务 IP，必须先找到官方明确发布的客户端连接目标地址源，并校验解析结果；不能根据爬虫/出口 IP 推断。Claude 独立列表从同一次生成的 Anthropic 域名和 Claude API 入站 IP 提取，AI 列表仍保留这些条目；需在 Loon 中将 Claude 订阅置于 AI 订阅之前并选择所需策略。

**添加其他上游分类：** 修改 `rule_sources.json`，注明仓库、分支、许可和文件路径，然后运行 `scripts/sync_rules.py`。同一仓库的文件从同一个不可变 commit 下载。`_Domain.list` 文件中前导点域名转换为 `DOMAIN-SUFFIX`，无前导点域名转换为 `DOMAIN`。Apple 合并域名版和补充版，不丢弃其中任何一份。

**保留规则语义：** 服务分类保留上游 IP、ASN 的 `no-resolve` 选项及规则顺序，只去除完全相同的条目。不同分类可能使用不同策略，因此不跨分类去重。不同订阅可能指定不同策略，请按实际需要安排 Loon 规则顺序。

**添加其他规则：** 按 `Rules/<分类>/<分类>.list` 创建规则，在首页规则列表中补充用途、更新方式以及 GitHub Raw / jsDelivr 链接。自动生成的规则应通过对应脚本更新，不直接编辑生成结果。测试代码仅在本地使用，不纳入仓库。

**域名转换：** 普通域名和 `domain:` 转成 `DOMAIN-SUFFIX`，`full:` 转成 `DOMAIN`；递归展开 `include:` 并去重。`regexp:`、`keyword:` 以及带属性的条目（例如广告/遥测）不转换，原文及位置写入 `sources.lock.json` 的 `skipped`，便于人工评估漏分流；带过滤属性的 include 和未知语法直接报错。不会把正则简单扩大为整个共享 CDN 域名。

**更新保护：** 下载有超时、重试和大小限制。两个脚本分别在自身全部来源校验成功后写入结果；工作流只有在两者均成功时才提交。AI 脚本拒绝非法/宽泛域名、私网和过宽 CIDR、空结果、递归 include 和异常数据量；其他服务同步拒绝未知规则类型、意外策略字段、错误 IP/ASN 和空结果。任一分类超过 25% 的既有规则消失时会终止运行；即使总数不变，大批替换也会触发保护。运行失败不会发布，因此远程订阅保留上一版。

若删除确属上游正常调整，先人工检查来源及差异，再对对应脚本添加 `--accept-removals`，检查生成结果后提交。定时工作流不启用此绕过选项。



**隐私与发布：** 仓库只维护公开规则及无凭据的订阅片段，不提交本机完整 `.lcf`、远程节点订阅地址、证书、密钥或访问日志。校验代码保留在本地，不提交测试代码。

IP 规则带 `no-resolve`，遵循 [Loon IP 规则文档](https://nsloon.app/docs/Rule/ip_rule)：不为了匹配 IP 而额外解析域名。订阅语法参考 [Loon 订阅规则文档](https://nsloon.app/docs/Rule/sub_rule)。自动校验不等同于真实设备测试，Loon 上的实际可用性需要结合节点及请求日志验证。

## 目录约定

```text
Rules/
├── AI/
    └── AI.list
├── Claude/
    └── Claude.list
└── Apple/
    └── Apple.list
```

每个分类独立建目录，规则文件与分类同名，说明和订阅链接统一维护在首页。
