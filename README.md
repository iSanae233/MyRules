# MyLoonRules

[![Update AI rules](https://github.com/iSanae233/MyLoonRules/actions/workflows/update-rules.yml/badge.svg)](https://github.com/iSanae233/MyLoonRules/actions/workflows/update-rules.yml)

个人维护的 Loon 分流规则。规则文件统一放在 [`Rules/`](Rules/) 目录，按用途提供订阅。

## 规则列表

| 规则 | 说明 | GitHub Raw | jsDelivr |
| --- | --- | --- | --- |
| [AI_Models.list](Rules/AI_Models.list) | 海外 AI 服务域名及适用的官方 IP 段，每天北京时间 04:00 检查更新 | [订阅](https://raw.githubusercontent.com/iSanae233/MyLoonRules/main/Rules/AI_Models.list) | [订阅](https://cdn.jsdelivr.net/gh/iSanae233/MyLoonRules@main/Rules/AI_Models.list) |

## 在 Loon 中使用

**GitHub Raw：**

```text
https://raw.githubusercontent.com/iSanae233/MyLoonRules/main/Rules/AI_Models.list
```

**jsDelivr CDN：**

```text
https://cdn.jsdelivr.net/gh/iSanae233/MyLoonRules@main/Rules/AI_Models.list
```

两个地址选择一个即可，无需重复添加。jsDelivr 存在 CDN 缓存，内容可能晚于 GitHub Raw 更新。

在 Loon 的「配置 → 订阅规则」中添加所选地址，选择你已有的 AI 代理策略组，并设置客户端自动更新。GitHub 更新文件后，Loon 仍需刷新订阅才会取得新版本。

也可以在配置文件的 `[Remote Rule]` 部分添加以下一行，把 `AI` 换成你实际存在的策略或策略组名称：

```ini
[Remote Rule]
https://raw.githubusercontent.com/iSanae233/MyLoonRules/main/Rules/AI_Models.list, policy=AI, tag=AI_Models, enabled=true
```

将此订阅放在可能抢先匹配的 Google、Microsoft 等宽泛规则之前。规则只决定流量使用哪个策略，节点仍需支持目标服务及 UDP（如使用语音）。无需安装证书或配置 MitM。

## AI_Models 覆盖范围与来源

| 服务 | 域名数据类别 | 自动获取的官方 IP |
| --- | --- | --- |
| ChatGPT / OpenAI（含数据源中列出的 Sora 域名） | `openai` | ChatGPT Voice 的 IPv4 / IPv6 前缀（如官方发布） |
| Gemini / Google AI（含 AI Studio、NotebookLM 等） | `google-gemini`，递归读取其 include | 无；使用域名分流 |
| Claude / Anthropic | `anthropic` | Claude API 的 **inbound** IPv4 / IPv6 段 |
| Grok / xAI | `xai` | 无；使用域名分流 |
| Perplexity | `perplexity` | 无；使用域名分流 |
| Groq | `groq` | 无；使用域名分流 |
| GitHub Copilot | `github-copilot` | 无；使用域名分流 |

域名每天同步自 [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community)，它是社区维护的数据，并非服务商完整的官方域名清单。每次运行先获取上游 commit SHA，再从同一个不可变版本下载所有类别及 include，避免混合不同版本。

官方 IP 来源：

- [OpenAI ChatGPT Voice JSON](https://openai.com/chatgpt-voice.json)：[OpenAI 网络说明](https://help.openai.com/en/articles/9247338-network-recommendations-for-chatgpt-errors-on-web-and-apps)将其定义为语音服务端地址，不代表 OpenAI 全部产品的 IP。
- [Anthropic IP 文档](https://platform.claude.com/docs/en/api/ip-addresses)：只读取 **Inbound IP addresses**（入站，即客户端连接服务端）至 **Outbound IP addresses** 之间的前缀，供访问 Claude API 使用。文档页面结构改变时更新会失败，需要维护者检查解析器。

**不将共享云平台整个 IP 段、DNS 临时解析结果、AI 爬虫来源 IP、MCP 出口 IP 或已退役地址当成服务目标 IP。** Gemini 等服务使用共享基础设施，当前不为它们补入整个 Google/AWS/Cloudflare 网段。此列表也不保证覆盖登录、付款、所有第三方附件或新上线功能；遇到漏分流请提供实际请求域名后补充数据源。

## 自动更新

- GitHub Actions 每天 **北京时间 04:00（Asia/Shanghai，UTC+8）**运行；对应 cron 为 `0 20 * * *`（UTC 前一天 20:00）。GitHub 调度可能延迟或漏跑，并非准点执行保证。
- 手动更新：打开 [Update AI rules](https://github.com/iSanae233/MyLoonRules/actions/workflows/update-rules.yml) → **Run workflow** → 选择 `main`。
- 更新使用仓库自带的 `GITHUB_TOKEN`，只需要 `contents: write`；不需要添加个人令牌、API Key 或其他 Secrets。
- 只有生成结果或来源版本记录变化时才提交；不强制推送。`sources.lock.json` 记录上游版本，因此上游提交变化也可能仅更新来源记录。
- 公开仓库长时间没有活动时，GitHub 可能暂停定时工作流（[官方说明：60 天](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)）。若工作流被停用，需要在 Actions 中重新启用；失败详情也在 Actions 页面查看。

## 维护与校验

```sh
# Python 3.10+，只使用标准库，无需 pip install。
python3 scripts/update_rules.py
git diff -- Rules/AI_Models.list sources.lock.json
```

关键文件：

| 文件 | 用途 |
| --- | --- |
| `scripts/update_rules.py` | 数据源、格式转换、IP 筛选与更新保护；关键判断附注释 |
| `Rules/` | 存放所有 `.list` 规则文件，目前提供 `AI_Models.list` |
| `sources.lock.json` | 来源 URL、上游 commit、输入哈希、按服务分类的规则和跳过条目 |
| `.github/workflows/update-rules.yml` | 定时/手动获取并提交更新 |

**添加服务商：** 在脚本的 `PROVIDERS` 中增加显示名称和上游 `data/` 文件名，确认来源确实属于目标服务，再运行生成脚本、检查差异，最后提交。若需要新增 IP，必须先找到官方明确发布的客户端连接目标地址源，并校验解析结果；不能根据爬虫/出口 IP 推断。

**添加其他规则：** 将文件放入 `Rules/`，在首页规则列表中补充用途、更新方式及 GitHub Raw / jsDelivr 链接。自动生成的规则应通过对应脚本更新，不直接编辑生成结果。测试代码仅在本地使用，不纳入仓库。

**域名转换：** 普通域名和 `domain:` 转成 `DOMAIN-SUFFIX`，`full:` 转成 `DOMAIN`；递归展开 `include:` 并去重。`regexp:`、`keyword:` 以及带属性的条目（例如广告/遥测）不转换，原文及位置写入 `sources.lock.json` 的 `skipped`，便于人工评估漏分流；带过滤属性的 include 和未知语法直接报错。不会把正则简单扩大为整个共享 CDN 域名。

**更新保护：** 所有来源必须成功下载并通过校验后才替换本地输出；下载有超时、重试和大小限制。拒绝非法/宽泛域名、私网和过宽 CIDR、空结果、递归 include 和异常数据量。任一服务分类超过 25% 的既有规则消失时会终止运行；即使总数不变，大批替换也会触发保护。运行失败不会提交，因此远程订阅保留上一版。

若删除确属上游正常调整，先人工检查来源及差异，再在本地执行 `python3 scripts/update_rules.py --accept-removals`，检查生成结果后提交。定时工作流不启用此绕过选项。

IP 规则带 `no-resolve`，遵循 [Loon IP 规则文档](https://nsloon.app/docs/Rule/ip_rule)：不为了匹配 IP 而额外解析域名。订阅语法参考 [Loon 订阅规则文档](https://nsloon.app/docs/Rule/sub_rule)。自动校验不等同于真实设备测试，Loon 上的实际可用性需要结合节点及请求日志验证。

## 许可

本仓库脚本使用 MIT 许可。域名数据沿用上游 MIT 许可，保留版权声明于 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。官方 IP 信息按所链接的服务商公开资料获取。

首页的规则列表、订阅链接和来源说明参考了 [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script/tree/master/rule/Loon/OpenAI) 的组织方式。
