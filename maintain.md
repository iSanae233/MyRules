# 维护与校验

```sh
# Python 3.10+，只使用标准库，无需 pip install。
python3 scripts/update_rules.py
git diff -- Rules/AI/AI.list sources.lock.json
```

关键文件：

| 文件 | 用途 |
| --- | --- |
| `scripts/update_rules.py` | 数据源、格式转换、IP 筛选与更新保护；关键判断附注释 |
| `Rules/` | 存放所有 `.list` 规则文件，每个分类包含同名 `.list` 和 `Readme.me` |
| `sources.lock.json` | 来源 URL、上游 commit、输入哈希、按服务分类的规则和跳过条目 |
| `.github/workflows/update-rules.yml` | 定时/手动获取并提交更新 |

**添加服务商：** 在脚本的 `PROVIDERS` 中增加显示名称和上游 `data/` 文件名，确认来源确实属于目标服务，再运行生成脚本、检查差异，最后提交。若需要新增 IP，必须先找到官方明确发布的客户端连接目标地址源，并校验解析结果；不能根据爬虫/出口 IP 推断。

**添加其他规则：** 按 `Rules/<分类>/<分类>.list` 创建规则，在同目录的 `Readme.me` 中简要说明用途、更新方式，并提供 GitHub Raw / jsDelivr 链接；在首页规则列表中添加该分类的入口。自动生成的规则应通过对应脚本更新，不直接编辑生成结果。测试代码仅在本地使用，不纳入仓库。

**域名转换：** 普通域名和 `domain:` 转成 `DOMAIN-SUFFIX`，`full:` 转成 `DOMAIN`；递归展开 `include:` 并去重。`regexp:`、`keyword:` 以及带属性的条目（例如广告/遥测）不转换，原文及位置写入 `sources.lock.json` 的 `skipped`，便于人工评估漏分流；带过滤属性的 include 和未知语法直接报错。不会把正则简单扩大为整个共享 CDN 域名。

**更新保护：** 所有来源必须成功下载并通过校验后才替换本地输出；下载有超时、重试和大小限制。拒绝非法/宽泛域名、私网和过宽 CIDR、空结果、递归 include 和异常数据量。任一服务分类超过 25% 的既有规则消失时会终止运行；即使总数不变，大批替换也会触发保护。运行失败不会提交，因此远程订阅保留上一版。

若删除确属上游正常调整，先人工检查来源及差异，再在本地执行 `python3 scripts/update_rules.py --accept-removals`，检查生成结果后提交。定时工作流不启用此绕过选项。

IP 规则带 `no-resolve`，遵循 [Loon IP 规则文档](https://nsloon.app/docs/Rule/ip_rule)：不为了匹配 IP 而额外解析域名。订阅语法参考 [Loon 订阅规则文档](https://nsloon.app/docs/Rule/sub_rule)。自动校验不等同于真实设备测试，Loon 上的实际可用性需要结合节点及请求日志验证。

## 目录约定

```text
Rules/
└── AI/
    ├── AI.list
    └── Readme.me
```

每个分类独立建目录，规则文件与分类同名，说明文件统一命名为 `Readme.me`。
