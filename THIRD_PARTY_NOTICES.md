# Third-party notices

## Service rules derived from blackmatrix7

The Apple, Bilibili, Crypto, YouTube, Google, Microsoft, Proton, Twitter,
Telegram, China and Global lists are derived from
[blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script),
authored by blackmatrix7 and contributors, under the GNU GPL version 2.
These lists retain that license, separately from this repository's MIT scripts.
The full upstream license is included in [LICENSES/blackmatrix7-GPL-2.0.txt](LICENSES/blackmatrix7-GPL-2.0.txt).
`rules.lock.json` records immutable source URLs, revisions and hashes.
Changes made by MyRules: convert dot-prefixed domain sets to DOMAIN-SUFFIX,
keep exact domains as DOMAIN, merge companion lists and remove exact duplicates.
The generator and its source configuration are included in this repository.

## Adblock rules derived from limbopro

`Rules/Adblock/Adblock.list` is derived from
[limbopro/Adblock4limbo](https://github.com/limbopro/Adblock4limbo),
Copyright (c) 2022 毒奶博主, under the MIT License.
The full license is included in [LICENSES/limbopro-MIT.txt](LICENSES/limbopro-MIT.txt).
Changes: remove exact duplicates and source REJECT policy fields, so Loon's
subscription policy selects the action. Source URLs and hashes are recorded
in `rules.lock.json`. This list does not incorporate the separate AdRules feed.

AdRules remains an external subscription. Its generated artifacts use their
respective upstream licenses and are not redistributed or relicensed here.
See [AdRules licensing and sources](https://github.com/Cats-Team/AdRules#license).

## AI domain data

Domain rules are derived from [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community).
The exact source revision, file URLs, and hashes used by each generation are recorded in `sources.lock.json`.

The upstream domain data is distributed under the following license:

```text
MIT License

Copyright (c) 2018-2019 V2Ray

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Service IP facts are obtained from OpenAI's ChatGPT Voice JSON and Anthropic's
published inbound API IP documentation. They are not copied from crawler IP feeds.
