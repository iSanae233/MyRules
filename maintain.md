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
| `scripts/sync_rules.py` | 同步其他服务分类，转换域名集并保留上游 IP、ASN、User-Agent 规则 |
| `rule_sources.json` | 分类、上游仓库与文件路径；新增服务时先修改此文件 |
| `Rules/` | 存放所有 `.list` 规则文件，每个分类包含同名 `.list` 和 `Readme.me` |
| `sources.lock.json` | 来源 URL、上游 commit、输入哈希、按服务分类的规则和跳过条目 |
| `rules.lock.json` | 其他分类的上游 commit、文件 URL、输入哈希和规则数量 |
| `.github/workflows/update-rules.yml` | 定时/手动获取并提交更新 |
| `examples/macOS.rules.conf` | 规则订阅迁移片段；不包含节点、凭据或完整网络配置 |

**添加 AI 服务商：** 在 `scripts/update_rules.py` 的 `PROVIDERS` 中增加显示名称和上游 `data/` 文件名，确认来源确实属于目标服务，再运行生成脚本、检查差异，最后提交。若需要新增 AI 服务 IP，必须先找到官方明确发布的客户端连接目标地址源，并校验解析结果；不能根据爬虫/出口 IP 推断。

**添加其他上游分类：** 修改 `rule_sources.json`，注明仓库、分支、许可和文件路径，然后运行 `scripts/sync_rules.py`。同一仓库的文件从同一个不可变 commit 下载。`_Domain.list` 文件中前导点域名转换为 `DOMAIN-SUFFIX`，无前导点域名转换为 `DOMAIN`。Apple、China 合并各自的域名版和补充版，不直接丢弃其中任何一份。Global 沿用现有配置的纯域名版。

**保留规则语义：** 服务分类保留上游 IP、ASN 的 `no-resolve` 选项及规则顺序，只去除完全相同的条目。不同分类可能使用不同策略，因此不跨分类去重。例如 YouTube 应在 Google 之前，AI 应在 Google / Microsoft 之前，服务细分规则应在 China / Global 之前。Adblock 的源文件固定 REJECT 字段被移除，订阅时仍需选择拒绝策略。

**添加其他规则：** 按 `Rules/<分类>/<分类>.list` 创建规则，在同目录的 `Readme.me` 中简要说明用途、更新方式，并提供 GitHub Raw / jsDelivr 链接；在首页规则列表中添加该分类的入口。自动生成的规则应通过对应脚本更新，不直接编辑生成结果。测试代码仅在本地使用，不纳入仓库。

**域名转换：** 普通域名和 `domain:` 转成 `DOMAIN-SUFFIX`，`full:` 转成 `DOMAIN`；递归展开 `include:` 并去重。`regexp:`、`keyword:` 以及带属性的条目（例如广告/遥测）不转换，原文及位置写入 `sources.lock.json` 的 `skipped`，便于人工评估漏分流；带过滤属性的 include 和未知语法直接报错。不会把正则简单扩大为整个共享 CDN 域名。

**更新保护：** 下载有超时、重试和大小限制。两个脚本分别在自身全部来源校验成功后写入结果；工作流只有在两者均成功时才提交。AI 脚本拒绝非法/宽泛域名、私网和过宽 CIDR、空结果、递归 include 和异常数据量；其他服务同步拒绝未知规则类型、意外策略字段、错误 IP/ASN 和空结果。任一分类超过 25% 的既有规则消失时会终止运行；即使总数不变，大批替换也会触发保护。运行失败不会发布，因此远程订阅保留上一版。

若删除确属上游正常调整，先人工检查来源及差异，再对对应脚本添加 `--accept-removals`，检查生成结果后提交。定时工作流不启用此绕过选项。

**策略检查：** 示例保留当前 Mac 的 China → HK，最终兜底仍由已有的 `FINAL,US` 决定。若本地还保留 `GEOIP,CN,DIRECT`，未命中域名规则的中国 IP 可能走 DIRECT；这与 China 域名走 HK 可以同时发生。若希望全部中国 IP 也走 HK，需要另外调整该本地规则，不应通过修改公开规则列表来隐式改变策略。

**外部广告源：** AdRules 的生成数据沿用各个上游的不同许可，暂不镜像或重新声明为 MIT；继续使用其原始订阅。Adblock 只同步原 Adblock4limbo 分类。不要把两者误认为同一个覆盖范围。

**隐私与发布：** 仓库只维护公开规则及无凭据的订阅片段，不提交本机完整 `.lcf`、远程节点订阅地址、证书、密钥或访问日志。校验代码保留在本地，不提交测试代码。

IP 规则带 `no-resolve`，遵循 [Loon IP 规则文档](https://nsloon.app/docs/Rule/ip_rule)：不为了匹配 IP 而额外解析域名。订阅语法参考 [Loon 订阅规则文档](https://nsloon.app/docs/Rule/sub_rule)。自动校验不等同于真实设备测试，Loon 上的实际可用性需要结合节点及请求日志验证。

## 目录约定

```text
Rules/
└── AI/
    ├── AI.list
    └── Readme.me
```

每个分类独立建目录，规则文件与分类同名，说明文件统一命名为 `Readme.me`。
