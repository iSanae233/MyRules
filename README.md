# MyRules

[![Update rules](https://github.com/iSanae233/MyRules/actions/workflows/update-rules.yml/badge.svg)](https://github.com/iSanae233/MyRules/actions/workflows/update-rules.yml)

个人维护的 Loon 分流规则。规则文件统一放在 [`Rules/`](Rules/) 目录，按用途提供订阅。

## 规则列表

| 规则 | 说明 | GitHub Raw | jsDelivr |
| --- | --- | --- | --- |
| [AI](Rules/AI/AI.list) | 海外 AI 模型与相关服务 | [订阅](https://raw.githubusercontent.com/iSanae233/MyRules/main/Rules/AI/AI.list) | [订阅](https://cdn.jsdelivr.net/gh/iSanae233/MyRules@main/Rules/AI/AI.list) |
| [Claude](Rules/Claude/Claude.list) | Claude / Anthropic 域名和官方 API 入站 IP | [订阅](https://raw.githubusercontent.com/iSanae233/MyRules/main/Rules/Claude/Claude.list) | [订阅](https://cdn.jsdelivr.net/gh/iSanae233/MyRules@main/Rules/Claude/Claude.list) |
| [Apple](Rules/Apple/Apple.list) | Apple 域名、关键字、User-Agent 和 IP 规则 | [订阅](https://raw.githubusercontent.com/iSanae233/MyRules/main/Rules/Apple/Apple.list) | [订阅](https://cdn.jsdelivr.net/gh/iSanae233/MyRules@main/Rules/Apple/Apple.list) |

Claude 也包含在 AI 规则中。若希望 Claude 使用单独策略，请将 Claude 订阅放在 AI 订阅之前，并在 Loon 中为 Claude 选择 `SG` 策略。IP 规则使用 `no-resolve`，仅匹配目标已经是 IP 的连接；更高优先级的本地或插件规则也可能影响结果。

## 自动更新

- GitHub Actions 每天 **北京时间 04:00（Asia/Shanghai，UTC+8）**运行；对应 cron 为 `0 20 * * *`（UTC 前一天 20:00）。GitHub 调度可能延迟或漏跑，并非准点执行保证。
- 手动更新：打开 [Update rules](https://github.com/iSanae233/MyRules/actions/workflows/update-rules.yml) → **Run workflow** → 选择 `main`。
- 更新使用仓库自带的 `GITHUB_TOKEN`，只需要 `contents: write`；不需要添加个人令牌、API Key 或其他 Secrets。
- 只有生成结果或来源版本记录变化时才提交；不强制推送。`sources.lock.json` 和 `rules.lock.json` 记录上游版本，因此上游提交变化也可能更新来源记录。
- 公开仓库长时间没有活动时，GitHub 可能暂停定时工作流（[官方说明：60 天](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)）。若工作流被停用，需要在 Actions 中重新启用；失败详情也在 Actions 页面查看。

维护方法和目录规范见 [maintain.md](maintain.md)。

## 许可

本仓库脚本使用 MIT 许可。AI 域名数据沿用上游 MIT 许可，Apple 规则沿用上游 GPL-2.0 许可。来源与许可声明见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

首页的规则列表和订阅链接参考了 [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script/tree/master/rule/Loon/OpenAI) 的组织方式。
