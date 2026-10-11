---
title: "Git 常用命令与核心概念整理"
description: "整理 Git 常用命令、版本回退与分支操作，以及工作区、暂存区、版本库等核心概念的理解方式。"
pubDatetime: 2023-08-26T20:41:00+08:00
featured: false
draft: false
tags:
  - Git
  - 工具
  - 笔记
---

整理自己常用的 Git 命令和核心概念：工作区、暂存区、版本库的关系，提交与回退（reset、reflog）、分支与远程操作等，也记了一些容易记混的命令参数。偏速查性质，遇到记不清的命令可以直接翻。

这是一个用来学习 Git 的文档。

> [廖雪峰的 Git 教程](https://www.liaoxuefeng.com/wiki/896043488029600/897271968352576)

## Git 命令

- `git init`：创建一个 Git 仓库

- `git add <file name>`：向仓库中添加文件

- `git commit -m <xxx>`：把添加的文件提交到仓库

- `git status`：查看仓库的状态

- `git diff <file name>`：查看文件修改情况

- `git reset --hard <commit id>`：将版本设置、回退到某次提交时

  HEAD 表示当前的版本，HEAD^ 表示上一个版本，HEAD^^ 上上一个，HAED~100 代表前 100 个版本

- `git log`：查看所有提交日志，显示 commit id

  `git log --pretty=oneline`：以单行形式显示日志

- `git reflog`：显示版本变化的时间线

  可以显示每个版本的 commit id，方便`git reset`
  
- `git checkout -- <file name>`

  `git restore <file name>`：丢弃工作区的修改
  
- `git restore --staged <file name>`

  `git reset HEAD <file name>`：去除某文件在暂存区的内容

- `git rm <file name>`：用于删除文件，将删除操作放到暂存区

- `git branch`：查看现有的所有分支

  `git checkout -b <branch>`：创建新分支并切换到新分支上，等价于`git branch <branch>`,`git checkout <branch>`

  `git switch -c <branch>`：创建并切换分支。switch 是新版的切换命令，更易懂

- `git merge <branch>`：合并指定分支到当前分支上

  `git merge --no-ff -m <message> <branch>`：不使用 fast forward 的方式合并（在日志中能够显示分支变化），而fast forward 就看不出做过合并

- `git branch -d <branch>`：删除分支

- `git log --graph`：查看日志，以分支形式显示

- `git stash`：存储当前的工作区（以切换到别的分支来解决 bug，处理好再回来继续）

  `git stash list`：查看存储情况

  `git stash apply <stash id>`：恢复某一存储的工作状态

  `git stash drop <stash id>`：删除某一存储的工作状态

  `git stash pop <stash id>`：恢复并删除某一存储的状态

- `git cherry-pick <commit id>`：将某次提交修改应用到当前分支上（复制某次提交）

## Git 概念

- 工作区和版本库

  - 工作区，即与`.git`目录同级的那些文件，git 仓库建立的位置
  - 版本库，即`.git`目录

  

  - stage 暂存区：`git add`将文件添加到暂存区，通过`git commit`将暂存区内的文件提交到当前分支中

- [分支](https://www.liaoxuefeng.com/wiki/896043488029600/900003767775424)
- [分支冲突与解决](https://www.liaoxuefeng.com/wiki/896043488029600/900004111093344)
- fast forward

a dev change.

a dev modify.

bug fixed.

## Git command help

```
See 'git help <command>' to read about a specific subcommand

Main Porcelain Commands
   add                  Add file contents to the index
   am                   Apply a series of patches from a mailbox
   archive              Create an archive of files from a named tree
   bisect               Use binary search to find the commit that introduced a bug
   branch               List, create, or delete branches
   bundle               Move objects and refs by archive
   checkout             Switch branches or restore working tree files
   cherry-pick          Apply the changes introduced by some existing commits
   citool               Graphical alternative to git-commit
   clean                Remove untracked files from the working tree
   clone                Clone a repository into a new directory
   commit               Record changes to the repository
   describe             Give an object a human readable name based on an available ref
   diff                 Show changes between commits, commit and working tree, etc
   fetch                Download objects and refs from another repository
   format-patch         Prepare patches for e-mail submission
   gc                   Cleanup unnecessary files and optimize the local repository
   gitk                 The Git repository browser
   grep                 Print lines matching a pattern
   gui                  A portable graphical interface to Git
   init                 Create an empty Git repository or reinitialize an existing one
   log                  Show commit logs
   merge                Join two or more development histories together
   mv                   Move or rename a file, a directory, or a symlink
   notes                Add or inspect object notes
   pull                 Fetch from and integrate with another repository or a local branch
   push                 Update remote refs along with associated objects
   range-diff           Compare two commit ranges (e.g. two versions of a branch)
   rebase               Reapply commits on top of another base tip
   reset                Reset current HEAD to the specified state
   restore              Restore working tree files
   revert               Revert some existing commits
   rm                   Remove files from the working tree and from the index
   shortlog             Summarize 'git log' output
   show                 Show various types of objects
   sparse-checkout      Initialize and modify the sparse-checkout
   stash                Stash the changes in a dirty working directory away
   status               Show the working tree status
   submodule            Initialize, update or inspect submodules
   switch               Switch branches
   tag                  Create, list, delete or verify a tag object signed with GPG
   worktree             Manage multiple working trees

Ancillary Commands / Manipulators
   config               Get and set repository or global options
   fast-export          Git data exporter
   fast-import          Backend for fast Git data importers
   filter-branch        Rewrite branches
   mergetool            Run merge conflict resolution tools to resolve merge conflicts
   pack-refs            Pack heads and tags for efficient repository access
   prune                Prune all unreachable objects from the object database
   reflog               Manage reflog information
   remote               Manage set of tracked repositories
   repack               Pack unpacked objects in a repository
   replace              Create, list, delete refs to replace objects

Ancillary Commands / Interrogators
   annotate             Annotate file lines with commit information
   blame                Show what revision and author last modified each line of a file
   bugreport            Collect information for user to file a bug report
   count-objects        Count unpacked number of objects and their disk consumption
   difftool             Show changes using common diff tools
   fsck                 Verifies the connectivity and validity of the objects in the database
   gitweb               Git web interface (web frontend to Git repositories)
   help                 Display help information about Git
   instaweb             Instantly browse your working repository in gitweb
   merge-tree           Show three-way merge without touching index
   rerere               Reuse recorded resolution of conflicted merges
   show-branch          Show branches and their commits
   verify-commit        Check the GPG signature of commits
   verify-tag           Check the GPG signature of tags
   whatchanged          Show logs with difference each commit introduces

Interacting with Others
   archimport           Import a GNU Arch repository into Git
   cvsexportcommit      Export a single commit to a CVS checkout
   cvsimport            Salvage your data out of another SCM people love to hate
   cvsserver            A CVS server emulator for Git
   imap-send            Send a collection of patches from stdin to an IMAP folder
   p4                   Import from and submit to Perforce repositories
   quiltimport          Applies a quilt patchset onto the current branch
   request-pull         Generates a summary of pending changes
   send-email           Send a collection of patches as emails
   svn                  Bidirectional operation between a Subversion repository and Git

Low-level Commands / Manipulators
   apply                Apply a patch to files and/or to the index
   checkout-index       Copy files from the index to the working tree
   commit-graph         Write and verify Git commit-graph files
   commit-tree          Create a new commit object
   hash-object          Compute object ID and optionally creates a blob from a file
   index-pack           Build pack index file for an existing packed archive
   merge-file           Run a three-way file merge
   merge-index          Run a merge for files needing merging
   mktag                Creates a tag object
   mktree               Build a tree-object from ls-tree formatted text
   multi-pack-index     Write and verify multi-pack-indexes
   pack-objects         Create a packed archive of objects
   prune-packed         Remove extra objects that are already in pack files
   read-tree            Reads tree information into the index
   symbolic-ref         Read, modify and delete symbolic refs
   unpack-objects       Unpack objects from a packed archive
   update-index         Register file contents in the working tree to the index
   update-ref           Update the object name stored in a ref safely
   write-tree           Create a tree object from the current index

Low-level Commands / Interrogators
   cat-file             Provide content or type and size information for repository objects
   cherry               Find commits yet to be applied to upstream
   diff-files           Compares files in the working tree and the index
   diff-index           Compare a tree to the working tree or index
   diff-tree            Compares the content and mode of blobs found via two tree objects
   for-each-ref         Output information on each ref
   get-tar-commit-id    Extract commit ID from an archive created using git-archive
   ls-files             Show information about files in the index and the working tree
   ls-remote            List references in a remote repository
   ls-tree              List the contents of a tree object
   merge-base           Find as good common ancestors as possible for a merge
   name-rev             Find symbolic names for given revs
   pack-redundant       Find redundant pack files
   rev-list             Lists commit objects in reverse chronological order
   rev-parse            Pick out and massage parameters
   show-index           Show packed archive index
   show-ref             List references in a local repository
   unpack-file          Creates a temporary file with a blob's contents
   var                  Show a Git logical variable
   verify-pack          Validate packed Git archive files

Low-level Commands / Syncing Repositories
   daemon               A really simple server for Git repositories
   fetch-pack           Receive missing objects from another repository
   http-backend         Server side implementation of Git over HTTP
   send-pack            Push objects over Git protocol to another repository
   update-server-info   Update auxiliary info file to help dumb servers

Low-level Commands / Internal Helpers
   check-attr           Display gitattributes information
   check-ignore         Debug gitignore / exclude files
   check-mailmap        Show canonical names and email addresses of contacts
   check-ref-format     Ensures that a reference name is well formed
   column               Display data in columns
   credential           Retrieve and store user credentials
   credential-store     Helper to store credentials on disk
   fmt-merge-msg        Produce a merge commit message
   interpret-trailers   Add or parse structured information in commit messages
   mailinfo             Extracts patch and authorship from a single e-mail message
   mailsplit            Simple UNIX mbox splitter program
   merge-one-file       The standard helper program to use with git-merge-index
   patch-id             Compute unique ID for a patch
   sh-i18n              Git's i18n setup code for shell scripts
   sh-setup             Common Git shell script setup code
   stripspace           Remove unnecessary whitespace

External commands
   askyesno
   credential-helper-selector
   flow
   lfs
```
