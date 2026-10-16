---
title: "Kotlin 协程小记：核心概念与异常处理"
description: "整理 Kotlin 协程的挂起函数、CoroutineScope、CoroutineContext 等核心概念，以及结构化并发与异常处理中的常见问题。"
pubDatetime: 2025-03-04T20:23:00+08:00
featured: false
draft: false
tags:
  - Kotlin
  - 协程
  - Android
---

Kotlin 协程的学习笔记，整理挂起函数、CoroutineScope、CoroutineContext、结构化并发与异常处理这些核心概念，以及同步、异步写法上的取舍。内容还在持续补充，目前记录的是已经想清楚的部分和几个仍在验证的问题。

## 相关文章

- ⭐Kotlin 协程与 JS 异步实现的渊源：https://johnsonlee.io/2020/04/01/asynchronous-programming/
- ⭐[一文快速入门 Kotlin 协程](https://juejin.cn/post/6908271959381901325)
- 公众号文章
  - [速通协程，一步到位！](https://mp.weixin.qq.com/s/KOdJ4IHpa874nyJgOeqG7Q)
  - [Android Kotlin协程（挂起函数+协程作用域）](https://mp.weixin.qq.com/s/qnngFIkrndHK5sPGnOn4Kw)
  - ⭐[Kotlin协程再探，为什么使用了协程反而更慢了？](https://mp.weixin.qq.com/s/THwfQkE-qMgzBDr-GFgcNw)
- 结构化并发
  - http://chuquan.me/2023/03/11/structured-concurrency/
- 协程中的异常处理
  - https://www.lukaslechner.com/why-exception-handling-with-kotlin-coroutines-is-so-hard-and-how-to-successfully-master-it/
- ⭐协程的取消与异常处理：https://mp.weixin.qq.com/s/YYLVeSAN4-R_cZhDKte-UQ?scene=1&click_id=6
- ⭐状态机、续体与结构化并发的魔法：https://mp.weixin.qq.com/s/FlJjO6lC9_FuI8-VdOKR4w

## 核心概念

- suspend function 挂起函数

- CoroutineScope 协程作用域

  常见的协程作用域：

  - GlobalScope
  - runBlocking
  - CoroutineScope
  - SupervisorScope

- CoroutineContext 协程上下文

  其中的元素包括：

  - Job：控制协程的生命周期
  - CoroutineDispatcher：将任务指派给适当的线程
  - CoroutineName：协程的名称，可用于调试
  - CoroutineExceptionHandler：处理未捕获的异常

- CoroutineBuilder 协程构建器

  - launch 
  - asyc

## 记录

可以理解为一个轻量级线程，一个线程中可以包含多个协程，并且它是完全建立在编程语言的基础上，不会涉及到底层的操作系统，所以特别轻量化，特别高效。

- `GlobalScope.launch { }`：启动一个顶层的协程，直到程序生命周期结束才回收，不会阻塞线程。
- `runBlocking { }`：启动一个协程，并且保证其子协程或代码会执行完全，未执行完会阻塞线程（一般不在项目中执行，有性能问题，测试用居多）
- `launch { }`：启动一个子协程，需要在协程作用域中执行（上面两个方法会创建协程作用域），返回一个 Job 对象
- `coroutineScope { }`：一个挂起函数，继承调用时的**协程上下文（不是作用域）**，创建一个新的协程作用域且保证其作用域内的所有代码和子协程在全部执行完之前，外部的协程会一直被挂起（但不会影响线程）
- `supervisorScope` 挂起函数，用于创建一个使用了 SupervisorJob 的 coroutineScope，该作用域的特点就是抛出的异常不会连锁取消同级协程和父协程
- `delay()`：让协程挂起限定的时间，是挂起函数。
- `suspend` 关键字，声明方法是一个挂起函数，挂起函数之间可以相互调用（普通的函数不能直接调用挂起函数，除非它提供一个协程作用域在其中调用），挂起函数意味着协程在执行它的时候会挂起（协程阻塞），并在之后的某个时机恢复，比如`delay(1000)`
- `async { }`：需要在协程作用域中执行，开启一个新的子协程，返回一个 Referred 对象，可以获得执行结果，而 launch 函数不行
- `await()`：Referred 对象的方法，可以获取其执行（最后一行返回值）的结果
- `withContext() { }` ：是一个挂起函数，会立即执行代码块中的代码，同时将外部协程挂起。当代码块中的代码全部执行完之后，会将最后一行的执行结果作为`withContext()`函数的返回值返回，相当于`async{...}.await()`，需要传入一个 CoroutineContext 参数，指定协程类型，有 `Dispatchers.Default`、`Dispatchers.IO`、`Dispatchers.Main` 三种，具体参见第一行代码内容。
- `suspendCoroutine { }`：需要在**协程作用域 / 挂起函数**中执行，会挂起当前的协程，并在一个子线程中执行 lambda 表达式中的内容，通过 `resume()` 和 `resumeWithException()` 来重新恢复挂起的协程。可以用来简化网络回调的写法。具体可参考第一行代码内容。

## 异常处理

1. 只要某个子协程因异常失败（CancellationException 除外，视作取消），就会立即通知父协程；父协程会马上取消所有其他子协程，随后自身也被取消，并将异常继续向上传播。
2. 父作用域失败，内层作用域同样取消
3. 协程取消的本质，是在协程官方挂起点（delay、withContext）检查 isActive（实际实现不是这样），并抛出 CancellationException，父协程接收到该异常，不会继续向上传播。
4. CancellationException 不能主动捕获，捕获后必须重新抛出，否则协程会识别不到取消信号（父协程主动 cancel，此时子协程会在挂起点抛出 CancellationException，如果捕获，子协程就不会被取消，父协程将一直处在取消中的状态，等待子协程结束后，才会结束）
5. supervisorScope 作用域中的子协程之间是隔离的，子协程的异常，不会造成父协程和兄弟协程的取消。但这个异常如果没有被手动捕获，会造成程序崩溃，需要在子协程中主动捕获，或者设置全局异常处理器。
6. async 异常在非 supervisorScope 作用域中，出现异常会立即向上传播，不会等待 await，只能设置全局异常处理器。在 supervisorScope 中，不会向上传播，会在 await 时才暴露出来，此时必须捕获，否则程序会崩溃（除非设置了 CoroutineExceptionHandler）
7. 我们必须在作用域或顶级协程中设置处理 CoroutineExceptionHandler，否则不会生效
8. 如果非 supervisorScope （顶层作用域）设置了CoroutineExceptionHandler，它的子协程出现异常没有捕获，CoroutineExceptionHandler 会捕获到异常，但同时，其他子协程会被取消，除非设置为 supervisorScope

## 同步 & 异步

- 同步
  - 任务一个一个地执行
  - 单线程执行
- 异步
  - 任务同时能够执行
  - 多线程执行，或者单线程轮流执行

形象理解：

- 背景：一次同学聚会，A 和 B 要去参加，A 去 B 家与其同行，B 有事情要处理
  - 同步的处理方式：A 在门口等待 B 把事情处理完了，一起过去
  - 异步的处理方式：A 先走一步，B 处理事情完成后再单独过去（A 没有浪费自己的时间）

异步的好处：

- 能够保证多任务并行，资源利用效率上更高。
- 图形化页面，点击进行耗时任务时，能够保证用户操作不会卡顿，不是执行完耗时操作才能响应用户操作，体验感大大提升。

相关文章：

- [异步JavaScript 简介- 学习Web 开发| MDN](https://developer.mozilla.org/zh-CN/docs/Learn/JavaScript/Asynchronous/Introducing)

## 零散的理解

### 协程的意义

看了一些文章下来，我理解协程的特点/优势有如下几个：

1. **很好地支持结构化并发。**方便对并发任务进行统一的管理（通过协程作用域），减少内存泄漏风险和维护成本
2. **方便地进行线程切换。**可以方便地将不同的任务安排到合适的线程中
3. 支持**以同步的方式来编写异步代码**（通过挂起/恢复），避免了“回调地狱”，代码可读性上大大提高了

## 问题

1. CoroutineScope 与 CoroutineContext 是分离的，为什么呢？
