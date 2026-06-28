---
title: "Gradle 字节码插桩前置知识（一）：ASM 基础"
description: "介绍 Android Gradle 代码插桩前需要掌握的 ASM 基础，包括 Core API、ClassReader、ClassVisitor、ClassWriter、Tree API 以及借助插件辅助编写插桩代码的基本流程。"
pubDatetime: 2026-06-28T20:10:00+08:00
featured: false
draft: false
tags:
  - Android
  - Gradle
  - ASM
  - 字节码插桩
---
## 1. 背景

我们期望通过插桩的方式实现按键防抖的效果，如下所示：

```kotlin
 // 插桩前
 btn.setOnClickListener {
        Toast.makeText(this@MainActivity, "button clicked", Toast.LENGTH_SHORT).show()
 }
 // 插桩后
 btn.setOnClickListener {
        if(Utils.isFastClick()){
                return
        }
        Toast.makeText(this@MainActivity, "button clicked", Toast.LENGTH_SHORT).show()
 }
```

插桩涉及到 ASM 和 Transform 相关的知识，本文将对 ASM 进行基本的介绍。

## 2. ASM

.java 文件需要经过编译转为 .class 文件，再交给 JVM 去加载。JVM 能够加载 .class 的前提，肯定是 .class 文件遵循着某种规则，让它能够解析。既然 .class 是具有规则的，那么能够对 .class 进行处理也就成为一种可能，我们可以在掌握了 .class 文件的规则后，编写一套程序来对它进行解析、处理，达到我们想要的目的。我们可以想到这样的方式，那么市面上一定也已经有一些成熟的方案了，比如，ASM 就是市面上一个非常成熟的开源库，可以帮助我们解析、修改 class 文件。

同时，这种对直接字节码的修改对我们的正常业务代码来说是无侵入的，可以在正常业务代码的基础上，进行字节码层面的修改，不对原来的逻辑造成影响。我们仍然可以按照我们原有的习惯去编写点击事件的代码，不需要考虑写入防抖的逻辑，ASM 能够在我们无感知的情况下，完成防抖的逻辑插入。这也是 AOP 思想的一种体现。

### 2.1. 基本使用

ASM 提供了两套主要的 API 供我们使用，一个是基于事件（Event based）的 Core API，另一个是基于对象（Object based）的 Tree API。

Core API 在解析 class 文件时将每个信息通过事件传递给我们，简单来说它在解析 class 文件时会按照一定的顺序，遇到特定的节点就回调对应的方法，我们通过重写方法来做增删改操作。

Tree API 将解析的 class 文件封装为一个 ClassNode，以类似于 HTML DOM 树的方式，让我们能够对其中的不同节点进行增删改操作。简单来说，就是将 class 文件的所有信息，封装在容器中，我们可以对容器进行增删改操作。

#### 2.1.1. Core API

##### 2.1.1.1. 核心角色

###### 2.1.1.1.1. ClassVisitor

ASM 提供给我们对 class 文件进行增删改的 API 都基于这个`ClassVisitor`抽象类，这个类中每个方法都对应 class 文件中的某一个结构，也就是说 ASM 根据 class 文件的规则，将一个 class 的结构拆分成为许多不同的节点，对应不同的 `visitXX()` 方法，当解析到节点的时候，就调用 `visitXX()` 方法，来提取到我们需要的信息，并进行我们想要的增删改操作。

同时 ClassVisitor 内部持有一个 ClassVisitor 类型字段，以代理的方式调用不同的 `visitXX()` 方法，这使得我们可以构建一条不同 ClassVisitor 组成的链条，逐层装饰，以组合的方式丰富一个基本的功能，逐层插入新的逻辑，这部分介绍将在下面进行展开。

###### 2.1.1.1.2. ClassReader

ClassReader 的核心作用是解析 class 文件的信息，并在解析的过程中，在对应的节点调用 ClassVisitor 的对应方法。

下面举个使用 ClassReader 和 ClassVisitor 打印类信息的例子：

1. 首先定义一个 ClassPrinter 类，重写我们需要的方法

   ```java
    public class ClassPrinter extends ClassVisitor {
           public ClassPrinter() {
                   super(ASM4);
           }
    ​
           @Override
           public void visit(int version, int access, String name, String signature, String superName, String[] interfaces) {//visit() 在解析过程中最先调用，在这里可以获得访问修饰符、类名称、父类名称等信息
                   System.out.println(name + " extends " + superName + " {");
           }
    ​
           @Override
           public FieldVisitor visitField(int access, String name, String desc, String signature, Object value) {//解析到字段时调用，字段信息、方法信息这类较复杂的结构，以和 ClassVisitor 类似的 Visitor 去访问其中不同结构
                   System.out.println(" " + desc + " " + name);
                   return null;
           }
    ​
           @Override
           public MethodVisitor visitMethod(int access, String name, String desc, String signature, String[] exceptions) {//解析到方法时调用，字段信息、方法信息这类较复杂的结构，以和 ClassVisitor 类似的 Visitor 通过不同的 visitXX() 方法去获取修改字段、方法的信息
                   System.out.println(" " + name + desc);
                   return null;
           }
    ​
           @Override
           public void visitEnd() {//解析结束调用
                   System.out.println("}");
           }
    }
   ```

2. 构建 ClassReader 和 ClassVisitor，调用 ClassReader accept() 方法

   ```java
    ClassReader cr = new ClassReader("java.lang.Runnable");// 构建 ClassReader，指定对哪个 class 文件进行解析，也可传入 InputStream 解析指定 class 文件
    ClassVisitor cv = new ClassPrinter();// 构建 Visitor
    cr.accept(cv, 0);// ClassReader 调用 accept 接收一个 ClassVisitor，ClassReader 开始对文件进行解析，解析过程中调用 ClassVisitor 对应的方法
   ```

3. 输出结果如下

   ```text
    java/lang/Runnable extends java/lang/Object {
     run()V
    }
   ```

###### 2.1.1.1.3. ClassWriter

ClassWriter 核心作用是生成类文件，它继承实现了 ClassVisitor，与我们自定义的 Visitor 的职责不同，它所有的 `visitXX()` 方法会对方法的入参信息进行组合存储，最后以一个字节数组的形式提供出来，对应的就是一个新的 class 文件。

官方给出的生成一个类的例子如下

考虑生成如下的接口

```java
 package pkg;
        public interface Comparable extends Mesurable {
            int LESS = -1;
            int EQUAL = 0;
            int GREATER = 1;
            int compareTo(Object o);
 }
```

通过 ClassWriter 进行 6 次方法调用即可生成：

```java
 ClassWriter cw = new ClassWriter(0);
 cw.visit(V1_5, ACC_PUBLIC + ACC_ABSTRACT + ACC_INTERFACE, "pkg/Comparable", null, "java/lang/Object", new String[] { "pkg/Mesurable" });
 cw.visitField(ACC_PUBLIC + ACC_FINAL + ACC_STATIC, "LESS", "I", null, new Integer(-1)).visitEnd();
 cw.visitField(ACC_PUBLIC + ACC_FINAL + ACC_STATIC, "EQUAL", "I", null, new Integer(0)).visitEnd();
 cw.visitField(ACC_PUBLIC + ACC_FINAL + ACC_STATIC, "GREATER", "I", null, new Integer(1)).visitEnd();
 cw.visitMethod(ACC_PUBLIC + ACC_ABSTRACT, "compareTo", "(Ljava/lang/Object;)I", null, null).visitEnd();
 cw.visitEnd();
 byte[] b = cw.toByteArray();// 生成的 class 对应的字节信息
```

##### 2.1.1.2. 基本使用流程

上面的例子中都是单独使用 ClassReader 打印信息或使用 ClassWriter 生成类，平时我们更常用的是对已有的 class 文件进行修改，这意味着我们要先解析 class 文件，再根据一定的条件对其进行更改，这时候就需要将它们结合起来使用了。

下面的代码展示了我们解析一个 class，并将它重新生成的过程

```java
 byte[] b1 = ...;
 ClassWriter cw = new ClassWriter(0);
 ClassReader cr = new ClassReader(b1);
 cr.accept(cw, 0);
 byte[] b2 = cw.toByteArray(); // b2 和 b1 表示同一个类
```

我们读取了一个 class，并使用 ClassWriter 对其进行重新生成，这本身没有意义，我们并没有修改任何东西。

再进一步，我们引入 ClassVisitor：

```java
 byte[] b1 = ...;
 ClassWriter cw = new ClassWriter(0);
 ClassReader cr = new ClassReader(b1);
 // 将 cw 传入给 cv，cv 会将所有事件转发给 cw
 ClassVisitor cv = new ClassVisitor(ASM4, cw) { };
 cr.accept(cv, 0);
 byte[] b2 = cw.toByteArray(); // b2 与 b1 表示同一个类
```

在开始介绍 ClassVisitor 时我们提到过它内部可以持有另一个 ClassVisitor 引用，所有的方法调用都会委托给这个引用。在这里我们将 cw 传给了 cv，当 ClassReader 调用 cv 的方法时，实际上都会将事件传递给 cr，也就是最后都会被 ClassWriter 写入到字节数组中。

> 配图占位：`image-2023-12-4_22-2-43.png`（原文档中的本地图片未随 Markdown 一起上传，后续可补充到博客资源目录。）
这里得到的结果还是没有变化，因为我们没有在 ClassVisitor 中重写任何方法，实际上我们可以通过在 ClassVisitor 中重写对应的方法，来完成我们需要的修改。看如下的自定义 Visitor 类

```java
 public class ChangeVersionAdapter extends ClassVisitor{
        public ChangeVersionAdapter(ClassVisitor cv) {
                super(ASM4, cv);
        }
        @Override
        public void visit(int version, int access, String name, String signature, String superName, String[] interfaces) {
                cv.visit(V1_5, access, name, signature, superName, interfaces);
        } }
```

这里仅重写了一个 visit() 方法，并修改了类的版本号，其他所有的方法都没有变动，还是原封不动地传递给下一个 cv 去处理

我们编写如下的代码，最后得到的这个类它的版本号被修改为 V1\_5

```java
 byte[] b1 = ...;
 ClassWriter cw = new ClassWriter(0);
 ClassReader cr = new ClassReader(b1);
 // 将 cw 传入给 cv，cv 会将所有事件转发给 cw
 ClassVisitor cv = new ChangeVersionAdapter(cw);
 cr.accept(cv, 0);
 byte[] b2 = cw.toByteArray();
```

> 配图占位：`image-2023-12-4_22-3-9.png`（原文档中的本地图片未随 Markdown 一起上传，后续可补充到博客资源目录。）
这里的例子比较简单，介绍了大致流程，后面将会结合 ASM 插件来针对具体的插桩场景进行讲解。

#### 2.1.2. Tree API

Tree API 将解析的 class 文件封装为一个 ClassNode，以类似于 HTML DOM 树的方式，让我们能够对其中的不同节点进行增删改操作。简单来说，就是将 class 文件的所有信息，封装在容器中，我们可以对容器进行增删改操作。

Core API 是在解析 class 过程中去进行各种 visit 事件的处理，并且遵循着一定的顺序，这也意味着在处理对应事件的时候，这个时刻对 class 文件的解析还没有结束，无法完整地获取一个 class 中的所有信息，所以在某些复杂场景下，使用 Core API 可能需要对同一个 class 进行多次解析，才能满足我们的需要。此时 Tree API 的优势就显现出来了，它随着 accept() 方法的结束，就能够获取全部 class 信息，通过对容器简单的增删改，就能使实现一些复杂需求。不过取而代之的是 Tree API 需要多耗费 30% 的时间和更多的内存，在选择时需要去权衡这一成本和 Core API 多次转换的成本。

由于本次插桩使用 Core API 完成，这里不再具体介绍其使用。

### 2.2. AS插件辅助编写插桩代码

#### 2.2.1. 需求场景

假设我们希望通过 ASM 完成如下的效果

```kotlin
 // 插桩前
 class MainActivity : AppCompatActivity() {
     override fun onCreate(savedInstanceState: Bundle?) {
         //...
     }
 }
 // 插桩后
 class MainActivity : AppCompatActivity() {
     override fun onCreate(savedInstanceState: Bundle?) {
                Utils.test()
         //...
     }
 }
 ​
 object Utils {

        fun test(){
                Log.d("Utils", "test() invoked.")
        }
 }
```

有前面的基础，我们可以有大概的思路：

```java
 ClassReader cr = new ClassReader(/*对应 MainActivity class 文件*/);
 ClassWriter cw = new ClassWriter(0);
 ClassVisitor cv = new MethodInjectClassVisitor(cw);// MethodInjectClassVisitor 中完成插入的修改，最后让 classWriter 生成新的 class 文件
 cr.accept(cv, 0);
 byte[] b2 = cw.toByteArray();
```

核心就是 MethodInjectClassVisitor 的编写，如果要直接编写，这里会涉及到比较多的字节码指令的知识，为了简化开发我们引入 ASM Bytecode Viewer Support Kotlin 插件。

#### 2.2.2. 插件使用

引入插件，编辑器中右键鼠标使用插件

> 配图占位：`image-2023-12-4_22-5-17.png`（原文档中的本地图片未随 Markdown 一起上传，后续可补充到博客资源目录。）
插件允许我们查看每个 java/kotlin 文件对应的字节码，这和 AS 中自带的查看 Kotlin 字节码的工具类似，但它同时提供了生成对应类所需要的 ASM 代码：

> 配图占位：`image-2023-12-4_22-5-37.png`（原文档中的本地图片未随 Markdown 一起上传，后续可补充到博客资源目录。）
> 配图占位：`image-2023-12-4_22-6-21.png`（原文档中的本地图片未随 Markdown 一起上传，后续可补充到博客资源目录。）
可以看到包括 onCreate() 方法在内的所有内容都通过插件中的一个 classWriter 对象生成出来，但通过这个我们还是不清楚添加什么代码才能插入一个`Utils.test()`方法调用，但插件确实提供了相应的功能，我们把需要插入的代码手动添加到`onCreate()`方法中：

> 配图占位：`image-2023-12-4_22-6-35.png`（原文档中的本地图片未随 Markdown 一起上传，后续可补充到博客资源目录。）
重新查看对应字节码：

> 配图占位：`image-2023-12-4_22-6-51.png`（原文档中的本地图片未随 Markdown 一起上传，后续可补充到博客资源目录。）
查看与前一次的不同

> 配图占位：`image-2023-12-4_22-7-5.png`（原文档中的本地图片未随 Markdown 一起上传，后续可补充到博客资源目录。）
> 配图占位：`image-2023-12-4_22-7-15.png`（原文档中的本地图片未随 Markdown 一起上传，后续可补充到博客资源目录。）
可以看到插件已经把我们刚才手动插入的代码的代码高亮显示，这就是我们需要在自定义 Visitor 中进行添加的代码。

#### 2.2.3. 编写自定义 Visitor

上面的高亮显示的代码是由 methodVisitor 进行两个方法调用得到的，而 methodVisitor 则是通过`classWriter.visitMethod(...)`获取的，其对应的类型为 MethodWriter，继承了 MethodVisitor，它们的作用和关系类似于 ClassWriter 和 ClassVisitor，其内部封装了很多方法，当访问到方法字节码中对应的节点，就会调用这些方法。我们可以通过自定义 ClassVisitor 完成 Class 修改，也需要自定义 MethodVisitor 来完成对方法的修改。

对应如下的代码：

```kotlin
 class MethodInjectClassVisitor(api: Int) : ClassVisitor(api) {
        // 重写 visitMethod 方法，每次访问到方法，首先会调用该方法，获取对应的 MethodVisitor，最后都会通过 MethodWriter 来将对应的方法信息写入到字节数组中，我们可以通过自定义 MethodVisitor 来完成方法的修改
        override fun visitMethod(
                access: Int,
                name: String?,
                descriptor: String?,
                signature: String?,
                exceptions: Array<out String>?
        ): MethodVisitor {
                val methodVisitor = super.visitMethod(access, name, descriptor, signature, exceptions)// 相当于 cv.visitMethod()，委托给下一个 cv，得到它对应的 methodVisitor，在我们构建的 ClassVisitor 链中，cv 对应 ClassWriter，它的 visitMethod 返回一个 MethodWriter在这里我们相当于得到了一个 MethodWriter
                return object : MethodVisitor(api, methodVisitor) {// 自定义 MethodVisitor
                        override fun visitCode() {
                                super.visitCode()//在 visitCode() 下面插入代码
                                methodVisitor.visitFieldInsn(
                                        GETSTATIC,
                                        "com/example/clickchecklib/Utils",
                                        "INSTANCE",
                                        "Lcom/example/clickchecklib/Utils;"
                                );
                                methodVisitor.visitMethodInsn(
                                        INVOKEVIRTUAL,
                                        "com/example/clickchecklib/Utils",
                                        "test",
                                        "()V",
                                        false
                                );
                        }
                }
        }
 }
```

这样就完成了插桩逻辑的编写

```java
 ClassReader cr = new ClassReader(/*对应 MainActivity class 文件*/);
 ClassWriter cw = new ClassWriter(0);
 ClassVisitor cv = new MethodInjectClassVisitor(cw);// MethodInjectClassVisitor 中完成插入的修改，最后让 classWriter 生成新的 class 文件
 cr.accept(cv, 0);
 byte[] b2 = cw.toByteArray();
```

最后得到的字节数组就是插入了我们需要的这个方法的 class 文件，我们可以将得到的数组通过 FileOutputStream 输出到原 class 路径下，反编译将会看到对应的代码，这里不再演示。

### 2.3. 总结 & 参考

本次插桩在 ASM 的使用大致如上面介绍，作为一个大致过程的参考，其中细节部分没有介绍得很清楚，所以如果是刚接触 ASM 可能还是有疑惑的地方，这里有一些学习过程中的资料可供参考学习：

1.  [Android 进阶之路：ASM 修改字节码，这样学就对了！](https://juejin.cn/post/6999646242125529096)

2.  [Android ASM 框架详解](https://juejin.cn/post/6844904013998243847)

3.  [Android - ASM 插桩你所需要知道的基础](https://juejin.cn/post/7000572440988352549)

4.  [https://asm.ow2.io/](https://asm.ow2.io/)

5.  [ASM 使用手册中文版](https://www.yuque.com/mikaelzero/asm/pd602d)

6.  [JVM 字节码指令表](https://blog.csdn.net/qq_33589510/article/details/105285250)

7.  [Oracle 官方指令集](https://docs.oracle.com/javase/specs/jvms/se8/html/jvms-6.html#jvms-6.5)
