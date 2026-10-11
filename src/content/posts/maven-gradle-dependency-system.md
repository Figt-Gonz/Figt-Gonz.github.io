---
title: "Maven 与 Gradle 依赖体系梳理"
description: "从 Maven 仓库结构、产物清单、发布链路到 Gradle classpath 与 POM scope 的映射关系，理清 Android 依赖管理背后的机制与常见坑。"
pubDatetime: 2026-07-08T21:41:00+08:00
featured: false
draft: false
tags:
  - Gradle
  - Maven
  - Android
  - 依赖管理
---

Android 工程里依赖问题往往最难排查：没改代码却编译不过、打包时多出无关库、SDK 发布后集成方拿不到传递依赖。这篇笔记把 Maven 仓库结构、产物清单、发布链路，与 Gradle 的 api/implementation 声明、两种 classpath、POM scope 之间的对应关系串起来讲清楚，最后列出常见坑与排查方向。整理自一次关于依赖体系的讨论，属于通用 Android/Gradle 工程知识。

> 整理自一次关于 Maven 仓库体系、库发布与消费、Gradle classpath 与 POM scope 关系的对话。
> 内容为通用 Android/Gradle 工程知识，不涉及公司内部信息。

## 0. 先记住三条主线

- **仓库体系**：Maven 仓库就是一个按固定目录结构存放依赖产物的文件服务器，坐标是每个库的唯一地址。
- **发布链路**：库本体（aar/jar）+ 依赖描述（pom/module）+ 元数据与校验文件，缺一不可。
- **依赖语义**：Gradle 的 `api/implementation/compileOnly/runtimeOnly` 是**你怎么声明**；`compileClasspath/runtimeClasspath` 是 Gradle 据此**算出来的实际集合**；POM 的 `compile/runtime/provided` 是发布后**告诉消费方怎么传递**。

---

## 一、Maven 仓库体系

Maven 仓库本质上是**按固定目录结构存放依赖产物的文件服务器**。Gradle 根据坐标去配置的仓库查找产物，下载到本地，再参与编译、打包、运行。

### 1. 本地仓库

```text
~/.m2/repository
```

- Linux/macOS：`/Users/用户名/.m2/repository`、`/home/用户名/.m2/repository`
- Windows：`C:\Users\用户名\.m2\repository`

执行 `./gradlew publishToMavenLocal` 后，产物会进入本地 Maven 仓库，通过 `mavenLocal()` 消费。主要用于本地调试 SDK、验证发布配置、多项目联调。

### 2. 远程公共仓库

- `google()`：Android 官方相关依赖（AGP、AndroidX、Material Components、Google Play Services、Firebase）。
- `mavenCentral()`：Java/Kotlin/Android 世界最主流的中央仓库（OkHttp、Retrofit、Gson 等）。

### 3. 私有仓库

Nexus、Artifactory、GitLab Package Registry、GitHub Packages、阿里云 Maven 私服、公司内部制品库。用于发布内部 SDK/业务组件/插件/基础库，以及依赖缓存、安全审计。

```groovy
repositories {
    maven {
        url = uri("https://maven.xxx.com/repository/android-release/")
        credentials {
            username = "xxx"
            password = "xxx"
        }
    }
}
```

### 4. Release 仓库与 Snapshot 仓库

- **Release**（`1.0.0`、`1.2.3`）：稳定版本，同一版本号不应反复覆盖，适合生产环境。
- **Snapshot**（`1.0.0-SNAPSHOT`）：开发中版本，可反复覆盖，适合联调、测试、灰度。

Snapshot 仓库内部实际会生成带时间戳的构建版本，例如：

```text
mylib-1.0.0-20260708.093012-1.aar
mylib-1.0.0-20260708.101522-2.aar
```

---

## 二、坐标与仓库目录结构

依赖坐标由三部分组成：

```text
groupId:artifactId:version
```

例如 `com.squareup.okhttp3:okhttp:4.12.0` 拆开为 `com.squareup.okhttp3` / `okhttp` / `4.12.0`。

- **groupId**：组织、公司、团队、命名空间。和代码里的 package 不是一回事，可以相同也可以不同。
- **artifactId**：具体库名（`okhttp`、`core-ktx`、公司内部的 `network-sdk`、`trade-core` 等）。
- **version**：语义大致为 `major.minor.patch` —— patch 修 bug、minor 新增兼容能力、major 破坏性升级。

仓库中的路径 = groupId 的点换成斜杠 + artifactId + version：

```text
com/example/sdk/user-center/1.0.0/
├── user-center-1.0.0.aar
├── user-center-1.0.0.pom
├── user-center-1.0.0.module
├── user-center-1.0.0-sources.jar
├── user-center-1.0.0-javadoc.jar
├── user-center-1.0.0.aar.md5 / .sha1 / .sha256
└──（上一级）maven-metadata.xml
```

---

## 三、Maven 产物清单

| 产物 | 作用 |
| --- | --- |
| `.jar` | 普通 Java/Kotlin 库。含 `.class`、`META-INF`、资源文件 |
| `.aar` | Android Library 专用，比 jar 丰富：`classes.jar`、`AndroidManifest.xml`、`res/`、`assets/`、`jni/`、`R.txt`、`proguard.txt`、`consumer-rules.pro`、`public.txt`、`lint.jar` |
| `.pom` | **依赖说明书**：坐标、依赖、scope。决定集成方能否自动拿到传递依赖 |
| `.module` | Gradle Module Metadata，表达能力比 POM 强：变体 variant、debug/release、apiElements/runtimeElements、依赖约束、attributes。Gradle 消费时优先使用它 |
| `sources.jar` | 源码包，让 IDE 能看源码、能跳调试 |
| `javadoc.jar` | 文档包，发布到 Maven Central 通常要求提供 |
| `.md5/.sha1/.sha256` | 校验文件，防下载损坏或篡改 |

**只要库里有 Android 资源、Manifest、自定义 View、consumer 混淆规则、native so，就应该发 `aar` 而不是 `jar`。**

只上传 aar、不上传 pom 的后果：集成方拿不到传递依赖 → 需要手动补依赖 → 容易 `ClassNotFoundException`。正确做法是完整发布 `aar + pom + module metadata`。

---

## 四、发布一个库（Gradle maven-publish）

```groovy
plugins {
    id 'com.android.library'
    id 'org.jetbrains.kotlin.android'
    id 'maven-publish'
}

android {
    namespace 'com.example.user'
    compileSdk 35
    defaultConfig {
        minSdk 23
        consumerProguardFiles 'consumer-rules.pro'
    }
}

dependencies {
    // 对外 API 暴露的依赖用 api；纯内部实现用 implementation
    implementation "com.squareup.okhttp3:okhttp:4.12.0"
}

afterEvaluate {
    publishing {
        publications {
            release(MavenPublication) {
                from components.release
                groupId = 'com.example.sdk'
                artifactId = 'user-center'
                version = '1.0.0'
                pom {
                    name = 'User Center SDK'
                    description = 'A user center SDK for Android.'
                }
            }
        }
        repositories {
            maven {
                name = "companyRepo"
                url = uri("https://maven.company.com/repository/android-release/")
                credentials {
                    username = findProperty("mavenUser")
                    password = findProperty("mavenPassword")
                }
            }
        }
    }
}
```

发布任务：

```bash
# 发到 Maven Local -> ~/.m2/repository/com/example/sdk/user-center/1.0.0/
./gradlew :user-center-sdk:publishToMavenLocal

# 发到指定仓库（任务名 = publish<Publication>PublicationTo<RepoName>Repository）
./gradlew :user-center-sdk:publishReleasePublicationToCompanyRepoRepository
```

发布时 Gradle 会：编译 Kotlin/Java → 生成 R 文件 → 打包 AAR → 生成 POM → 生成 module metadata → 生成校验文件 → 上传。

---

## 五、集成方如何消费

```groovy
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
        maven {
            url = uri("https://maven.company.com/repository/android-release/")
            credentials { username = "xxx"; password = "xxx" }
        }
    }
}

dependencies {
    implementation "com.example.sdk:user-center:1.0.0"
}
```

### 依赖解析流程

```text
1. 按 groupId/artifactId/version 计算仓库路径
2. 按 repositories 声明顺序查找（google() -> mavenCentral() -> 公司私服）
3. 找到 .module / .pom 元数据
4. 下载 aar/jar
5. 解析并递归下载传递依赖
6. 放入本地 Gradle 缓存
7. 加入 compileClasspath / runtimeClasspath
```

### 消费时依次发生什么

- **编译**：AAR 里的 `classes.jar` 进入编译 classpath。
- **资源合并**：AAR 的 `res/` 参与 App 资源合并，SDK 里的 string/布局在最终 App 可访问。
- **Manifest merge**：AAR 的 `AndroidManifest.xml` 合并进 App。这也是 SDK 不能随便声明权限、Provider、exported 组件的原因——权限可能算到主 App 头上，应用市场审核会找主 App 说明。
- **混淆**：AAR 里的 `consumer-rules.pro` 自动并入 App 混淆规则，集成方无需手动配置。
- **打包**：SDK 的代码、资源、so、assets 最终打进 APK/AAB。

### 注意：Gradle 缓存 ≠ Maven 本地仓库

```text
mavenLocal()   -> ~/.m2/repository
Gradle 缓存    -> ~/.gradle/caches/modules-2/files-2.1/
```

两者不是同一个目录。

---

## 六、依赖声明 → classpath → POM scope（核心速查）

### 1. 两种 classpath

- `compileClasspath`：**编译期**类路径，编译器需要看到哪些类。缺了会报 `Unresolved reference`、`Cannot access class`。
- `runtimeClasspath`：**运行期**类路径，程序真正运行时需要哪些类。缺了会报 `ClassNotFoundException`、`NoClassDefFoundError`（典型场景：`Class.forName`、SPI、反射）。

### 2. 四种 Gradle 声明

| Gradle 声明 | 当前模块 compileClasspath | 当前模块 runtimeClasspath | 发布到 POM 常见 scope | 语义 |
| --- | --- | --- | --- | --- |
| `api` | 有 | 有 | `compile` | 对外 API 暴露该类型，消费方编译也需要 |
| `implementation` | 有 | 有 | `runtime` | 纯内部实现，消费方编译期不应感知 |
| `compileOnly` | 有 | 无 | 通常不发布，或映射为 `provided` | 编译需要，运行时由外部环境提供 |
| `runtimeOnly` | 无 | 有 | `runtime` | 编译不需要，运行时才需要（反射/SPI/驱动） |
| `testImplementation` | 测试有 | 测试有 | 不发布 | 测试依赖 |

### 3. 四种 Maven POM scope

- `compile`：消费方编译 + 运行都需要，会传递。≈ Gradle `api`。
- `runtime`：消费方编译期不暴露、运行期需要，会传递。≈ Gradle `implementation` / `runtimeOnly`。
- `provided`：编译需要、运行时由外部环境提供、不打进产物。≈ Gradle `compileOnly`。
- `test`：只在测试期需要，不传递给正常消费方。≈ `testImplementation`。

### 4. 关键映射（注意是“大致对应”）

```text
api            -> POM compile
implementation -> POM runtime
runtimeOnly    -> POM runtime
compileOnly    -> 通常不发布 / 接近 provided
```

实际映射会受 Gradle 版本、`maven-publish`、Java Library Plugin、Android Gradle Plugin 以及 Gradle Module Metadata（`.module`）影响。

### 5. 实用判断原则

```text
public API 暴露出去的依赖，用 api
库内部实现用的依赖，用 implementation
运行环境一定会提供的依赖，才用 compileOnly
编译不需要但运行反射/SPI 需要的依赖，用 runtimeOnly
```

---

## 七、常见坑与症状

- **该 api 却用了 implementation** → 集成方编译报 `Cannot access class 'XxxClient'`、`class file for xxx not found`。修复：把 `implementation` 改成 `api`。
- **api 用太多** → 消费方编译 classpath 被污染，编译变慢、版本冲突概率上升、模块边界变差。
- **implementation 发布后变成 POM runtime** → 消费方编译期看不到该依赖。如果公开 API 里出现了它的类型（例如返回 `JsonObject`），集成方就会报 `Cannot access class 'com.google.gson.JsonObject'`。
- **滥用 compileOnly 发布 SDK** → 集成方只依赖你的库、没自己加该依赖时，运行时崩 `NoClassDefFoundError: okhttp3.OkHttpClient`。要记住：`compileOnly` 不是“帮集成方自动带上依赖”，而是“我编译要用，运行时你外部提供”。
- **compileOnly 不会打进 AAR**，但你的 class 里可能存在对它的引用 → 运行时没有就崩。
- **重复类冲突**：两个依赖带了同一个类 → `Duplicate class com.xxx.SomeClass found in modules A and B`，本质是 classpath 里出现重复 class。
- **编译能过、运行崩**：常见原因是 compileOnly 用错、POM 没正确声明 runtime 依赖、依赖被 exclude、冲突解析到不兼容版本。
- **版本号反复覆盖 Release** → 集成方缓存混乱、不同机器拿到不同产物、CI 不可复现。开发联调请用 `1.0.1-SNAPSHOT`。
- **依赖冲突**：SDK 依赖 OkHttp 4.9.0、App 依赖 4.12.0 时，Gradle 通常选较高版本；若存在二进制不兼容会报 `NoSuchMethodError`、`NoClassDefFoundError`。

---

## 八、一句话总结

SDK 提供方把 Android Library 编译成 AAR，再生成 POM / module metadata 描述坐标与依赖，上传到 Maven 仓库；集成方配置仓库地址后通过 `groupId:artifactId:version` 依赖它，Gradle 根据坐标下载 AAR、读取 POM 解析传递依赖，最后把 SDK 的代码、资源、Manifest、混淆规则合并进 App。

最核心的三个东西：

```text
坐标：    com.example.sdk:user-center:1.0.0
产物：    user-center-1.0.0.aar
依赖描述：user-center-1.0.0.pom / user-center-1.0.0.module
```

---
