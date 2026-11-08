# MyRules

[![Update rules](https://github.com/iSanae233/MyRules/actions/workflows/update-rules.yml/badge.svg)](https://github.com/iSanae233/MyRules/actions/workflows/update-rules.yml)

个人维护的 Loon 分流规则。规则文件统一放在 [`Rules/`](Rules/) 目录，按用途提供订阅。

## 规则列表

| 规则 | 说明 | GitHub Raw | jsDelivr |
| --- | --- | --- | --- |
| [Adblock](Rules/Adblock/Readme.me) | 网页广告补充规则，继承原 Adblock4limbo 的覆盖范围 | [订阅](https://raw.githubusercontent.com/iSanae233/MyRules/main/Rules/Adblock/Adblock.list) | [订阅](https://cdn.jsdelivr.net/gh/iSanae233/MyRules@main/Rules/Adblock/Adblock.list) |
| [AI](Rules/AI/Readme.me) | 海外 AI 模型与相关服务 | [订阅](https://raw.githubusercontent.com/iSanae233/MyRules/main/Rules/AI/AI.list) | [订阅](https://cdn.jsdelivr.net/gh/iSanae233/MyRules@main/Rules/AI/AI.list) |
| [Apple](Rules/Apple/Readme.me) | Apple 域名、关键字、User-Agent 和 IP 规则 | [订阅](https://raw.githubusercontent.com/iSanae233/MyRules/main/Rules/Apple/Apple.list) | [订阅](https://cdn.jsdelivr.net/gh/iSanae233/MyRules@main/Rules/Apple/Apple.list) |
| [Bilibili](Rules/Bilibili/Readme.me) | 哔哩哔哩相关服务 | [订阅](https://raw.githubusercontent.com/iSanae233/MyRules/main/Rules/Bilibili/Bilibili.list) | [订阅](https://cdn.jsdelivr.net/gh/iSanae233/MyRules@main/Rules/Bilibili/Bilibili.list) |
| [Crypto](Rules/Crypto/Readme.me) | 加密资产交易平台及相关服务 | [订阅](https://raw.githubusercontent.com/iSanae233/MyRules/main/Rules/Crypto/Crypto.list) | [订阅](https://cdn.jsdelivr.net/gh/iSanae233/MyRules@main/Rules/Crypto/Crypto.list) |
| [YouTube](Rules/YouTube/Readme.me) | YouTube 及相关媒体服务 | [订阅](https://raw.githubusercontent.com/iSanae233/MyRules/main/Rules/YouTube/YouTube.list) | [订阅](https://cdn.jsdelivr.net/gh/iSanae233/MyRules@main/Rules/YouTube/YouTube.list) |
| [Google](Rules/Google/Readme.me) | Google 相关服务 | [订阅](https://raw.githubusercontent.com/iSanae233/MyRules/main/Rules/Google/Google.list) | [订阅](https://cdn.jsdelivr.net/gh/iSanae233/MyRules@main/Rules/Google/Google.list) |
| [Microsoft](Rules/Microsoft/Readme.me) | Microsoft 相关服务 | [订阅](https://raw.githubusercontent.com/iSanae233/MyRules/main/Rules/Microsoft/Microsoft.list) | [订阅](https://cdn.jsdelivr.net/gh/iSanae233/MyRules@main/Rules/Microsoft/Microsoft.list) |
| [Proton](Rules/Proton/Readme.me) | Proton Mail 相关服务 | [订阅](https://raw.githubusercontent.com/iSanae233/MyRules/main/Rules/Proton/Proton.list) | [订阅](https://cdn.jsdelivr.net/gh/iSanae233/MyRules@main/Rules/Proton/Proton.list) |
| [Twitter](Rules/Twitter/Readme.me) | Twitter / X 相关服务 | [订阅](https://raw.githubusercontent.com/iSanae233/MyRules/main/Rules/Twitter/Twitter.list) | [订阅](https://cdn.jsdelivr.net/gh/iSanae233/MyRules@main/Rules/Twitter/Twitter.list) |
| [Telegram](Rules/Telegram/Readme.me) | Telegram 及上游列出的相关客户端 | [订阅](https://raw.githubusercontent.com/iSanae233/MyRules/main/Rules/Telegram/Telegram.list) | [订阅](https://cdn.jsdelivr.net/gh/iSanae233/MyRules@main/Rules/Telegram/Telegram.list) |
| [China](Rules/China/Readme.me) | 中国大陆服务域名及上游补充规则 | [订阅](https://raw.githubusercontent.com/iSanae233/MyRules/main/Rules/China/China.list) | [订阅](https://cdn.jsdelivr.net/gh/iSanae233/MyRules@main/Rules/China/China.list) |
| [Global](Rules/Global/Readme.me) | 上游 Global 域名规则，不扩展到其 IP 规则 | [订阅](https://raw.githubusercontent.com/iSanae233/MyRules/main/Rules/Global/Global.list) | [订阅](https://cdn.jsdelivr.net/gh/iSanae233/MyRules@main/Rules/Global/Global.list) |

## 自动更新

- GitHub Actions 每天 **北京时间 04:00（Asia/Shanghai，UTC+8）**运行；对应 cron 为 `0 20 * * *`（UTC 前一天 20:00）。GitHub 调度可能延迟或漏跑，并非准点执行保证。
- 手动更新：打开 [Update rules](https://github.com/iSanae233/MyRules/actions/workflows/update-rules.yml) → **Run workflow** → 选择 `main`。
- 更新使用仓库自带的 `GITHUB_TOKEN`，只需要 `contents: write`；不需要添加个人令牌、API Key 或其他 Secrets。
- 只有生成结果或来源版本记录变化时才提交；不强制推送。`sources.lock.json` 和 `rules.lock.json` 记录上游版本，因此上游提交变化也可能更新来源记录。
- 公开仓库长时间没有活动时，GitHub 可能暂停定时工作流（[官方说明：60 天](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)）。若工作流被停用，需要在 Actions 中重新启用；失败详情也在 Actions 页面查看。

维护方法和目录规范见 [maintain.md](maintain.md)，订阅迁移片段见 [examples/macOS.rules.conf](examples/macOS.rules.conf)。

AdRules 暂保留[原始订阅](https://adrules.top/adrules.list)：其生成数据涉及多种上游许可，本仓库不镜像该聚合文件。

## 许可

本仓库脚本使用 MIT 许可。AI 域名数据、Adblock 规则分别保留上游 MIT 许可，其他同步的服务规则沿用上游 GPL-2.0 许可。来源与许可声明见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

首页的规则列表和订阅链接参考了 [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script/tree/master/rule/Loon/OpenAI) 的组织方式。
