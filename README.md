# MyLoonRules

[![Update AI rules](https://github.com/iSanae233/MyLoonRules/actions/workflows/update-rules.yml/badge.svg)](https://github.com/iSanae233/MyLoonRules/actions/workflows/update-rules.yml)

个人维护的 Loon 分流规则。规则文件统一放在 [`Rules/`](Rules/) 目录，按用途提供订阅。

## 规则列表

| 规则 | 说明 | GitHub Raw | jsDelivr |
| --- | --- | --- | --- |
| [AI](Rules/AI/Readme.me) | 海外 AI 服务域名及适用的官方 IP 段，每天北京时间 04:00 检查更新 | [订阅](https://raw.githubusercontent.com/iSanae233/MyLoonRules/main/Rules/AI/AI.list) | [订阅](https://cdn.jsdelivr.net/gh/iSanae233/MyLoonRules@main/Rules/AI/AI.list) |

## 自动更新

- GitHub Actions 每天 **北京时间 04:00（Asia/Shanghai，UTC+8）**运行；对应 cron 为 `0 20 * * *`（UTC 前一天 20:00）。GitHub 调度可能延迟或漏跑，并非准点执行保证。
- 手动更新：打开 [Update AI rules](https://github.com/iSanae233/MyLoonRules/actions/workflows/update-rules.yml) → **Run workflow** → 选择 `main`。
- 更新使用仓库自带的 `GITHUB_TOKEN`，只需要 `contents: write`；不需要添加个人令牌、API Key 或其他 Secrets。
- 只有生成结果或来源版本记录变化时才提交；不强制推送。`sources.lock.json` 记录上游版本，因此上游提交变化也可能仅更新来源记录。
- 公开仓库长时间没有活动时，GitHub 可能暂停定时工作流（[官方说明：60 天](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)）。若工作流被停用，需要在 Actions 中重新启用；失败详情也在 Actions 页面查看。

维护方法和目录规范见 [maintain.md](maintain.md)。

## 许可

本仓库脚本使用 MIT 许可。域名数据沿用上游 MIT 许可，保留版权声明于 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。官方 IP 信息按所链接的服务商公开资料获取。

首页的规则列表和订阅链接参考了 [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script/tree/master/rule/Loon/OpenAI) 的组织方式。
