---
title: "《代码整洁之道》读书笔记"
description: "按章节整理《代码整洁之道》中关于命名、函数、注释、错误处理、单元测试与类的核心观点与实践建议。"
pubDatetime: 2025-10-11T23:07:00+08:00
featured: false
draft: false
tags:
  - 读书笔记
  - 代码规范
---

## 前言

怎么读，作者给了建议：

![image-20251029234034662](./clean-code-reading-notes/images/202510292340728.png)

## 第一章 整洁代码

AI 时代下，这种情况是否出现了改观呢？

![image-20251029234438760](./clean-code-reading-notes/images/202510292344804.png)

一个有职业素养的程序员的态度

![image-20251029235213086](./clean-code-reading-notes/images/202510292352137.png)

## 第二章 有意义的命名

不要同时有 Product、ProductInfo、ProductData 这种命名

![image-20251030235925883](./clean-code-reading-notes/images/202510302359916.png)

为什么呢？Data、Info 我可以理解，因为他们没有意义，但我经常可以看到 XXManager、XXProcessor，我觉得他想说的是不要单独使用 Manager/Processor/Data/Info，但可以使用短语的方式。

![image-20251030231236550](./clean-code-reading-notes/images/202510302312592.png)	

### 统一概念

同一个场景，统一使用一种概念：

![image-20251031000106159](./clean-code-reading-notes/images/202510310001197.png)

### 添加有意义的语境

这里用来拆分一个函数的方式，是把它内聚到一个单独的新类中，这个是我之前没有见过的，学到了。

![image-20251031000236868](./clean-code-reading-notes/images/202510310002900.png)

![image-20251031000427274](./clean-code-reading-notes/images/202510310004307.png)

![image-20251031000448033](./clean-code-reading-notes/images/202510310004073.png)

## 第三章 函数

自顶向下读代码，我以前通常是先写一个函数，再在这个函数下面去调用这个函数，意为：上面那个函数已经读过了，那么下面那个函数去调用，会比较好理解。

这个自顶向下读代码的方式，确实挺符合阅读习惯的，也适合去用来拆分函数。

![image-20251107000135397](./clean-code-reading-notes/images/202511070001466.png)

## 第四章 注释

![image-20251109221319593](./clean-code-reading-notes/images/202610251232044.png)

变量名和函数名都是很好的表达意思的方式，比注释更要有力、直接

![image-20251109215720062](./clean-code-reading-notes/images/202511092157151.png)

## 第六章 对象和数据结构

第一次知道了面向过程编程与面向对象编程这种特性，逐帧学习

![image-20251111234820389](./clean-code-reading-notes/images/202511112348428.png)

![image-20251111234834457](./clean-code-reading-notes/images/202511112348488.png)

![image-20251111234754522](./clean-code-reading-notes/images/202511112347593.png)

![image-20251111235159188](./clean-code-reading-notes/images/202511112351214.png)

### 得莫忒耳律

这一节没看懂

![image-20251112000347148](./clean-code-reading-notes/images/202511120003181.png)

![image-20251112002122495](./clean-code-reading-notes/images/202511120021523.png)

本章的总结：

- 对象适合拓展类型，即一个行为的不同表现方式，但不适合拓展行为（函数），需要改动每个类型

- 固有的数据结构适合被用于构建、拓展行为，但不适合拓展类型（数据结构），需要改动每个函数

## 第七章 错误处理

作者推荐大部分情况下，不需要使用检查式异常，这会造成调用链上链式的修改，而只需要运行时异常

![image-20251112235508220](./clean-code-reading-notes/images/202511122355277.png)

异常统一打包处理，这个方式挺妙的。加了一个中间层，也能减少与三方库的耦合度。

![image-20251112233845215](./clean-code-reading-notes/images/202511122338281.png)

![image-20251112233902887](./clean-code-reading-notes/images/202511122339943.png)

特例模式，学习了，这个要运用面向对象，运用多态。其实就是处理一种默认情况，类似默认值，这比抛出异常或者返回 null 要好很多

![image-20251112234458613](./clean-code-reading-notes/images/202511122344662.png)

此外记住一种简洁的异常处理方式，try-catch-finally 每一块尽可能封装到单独的方法中，尤其是当他们很长的时候，这样整洁

## 第八章 边界

Adapter 的一种绝佳应用：当三方代码尚未确定，我们先设计好我们自己的 API，当三方代码设计完毕，我们通过 Adapter 将三方代码 API 功能调用通过 Adapter 转化为我们自己 API 的形式，仍然不影响我们的调用方式。

![image-20251116111206306](./clean-code-reading-notes/images/202511161112400.png)

## 第九章 单元测试

单元测试的意义：为所有改动提供保障，为重构保驾护航，防止代码腐化的有效手段

![image-20251116115407577](./clean-code-reading-notes/images/202511161154629.png)

![image-20251116115356996](./clean-code-reading-notes/images/202511161153036.png)

## 第十章 类

![image-20251125232742522](./clean-code-reading-notes/images/202511252327574.png)

![image-20251125232755034](./clean-code-reading-notes/images/202511252327064.png)

这一点，学习了，当存在越来越多成员变量被少量函数共享，为什么不把它们拆分，封装到一个单独的类中呢？

![image-20251125233017751](./clean-code-reading-notes/images/202511252330789.png)

一种重构的场景，类的拆分、组织

![image-20251126233150322](./clean-code-reading-notes/images/202511262331407.png)

![image-20251126233251775](./clean-code-reading-notes/images/202511262332819.png)

![image-20251126233301950](./clean-code-reading-notes/images/202511262333988.png)

## 第十一章 系统

依赖注入、AOP，这一章的内容层次比较高，上升到系统架构层级，用到后端里面的 EJB1 EJB2 等标准，不熟悉，比较难学（主要是没有实践经验），后面慢慢悟吧
