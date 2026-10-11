---
title: "设计模式学习笔记：从设计原则到 23 种模式"
description: "按设计原则、UML 类图到具体模式的顺序整理设计模式学习笔记，包含简单工厂、策略、装饰、观察者、单例、建造者等模式的意图与实现要点。"
pubDatetime: 2025-05-17T21:41:00+08:00
featured: false
draft: false
tags:
  - 设计模式
  - Java
  - 面向对象
---

设计模式背成 23 个名词不难，难的是判断什么场景该用哪个。这篇笔记从面向对象和设计原则讲起，再按顺序整理简单工厂、策略、装饰、观察者、迭代器、适配器、模板方法、工厂方法、单例、原型、建造者、抽象工厂、桥接等模式的意图、结构与实现要点，每个模式都配了类图或示意图。可以当速查手册翻，也适合跟着顺序过一遍。

## 学习思路

1. 学习路线：

   https://www.codefather.cn/course/1789189862986850306/section/1789190698894860290?type=&v=%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F#heading-10

2. 书籍：

   - 图解设计模式，就着这本按顺序看
   - 深入设计模式，不懂的地方交叉着看

3. 优先级

   ![image-20241206001911773](./design-patterns-notes/images/202412060019828.png)

## 基本概念

### 面向对象

封装、继承、多态。

万物皆对象。

抽象类和接口的不同作用。

抽象是精髓所在，万物皆对象，class 就是一种抽象。

完成抽象，意味着囊括多种变化/数据/类型，应对不同的场景。让开发过程尽可能只需要对抽象进行具体化实现即可（复用/拓展），而不是说处处具体化，这样意味着效率低下和冗余。

**好程序的标准：**

1. 可维护
2. 可拓展
3. 可复用
4. 灵活性好

### UML 类图

[30分钟学会UML类图-知乎](https://zhuanlan.zhihu.com/p/109655171)

## 设计原则

### 单一职责原则 S

对于一个类而言，应该仅有一个引起它变化的原因。每个类、每个方法只有一项具体的职责。简单来说就是某一种变化只对应某个类/方法，而不会在多种需求出现时只改变一个类。

单一职责意味着耦合性的降低。

形象的举例：手机阅读 or 电子阅读器阅读

### 开放-封闭原则 O

对拓展开放，对修改封闭。对迎面而来的变化，尽可能化为一种拓展，而不是对原有逻辑的修改。这就要求我们在开发、设计过程中，要合理的利用抽象（类、抽象类、接口），使得变化发生时，只需拓展一些类即可，而不用修改原有的类。

当然，过度抽象也是不必要的，过犹不及。

### 依赖倒置原则 D

依赖抽象（接口/抽象类），而不是具体实现。（面向接口编程，而不是具体实现）

如果依赖具体的实现，比如高层模块依赖底层模块，那么如果现在底层模块不能满足需求，我们就无法使用高层模块了。所以要把依赖底层实现（具体实现）变为依赖某个抽象（接口/抽象类），这样哪怕原本的底层模块不能使用，但依赖的接口/抽象类没有问题，那么我们就可以进行另外的拓展，来替换掉原来的底层模块。

这里的替换，也涉及到另外的一个原则——**里式替换原则 L**，即所有子类都可以替换掉其父类，也就是说，所有子类一定是可以完成父类的工作的（而这就要求我们采取继承关系，一定是 is-a 的关系，例子：以这种原则来说，企鹅不能继承鸟，因为它不会飞），所以我们依赖父类这个抽象，就可以通过继承、多态来达成可复用、可拓展、高灵活性的效果。而如果不满足这个原则，继承关系将出现问题，比如原本依赖父类某个方法，现在提供了一个子类它不满足里式替换（重写的方法返回值、抛出异常不满足）那么原本的程序将会报错。

另外提一点，为了保证所有子类可以替换掉父类，里式替换原则对子类拓展父类提出了很多要求，尤其是方法重写上，比如返回值、访问修饰符、抛出的异常等，但这里很多编程语言已经帮我们做出了规定（Java 的重写规则）

### 接口隔离原则 I

降低接口的颗粒度，避免“臃肿”接口。实现臃肿的接口会造成部分功能不会被实现类使用到，而如果需要修改接口的时候，同时也要修改实现了它的类。正确的做法是把一个接口的职责拆分开，实现类按需实现不同的接口，这样更加灵活，易于维护，修改较少。详见深入设计模式内容。

## 设计模式内容

### 设计模式的分类

- 创建型
- 结构型
- 行为型

### 简单工厂模式

多个类继承一个基类，再通过专门的工厂类（Factory），根据相应的要求（变化点、参数），来构建这个基类对象（多态），完成不同的功能。当需要拓展功能的时候，只需要添加一对应的子类即可。

场景：一个计算器的程序设计

一般的思路是：在一个类中完成所有工作，用户输入、程序接收，判定操作符（switch）、得到计算结果。

但是为了达到可拓展、易维护的目的，这样做肯定是不行的。

1. 用户图形界面与业务（计算）关联在一起，代码掺杂在一起，这对于后续进行拓展是不利的。你需要人工地再去读代码，整理每个部分的功能。

   所以要将业务逻辑和界面逻辑分开，将它们的耦合度降低。（单独封装一个 Operation 类）

2. 运算符的算法都在一起，修改一个运算的算法会暴露所有的算法，有修改的风险。

   为了方便后续的拓展，比如要添加新的运算，指数运算，可以将所有的运算操作都封装为单独的类，继承 Operation 类，完成相应计算。这样后续对每个算法修改只需要打开单独的类即可，添加新的算法也只需要添加新的类即可。

3. 使用简单工厂模式，添加 OperationFactory 类，由它来创建 Operation 对象，通过传入的操作符参数，判定具体创建哪个运算对象（Add/Sub/Mul/Div）再执行 Operation 的`getResult()`方法，通过多态来决定运行时具体执行哪个方法。

本质上其实就是完成对象的构建，把对象构建过程单独拎出来交给一个类/方法/代码段，这都可以称作工厂模式。

不一定要是一个类，只要逻辑上有这种功能，结合设计原则（单一职责、开闭...）即可

**工厂模式它的主要目的不是为了创建对象实例，而是创建实例来使用（不是为了创建而创建，而是为了使用而创建），所以工厂中可以加入具体的业务逻辑。**

### 策略模式

定义算法家族，并分别进行封装，算法的之间可以进行替换（根据一定的条件使用不同的算法），而且即使算法发生变化，也不会影响到使用者。

大致的思想与简单工厂模式有类似之处。

简单来说就是通过定义一个算法基类，子类来实现具体算法，再定义一个调用者，包含一个基类对象，通过传递不同的参数，来使用到基类中不同的算法。

### 装饰模式

核心是为了保证一个基础的类它的简单性，通过**使用其他类组合来代替直接向其中添加代码，维持类的单一职责（单一、简单）和开闭原则（可拓展、而不修改）**

基本的思路是，定义一个接口，下面一个基本功能的实现类，再有一个作为拓展功能基类的实现类，持有一个接口字段，在其中调用这个接口字段的方法，其子类通过添加其他逻辑，重写接口字段方法，调用父类（基本功能类）接口字段方法的同时添加上新的逻辑。这样在使用时，可以创建一个基本功能实现类，再创建拓展功能类，传入基本实现类，实现一个包装装饰，这样执行方法时既完成了基本实现类的工作，有有了新的功能（装饰）。

### 观察者模式与发布订阅模式

- 观察者模式
  - 被观察者持有观察者的引用，当发生一些事件时，通知观察者（调用观察者的方法）
  - 通过定义一个 Observer 接口，来实现观察者与被观察者的松耦合，每次只需要调用 Observer 的固定方法来通知不同的具体实现子类
  - 特点：面向接口编程，实现松耦合
- 发布订阅模式
  - 发布者与订阅者之间存在一个 Broker，来做事件的传递，从而实现完全耦合
- 总结
  - 使用场景不同，一个松耦合一个完全解耦，就好比公司送月饼、粽子给员工，是自己部门派发，而公司给其他公司寄送物件，是交给快递公司来寄送。
  - 比喻是理解了，但实际的应用场景还是不清楚

> 相关文章：https://zhuanlan.zhihu.com/p/51357583

### 迭代器模式-Itorator

#### 结构

普遍结构：

![image-20241207220201445](./design-patterns-notes/images/image-20241207220201445.png)

示例结构：

![image-20241207221248503](./design-patterns-notes/images/image-20241207221248503.png)

#### 使用场景

对自定义容器进行遍历操作时，可考虑使用迭代器模式。

#### 优势

- **符合依赖倒置原则**。遍历操作依赖接口而不是具体实现，当容器的实现改变，比如存储数据结构从 array 改为使用 ArrayList，不需要修改原来的遍历代码，仍旧采用上面的接口方法调用即可。
- **符合开闭原则**，无需修改 Iterator 类，只需要新增一个实现类应对该情况即可。

### 适配器模式-Adapter

#### 结构

![image-20241208224649315](./design-patterns-notes/images/202412082246429.png)

##### 举例实现结构

![image-20241208230231553](./design-patterns-notes/images/202412082302605.png)

#### 使用场景

- 让现有的类适配新的接口（API）时，几乎总是会使用 Adapter 模式。能够达到不修改现有类（Client、Target 角色），而使新的接口（Adaptee）适配于它们，实现对应功能的效果。
- 软件、库版本升级时，为保持与旧版本 API 兼容，可将新版本作为 Adaptee 角色，旧版本 API 作为 Target 角色，通过 Adapter 使得新版本 API 能够兼容旧版本 API

![image-20241229212546686](./design-patterns-notes/images/202412292125739.png)

### 模板方法模式-Template Method

#### 结构

![image-20241208231708310](./design-patterns-notes/images/202412082317356.png)

#### 使用场景

当我们编写不同类时，当发现多个类中存在重复逻辑，想要将重复逻辑复用，而特定逻辑保留时，就可以使用模板方法模式。

在抽象父类中定义通用可复用的流程，并将一些特定步骤交给子类实现，达到代码复用效果的同时，也能通过多态保持一定灵活性。

#### 拓展点

- 在抽象父类中使用 `final` 修饰方法，表明其无法被重写，这是应该属于父类中的方法。

### 工厂方法模式-Factory Method

#### 结构

![image-20241208235655439](./design-patterns-notes/images/202412082356488.png)

#### 使用场景

工厂方法模式，是模板方法模式的一种应用场景，用来创建对象实例的。

我理解，一开始一定是一个简单工厂模式，当需要创建另一类完全不同类型的产品时，此时就需要另一个工厂，创建另一类产品。此时就可以考虑引入工厂方法模式，进行抽象以及复用了。

### 单例模式-Singleton

保证一个类仅可存在一个实例。适用于一些不需要重复创建/创建较为消耗资源的类。

Java 中单例的 6 种写法：

```java
class Singleton{//饿汉式
    private static final Singleton instance = new Singleton();
    
    private Singleton(){
        
    }
    
    public static Singleton getInstance(){
        return instance;
    }
}

class Singleton{//懒汉式，线程不安全
    private static Singleton instance;
    
    private Singleton(){
        
    }
    
    public static Singleton getInstance(){
        if(instance == null){
            instance = new Singleton();
        }
        return instance;
    }
}

class Singleton{//懒汉式，线程安全
    private static Singleton instance = null;
    
    private Singleton(){
        
    }
    
    synchronized public static Singleton getInstance(){
        if(instance == null){
            instance = new Singleton();
        }
        return instance;
    }
}

class Singleton{//双重校验锁🔒，线程安全
    private static volatile Singleton instance; //需要使用 volatile 关键字，保证其他线程可见，共享该变量，并且防止指令重排序，避免重排序导致的返回未初始化的对象变量。
    
    private Singleton(){
        
    }
    
    public static Singleton getInstance(){
        
        if(instance == null){
            synchronized (Singleton.class){
                if(instance == null){//必须有,如果没有,线程同时通过上面的 == null,会创建多个实例
                    instance = new Singleton();
                }
        	}
        }
        
        return instance;
    }
}

public class Singleton {// 静态内部类方式，利用类加载保证线程安全
    // 私有化构造方法，防止外部直接实例化
    private Singleton() { 
        System.out.println("Singleton instance created");
    }

    // 静态内部类，持有外部类的单例实例
    private static class SingletonHolder {
        // 静态内部类的静态成员，即外部类的唯一实例
        private static final Singleton INSTANCE = new Singleton();
    }

    // 公共静态方法，提供单例的全局访问点
    public static Singleton getInstance() {
        return SingletonHolder.INSTANCE;
    }

    // 示例方法
    public void doSomething() {
        System.out.println("Doing something in Singleton");
    }
    
    public static void main(String[] args) {
        // 获取单例实例并调用方法
        Singleton singleton1 = Singleton.getInstance();
        singleton1.doSomething();

        // 验证同一个实例
        Singleton singleton2 = Singleton.getInstance();
        System.out.println(singleton1 == singleton2); // 输出 true，证明是同一个实例
    }
}
```

### 原型模式-Prototype

#### 核心思想

通过对象实例而不是 `new MyClass()` 来创建实例。 

#### 结构

基本结构：

![image-20241210002327612](./design-patterns-notes/images/202412100023676.png)

示例结构：

![image-20241210002347774](./design-patterns-notes/images/202412100023827.png)

#### 使用场景

- 难以根据类来生成实例时。比如一个类是根据用户阶段性的输入生成的，此时想要再生成一个同样的实例，靠 new 的方式是困难的。此时根据实例来生成实例就简单得多。

书中给的案例是使用 Object 的 clone 进行对象克隆，关于 clone 方法的使用需要另外注意。可参考 Effective Java 中的建议。

### 建造者模式-Builder

#### 结构

##### 基本结构

![image-20241216235829168](./design-patterns-notes/images/202412162358223.png)

##### 示例结构

![image-20241216235743993](./design-patterns-notes/images/202412162357083.png)

#### 使用场景

构建复杂结构的对象实例时可考虑使用。

#### 拓展点

- 其与[模板方法模式](#模板方法模式-Template Method)的不同在于，模板方法是在抽象父类中定义了执行模板，决定了子类方法的执行流程、顺序；而建造者模式中子类方法的执行流程是在 Director 类（即 Builder 的使用者）中决定的。
- 其与外观模式（Facade）有相似之处。建造者模式通过在 Director 中组合 Builder 的方法，为外界提供一个简单的生成实例的接口（API），在示例中则是 `constructor` 方法；而外观模式是通过组合内部模块向外部提供可以简单调用的接口（API）

### 抽象工厂模式-Abstract Factory

#### 结构

##### 基本结构

![image-20241229154118367](./design-patterns-notes/images/202412291541442.png)

##### 示例结构

![image-20241229154042705](./design-patterns-notes/images/202412291540790.png)

#### 使用场景

我理解抽象工厂是工厂方法模式演化而来的。当工厂方法模式中，不止需要创建一种产品，需要不同的工厂，而这些产品、工厂有可以统一进行抽象。从而有了抽象工厂、抽象零件、抽象产品等概念，进而就变为了抽象工厂了。

同时，工厂方法中一般指存在一个 create 方法，而抽象工厂中通常存在一组 create 方法来创建不同的产品。

#### 拓展点

优势：在添加新的产品子类时会很容易，只需要实现/继承现有基类即可。

劣势：在添加新的产品/零件时会很麻烦，需要添加一个新的基类/接口，然后修改工厂基类添加一个新的 create 方法并修改所有具体实现类

### 桥接模式-Bridge

#### 核心思想

利用委托的方式，将**类的功能层次结构**与**类的实现层次结构**进行分离。功能结构的修改、拓展只需要关注**类的功能层次结构**，可以复用已有实现侧代码的同时又不变动实现侧代码。反过来实现层次结构的修改、拓展只需要关注**类的实现层次结构**。

组合优于继承原则的具象化。例子：

![image-20241229212245092](./design-patterns-notes/images/202412292122160.png)

![image-20241229212226320](./design-patterns-notes/images/202412292122389.png)

#### 结构

##### 基本结构

![image-20241229161216163](./design-patterns-notes/images/202412291612220.png)

##### 示例结构

![image-20241229173418643](./design-patterns-notes/images/202412291734710.png)

### 策略模式-Strategy

#### 核心思想

依赖倒置思想的具象化。即定义接口，通过依赖接口、使用接口而不是具体类，达成与不同具体策略算法的解耦。想要更换策略、拓展策略，只需要切换依赖项、拓展新的实现类即可。

#### 结构

##### 基本结构

![image-20241229205850551](./design-patterns-notes/images/202412292058616.png)

##### 示例结构

![image-20241229205947548](./design-patterns-notes/images/202412292059618.png)

### 组合模式-Composite

#### 核心思想

通过组合的方式，构建具有一致性（通过接口/抽象类）的递归结构。

举例：

- Android 中的 View、ViewGroup 结构。
- 文件系统中的 File 与 Directory 结构。

#### 结构

##### 基本结构

![image-20241231151554521](./design-patterns-notes/images/image-20241231151554521.png)

##### 示例结构

![image-20241231151538002](./design-patterns-notes/images/image-20241231151538002.png)

### 访问者模式-Visitor

#### 核心思想

将复杂数据结构与对该数据结构的访问、处理进行分离。在不影响数据结构的情况下，增加处理的功能。

典型应用：

- ASM 库，Java 字节码插桩。

#### 结构

##### 基本结构

![image-20241231154733785](./design-patterns-notes/images/image-20241231154733785.png)

##### 示例结构

![image-20241231153551176](./design-patterns-notes/images/image-20241231153551176.png)

#### 优劣势

![image-20241231194420899](./design-patterns-notes/images/image-20241231194420899.png)

适用于数据结构比较稳定，很少变动的场景。比如字节码格式。

### 装饰模式-Decorator

#### 核心思想

通过组合、委托的方式，对同一接口功能进行递归调用，在其功能可以自由选定、组装的同时，也能达到接口增强的效果。

#### 结构

##### 基本结构

![image-20241229222323240](./design-patterns-notes/images/202412292223312.png)

##### 示例结构

![image-20241229222349683](./design-patterns-notes/images/202412292223750.png)

#### 拓展点

- 其与典型责任链的不同在于，它的执行过程往往无法中断，可以理解为一条任务链

### 责任链模式-Chain Of Responsibility

#### 核心思想

构建一条处理请求的链条，按顺序遍历，决定谁来处理该请求。

#### 结构

##### 基本结构

![image-20241229214520084](./design-patterns-notes/images/202412292145144.png)

##### 示例结构

![image-20241229214622150](./design-patterns-notes/images/202412292146208.png)

#### 使用场景

- 任务链场景。我理解任务链是一种特殊的责任链，链路上的每个节点都会进行处理。用于分步骤执行的任务链场景，比如 TCP、RPC 通信过程中协议数据的组装。认证过程中一系列操作的执行。（这里的任务链可以理解为是装饰模式）
  其优势在于可以方便地组合、排布不同的任务，后续有新的操作需求可以非常方便地拓展。

- Android 中事件传递机制，是责任链模式的典型应用。

  ```java
  // ViewGroup 的事件分发流程伪代码
  fun dispatchTouchEvent(ev: MotionEvent) : Boolean {
      var result = false
      if (onInterceptTouchEvent(ev)) {// ViewGroup 自己是否进行拦截
          result = onTouchEvent(ev)// 如果拦截，直接调用自己的 onTouchEvent() 方法进行处理
      } else {
          result = child.dispatchTouchEvent(ev)// 如果不拦截，交由子视图进行处理，分发，这里实际上是会遍历所有子视图看是否处理
      }
      return result
  }
  ```

#### 拓展思路

- 责任链构建的过程，可以使用其他模式进行进一步封装。

  - 构建操作

  - 使用责任链进行处理

- 可以使用方法递归和迭代两种调用方式来进行责任链任务的执行

  - 递归

    ```java
    public void support(Trouble trouble) {  // 解决问题的步骤
        if (resolve(trouble)) {
            done(trouble);
        } else if (next != null) {
            next.support(trouble);
        } else {
            fail(trouble);
        }
    }
    ```

  - 迭代

    ```java
    public void support(Trouble trouble) {
        for (Support obj = this; true; obj = obj.next) {
            if (obj.resolve(trouble)) {
                obj.done(trouble);
                break;
            } else if (obj.next == null) {
                obj.fail(trouble);
                break;
            }
        }
    }
    ```

### 外观模式-Facade

#### 核心思想

一些软件随着时间推移，功能越来越多。使用时需要了解许多依赖关系、构建顺序、调用顺序等细节。外观模式就是为了解决这个问题的。

对外暴露一个公开易用的接口（API），来使用一些封装好的库、功能。简化组件库、功能库的使用方式。

举例：北极星 SDK 中的 UmsAgent，神策 SDK 中的 SharedSensorsDataAPI。

#### 结构

##### 基本结构

![image-20241229231234065](./design-patterns-notes/images/202412292312150.png)

##### 示例结构

![image-20241229231251503](./design-patterns-notes/images/202412292312583.png)

### 仲裁者/中介者模式-Mediator

#### 核心思想

将各个分散的对象、逻辑交互，进行收拢，统一交由 Mediator 处理。避免分散带来的灾难。

#### 结构

##### 基本结构

![image-20250101130459976](./design-patterns-notes/images/image-20250101130459976.png)

##### 示例结构

![image-20241231210312558](./design-patterns-notes/images/image-20241231210312558.png)

#### 解读

书中举的例子与 Android 中开发页面的场景是一致的，一个页面中存在多个控件，每个控件的状态可能相互影响。

但 Android 中可能并不会使用该方式，而是通过设置一些状态监听，在页面中对这些控件进行统一的状态管理。因为我们不想再单独编写自定义的 View 控件和 Colleague 接口，如果每次如此会存在类膨胀的问题。

![image-20250108233737972](./design-patterns-notes/images/202501082337062.png)

### 观察者模式-Observer

#### 核心思想

示例：

- 自定义的各种 Listener 接口，可以使用 lambda 表达式进行使用。
- Android 中的 LiveData

#### 结构

##### 基本结构

![image-20241231201334747](./design-patterns-notes/images/image-20241231201334747.png)

##### 示例结构

![image-20241231201140666](./design-patterns-notes/images/image-20241231201140666.png)

### 备忘录模式-Memento

#### 结构

##### 基本结构

![image-20250113232310500](./design-patterns-notes/images/202501132323576.png)

##### 示例结构

![image-20250108235818723](./design-patterns-notes/images/202501082358796.png)

#### 拓展点

- Memento 有两类接口（API）

  - wide interface：宽接口，宽指的是功能上更多，能获取、操作 Memento 对象的更多状态。一般 Originator 可访问宽接口。

  - narrow interface：窄接口，窄指的是功能上更少，能获取、操作 Memento 对象的有限。一般 Caretaker 可访问窄接口，不可访问宽接口。

  通过设置宽接口与窄接口，我们限制 Caretaker 对 Memento 的访问，可以减小对 Memento 进行修改的影响面。

- Memento 模式的核心思想在于单一职责和封装。

- 优缺点

  ![image-20250113235700882](./design-patterns-notes/images/202501132357959.png) 

- 可通过数据压缩、计算状态间差值的方式减小内存/磁盘的占用

### 状态模式-State

#### 核心思想

- 利用多态特性，替代 if-else 代码
- 分而治之，将大问题分解为各个小问题处理（分散到子类中）
- 类似于策略模式

应用场景：播放器状态控制

![image-20250119204015001](./design-patterns-notes/images/202501192040087.png) 

#### 结构

##### 基本结构

![image-20250119180242511](./design-patterns-notes/images/202501191802586.png)

##### 示例结构

![image-20250119175041707](./design-patterns-notes/images/202501191750827.png)

#### 拓展点

- 我理解此处示例中的 State 类，可以通过 enum 枚举类来实现，更加方便、易维护，且天然为单例。而对于需要创建多个对象的情况，可以使用 Kotlin 中的 sealed 类
- ![image-20250119183201856](./design-patterns-notes/images/202501191832935.png)
- ![image-20250119204151927](./design-patterns-notes/images/202501192041988.png)

### 享元模式-Flyweight

#### 核心思想

Flyweight 意为轻量级。当重复创建某些重量级对象，会大大占用内存。享元模式的思想就是缓存并复用已有的重量级对象，达到减轻内存负担的作用。

典型应用：

- 池化技术。线程池、连接池。

#### 结构

##### 基本结构

![image-20250119185149961](./design-patterns-notes/images/202501191851041.png)

##### 示例结构

![image-20250119184433989](./design-patterns-notes/images/202501191844072.png)

#### 拓展点

- 当需要使用享元模式时，需要考虑共享对象的修改会对多个地方产生影响。
- 固有信息与非固有信息
  ![image-20250119190505118](./design-patterns-notes/images/202501191905200.png)

### 代理模式-Proxy

#### 结构

##### 基本结构

![image-20241229232037322](./design-patterns-notes/images/202412292320399.png)

##### 示例结构

![image-20241229232103411](./design-patterns-notes/images/202412292321492.png)

#### 拓展点

![image-20250108232951526](./design-patterns-notes/images/202501082329611.png)

![image-20241229232513570](./design-patterns-notes/images/202412292325640.png)

### 命令模式-Command

#### 结构

##### 基本结构

![image-20250119192849780](./design-patterns-notes/images/202501191928844.png)

![image-20250119202354542](./design-patterns-notes/images/202501192023618.png)

##### 示例结构

![image-20250119191742840](./design-patterns-notes/images/202501191917919.png)

### 解释器模式-Interpreter

#### 结构

##### 基本结构

![image-20250119212559801](./design-patterns-notes/images/202501192125896.png)

##### 示例结构

![image-20250119212845591](./design-patterns-notes/images/202501192128667.png)

##### 拓展点

![image-20250119212923828](./design-patterns-notes/images/202501192129954.png)
