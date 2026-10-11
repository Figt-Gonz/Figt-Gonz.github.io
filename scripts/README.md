# 知识库 → 博客 迁移脚本

把 Obsidian 知识库里的笔记（`40.知识沉淀/`）转成 AstroPaper 文章，落到 `src/content/posts/`。

## 用法

```bash
# 先干跑：只写 .staging-migration/，不碰 posts/
python3 scripts/migrate-vault-notes.py --dry-run

# 真正落库
python3 scripts/migrate-vault-notes.py --apply

# 只处理指定 slug
python3 scripts/migrate-vault-notes.py --apply --only git-notes https-tls-handshake

# 清单里还没定 pubDatetime 时，用占位日期验证管道
python3 scripts/migrate-vault-notes.py --dry-run --pubdate-fallback "2099-01-01T10:00:00+08:00"
```

脚本幂等：重跑覆盖同 slug 产物；图片下载有 `/tmp/vault-migration-imgcache` 缓存，不重复抓取。

## 清单 `migration-manifest.json`

- `vault_root`：知识库根目录（默认 `40.知识沉淀`）
- `asset_pools`：本地图片资产池。笔记里的图片常写成 `D:\...` 或 `..\..\img\x.png`，脚本会按文件名在资产池里找回（Obsidian 迁移后文件名带哈希前缀，如 `0de6f6ea32d1-image-2024...png`）
- `entries[]`：
  - `slug`：文章文件名（kebab-case，必须与现有文章不重复）
  - `src`：相对 `vault_root` 的笔记路径
  - `title` / `description` / `tags` / `pubDatetime`：写入 frontmatter
  - `intro`：迁移时补写的开篇引言，插在正文最前面；正文本身不改
  - `drop_sections`：要删掉的个人向小节标题（如 `["TODO"]`），从该标题删到下一个同级标题
  - `enabled`：`false` 表示这次不迁

未填 `pubDatetime` 且没给 `--pubdate-fallback` 的条目会被跳过，不会半途写坏。

## 转换规则

1. 去掉 Obsidian frontmatter（`source_repo` / `type` 等）
2. 正文开头的 H1 与 title 重复 → 删掉（标题由主题渲染）
3. 图片：http(s) 下载进 `posts/<slug>/images/`，路径改写成 `./<slug>/images/xxx.png`；本地路径先按相对路径找、再按文件名在 `asset_pools` 里找
4. 找不到的图片：删除该图片并写进报告，**不静默吞掉**
5. `[[wikilink]]` → 纯文本
6. 3 行以上连续空行压成一个空行

## 注意事项

- `dist/` 被 git 跟踪（历史遗留）。本地构建后如果不想提交产物：`git checkout -- dist && git clean -fd dist`
- 发布前跑一遍敏感信息扫描（公司/内部/客户等），笔记里不要带内部信息
- 报告文件：`--apply` 写 `tmp/migration-report.json`，`--dry-run` 写 `.staging-migration/migration-report.json`
