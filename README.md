# docPy
基于python3x的文档自动生成工具
> 该README文档由批处理解析器自动生成

# 概念

应用docPy前应该了解的几个概念

## 1. 文档节点对象
 
 将文档中的所有有效注释（多行注释）抽象为一个文档节点对象。在解析文档时候，用正则匹配出注释并产生一个文档节点对象。一个文档节点对象可以是一个项目的注释/一个模块的注释/一个类的注释/一个函数的注释/一个变量的注释。如，在c++中，下面的代码注释了一个类。
 ```
  /*
   &: class ClassObject
   $: 一个示例类
   LK: Module
  */ 
  class ClassObject : public Object
  {
   ...
  }
 
 ```
 
 在该注释中，符号`&`定义了一个类文档对象，`$`定义了对该类的注释内容，`LK`定义了该文档对象的链接性（LK是Link的缩写，指链接到Module模块）。在docPy的语法中，上面的代码将会产生一个类节点对象，并在functional.py的类中完成对它的连接。
 
 那什么是链接性。打个比方，一个类cls的成员变量var只能出现在cls类的定义域以内，那么这个成员变量var就会链接到类cls。而类只能定义在某个模块mod内，如果cls属于mod模块那么，cls就连接到mod，但cls的成员变量var不能连接到mod，这一点是不言而喻的。之所以定义链接性，其目的有二
 
 1. 也是重要的一点是，在写代码时，必须模块分明，条例清晰，在定义类的时候一定要搞清楚类的作用和从属的模块
 2. 在生成.md或者和.html文件时，可以很方便的产生层级分明的文档（比如该readme.md文档）
 
## 2. 文档节点对象关系
 在解析完文档后，每个文档节点对象都是孤立的并未产生关系，只有在经过连接之后，才能生成文档节点树，其根节点是一个ProjectObject，第二层是ModuleObject，第三层是模块级的变量/函数/类，第四层是成员变量/方法（如前暂不支持内嵌类）。
 
 在建立连接时，可以显式的使用`LK`或者`M`来指定连接的对象，当在同一文件内已定义过模块对象后，可以省略链接关键字。每个文档节点对象由*注释文档对象*产生。每个注释文档对象必须定义其完整性。例如，一个函数必须由函数名，和对该函数的解释（毕竟是文档嘛），那么如果在解析过程中，发现了一个函数注释文档对象，而没有匹配到函数名时，程序就会报错，它不满足函数注释文档对象的完整性。如下Python代码
 ```
  """
   @: Foo
   >: (int) in_1 : Foo函数的第一个输入参数，类型为int，名称为in_1
   >: (dobule) in_2: Foo函数的第二个参数，类型为double，名称为in_2
   <: (bool)
   $: 对Foo函数的描述
   M: ClassOfFoo
  """
 ```
 
使用关键字`@`定义了一个函数节点对象，使用`>`定义了两个输入参数，用`<`定义了一个返回类型，`$`定义了对`Foo`的描述信息，`M`定义了该方法属于`ClassOfFoo`类。不过，当一个函数没有输入参数和返回值（void)时，而且之前已经定义过该方法的类，那么以上代码可以简写为
 ```
  """
   @: Foo
   $: 对Foo函数的描述
  """
 ```

每个注释文档对象都必须有`name`和`desc`，即名称和描述信息。

在建立隐式链接时，所连接到的父节点必须只有一个，且在之前已定义。显式连接则可以指定多个父节点，并且父节点不一定在之前就已定义。

# Usage

## 文档节点对象和注释文档节点对象（BasedObjec CommentBlock）

凡是定义这两类的对象必须继承该两个父类，如果你向自定义自己的文档对象和注释文档对象，具体内容可查看下面文档

## 项目文档节点和项目注释文档节点（ProjectObject ProjectBlock）

### ProjectBlock

#### 完整性：`name`/`desc`

#### 链接性: 根节点

#### 语法(注释符号以c++为例)

```
 /*
  Pj: [ProjName]
  $: [descripation of ProjName]
 */
```
#### Note: 目前仅支持在一个文档目录中定义一个Porject

## 模块文档节点对象和模块注释文档节点对象(HaveRefsModuleObject ModuleObject LazyModuleBlcok)

### LazyModuleBlcok

#### 完整性：`name`/`desc`

#### 可选注释：`LK`

#### 链接性：-> ProjectObject

#### 语法(注释符号以c++为例)

```
 /*
  !: [ModName]
  $: [descripation of ProjName]
  LK: [parent[,...]]
 */
```

## 模块变量文档节点对象和模块变量注释文档节点对象(ModuleVariableObject LazyVariableBlock)

### LazyVariableBlock

#### 完整性：`name`/`desc`/`type`

#### 可选注释：`LK`

#### 链接性：-> ModuleObject

#### 语法(注释符号以c++为例)

```
 /*
  Var: ([type]) [VarName]
  $: [descripation of VarName]
  LK: [parents[,...]]
 */
```
## 模块函数文档节点对象和模块函数注释文档节点对象(ModuleFunctionObject LazyFunctionBlock)

### LazyFunctionBlock

#### 完整性：`name`/`desc`

#### 可选注释：`LK`/`>`/`<`

#### 链接性：-> ModuleObject

#### 语法(注释符号以c++为例)

```
 /*
  @: [FunctionaName]
  >: ([type]) [name] : [desc of input param]
  ...
  <: ([type])
  $: [descripation of FunctionaName]
  LK: [parents[,...]]
 */
```

## 类文档节点对象和类注释文档节点对象(ClassObject LazyClassBlock)

### LazyClassnBlock

#### 完整性：`name`/`desc`

#### 可选注释：`LK`

#### 链接性：-> ModuleObject

#### 语法(注释符号以c++为例)

```
 /*
  &: class [ClassName]
  $: [descripation of ClassName]
  LK: [parents[,...]]
 */
```

## 类方法文档节点对象和类方法注释文档节点对象(MethodObject LazyMethodBlock)

### LazyMethodBlock

#### 完整性：`name`/`desc`

#### 可选注释：`M`

#### 链接性：-> ClassObject

#### 语法(注释符号以c++为例)

```
 /*
  @: [methodName]
  $: [descripation of methodName]
  M: [parents[,...]]
 */
```

## 类变量文档节点对象和类变量注释文档节点对象(MemberVariableObject LazyMemberVariableBlock)

### LazyMemberVariableBlock

#### 完整性：`name`/`desc`/`type`

#### 可选注释：`M`

#### 链接性：-> ClassObject

#### 语法(注释符号以c++为例)

```
 /*
  Var:([type]) [VarName]
  $: [descripation of VarName]
  M: [parents[,...]]
 */
```



# Module DocObject

 定义文档节点对象，从注释块对象中生成一个指定的文档节点 该节点将用于*1.产生链接特性 2.方便functional.report()函数访问文档的所有节点*

------

## Class BasedObject

 抽象基类，所有节点对象都继承自它

------

### Var name  (*type*=str)

 文档节点的名称，如一个类名或者一个模块名

### Var desc  (*type*=str)

对该节点的描述，也就是注释内容

### Var linked_to  (*type*=str|list)

 该节点所指向的父节点，根据子类的不同而类型不同 一个类域下的所有节点的linked_to均未该类的名字，一个Project或者Module下的 节点均未列表

### method  add_parent()

param **parent** (*type=*subClassOfBaseObject)

> 该节点链接到的对象

 *该类不直接提供给外部使用，仅在add_child中使用，add_child为对外提供的接口*如果重复父亲添加子，子添加父亲，则会导致关系冗余。

### method  add_child()

param **child** (*type=*subClassOfBaseObject)

> 指向该类的子节点

 提供给functional中的函数使用，用于添加链接

## Class Scoped

 定义域对象，提供给*Lazy*对象继承

------

### Var priority  (*type*=int)

 在域栈中的优先级，根据该数值的大小进行入栈出栈操作

### method  init()

构造器

### method  __eq__()

 注意！定义了\_\_eq__的将不再是hashable的对象了，如果想要实现hashable需要继承父类的__hash__对象

### method  __gt__()



### method  __lt__()



### method  __le__()



### method  __ge__()



## Class ScopedObject

 在对一个源码文档进行扫描搜索时，随着扫描的进行，指针会不时地进入和退出一个特点的区域，例如在处理一个类方法时，指针在一个类的域中；处理一个模块时，指针处在一个项目域中。ScopedObject对这种行为进行了抽象，在解析文档时，有且仅有一个全域，即ScopedObject自身。当开始扫描文档时，该类自举，将self压入栈内，当扫描完退出文档时，该域对象弹出域栈。在扫描期间，每进入一个域，则入栈该域对象；退出该域时，弹出域栈，直到遇到第一个优先级更大的域对象时，停止弹栈。此时栈顶就为当前域。从广义上将每个文档对象都应当有自己的域，但是在源码文档中，有”域“这个概念的就仅有Project/Module/Class三个文档节点对象，因此每当进入这三者其一时，域对象需要表现为一个文档节点对象的代理，通过该代理进行操作，实现了解耦，使得无需再修改functional的代码。它分别继承BaseObject和Scoped类

------

### Var _proxy  (*type*=subClassOf[Scoped])

 域对象的代理

### Var _stack  (*type*=list[stack])

域栈

### method  init()



### method  __del__()

析构函数，由于再构造时会将self压入栈内，而且其优先级最高，所以再程序中无法弹出栈底元素(self)，所以再析构时，应该将其弹出，这样对该域对象(self)的引用计数就会安全的降为0，否则可能在内存中一直保存(不过肯能在_stack析构之后，该对象的引用计数也会安全降为0)

### method  change_scope()

 当要切换域对象时，函数将要比对当前域（栈顶元素）与将要切换到的域对象的优先级 当遇到域优先级更大的域对象时，需要弹出栈顶元素直到遇到比obj域范围更大的对象为止 然后将其压栈；否则直接压栈，表示进入了更小的域范围

### method  get_background()

 当在同优先级域对象之间切换时，如果不进行退栈处理，那么诸如 `self.scope.add_child(obj) - self.scope.proxy(obj)`着用的用法就会出错，由于代理对象未修改 而往一个代理对象上添加一个相同优先级的对象显然是不对的（如当前代理对象和obj均为ClassObject，那么在第一句中 add_child()就会抛出一个ValueError错误。因此，在同优先级的域对象之间相互切换应该找到背景域（当前代理对象的父节点）

### method  top()

返回栈顶元素

### method  proxy()

提供给外部的接口用于设置域代理对象

### method  add_child()

 *act-like-a-BaseObject*，实现对文档节点对象的代理功能

### method  add_parent()

 *act-like-a-BaseObject*，实现对文档节点对象的代理功能

## Class ReferencedObject

 引用模块类

------

### Var linked_to  (*type*=list[str])

 父文档节点

### Var refs  (*type*=list[str])

该文档所有引用到的模块名

### method  init()

param **name** (*type=*str)

> the name of obejct



### method  add_parent()



### method  add_child()

引用节点暂时无子节点

## Class ProjectObject

 项目文档节点类，是一个Scoped

------

### Var modules  (*type*=list[ModuleObject|HaveRefsModuleObject])

 ProjectObject所有子节点

### method  add_parent()

目前项目节点为根节点，再无父节点

### method  add_child()

 添加子节点，应该均为模块

## Class ModuleObject

 模块文档节点对象， 是一个Scoped

------

### Var classes  (*type*=list[ClassObject])

 保存该模块下所有类文档节点对象

### Var variables  (*type*=list[VariableObject])

 保存该模块下所有变量文档节点对象

### Var functions  (*type*=list[FunctionObject])

 保存该模块下所有函数文档节点对象，包括类方法

### Var linked_to  (*type*=list[Object])

 所有父节点，是一个列表，也即一个类可以链接到多个模块

### method  init()



### method  add_parent()

param **parent** (*type=*BasedObject)

> ；链接到的父节点



### method  add_child()



## Class HaveRefsModuleObject

 有引用的模块的文档对象，这是一个包装类

------

### Var references  (*type*=list)

所有引用

### method  init()



### method  add_child()

param **child** (*type=*ReferencedObject)

> 



## Class ClassObject

类文档节点对象

------

### Var methods  (*type*=list[ClassMethodObject])

保存该类下所有方法

### Var variables  (*type*=list[MemberVariableObject])

保存该类下所有成员变量

### Var linked_to  (*type*=list)

所有父节点，为列表，也即一类可以定义再多个模块下

### method  add_parent()

param **parent** (*type=*ModuleObject)

> 



### method  add_child()



## Class VariableObject

 变量节点对象，抽象基类

------

### Var type  (*type*=str[AnyType])

变量类型

### method  init()



### method  add_child()

变量对象无子节点

## Class MemberVariableObject

 成员变量文档节点对象，特化VariableObject

------

### Var linked_to  (*type*=ClassObject)

为单个类对象

### method  init()



### method  add_parent()

param **parent** (*type=*ClassObject)

> 



## Class ModuleVariableObject

 模块变量文档节点对象，变量对象的特化

------

### Var linked_to  (*type*=list[ModuleObject])

为列表，也即一个模块变量可以定义在多个模块中

### method  init()



### method  add_parent()

param **parent** (*type=*ModuleObject)

> 



## Class FunctionObject

 函数文档节点对象，抽象基类

------

### Var in_param  (*type*=list[tuple])

输入参数列表，每个元素为一个元组；元组的第一个为参数类型，第二个为参数名，第三个为表里的描述信息

### Var out_type  (*type*=str[AnyType])

函数的返回值类型

### method  init()



### method  add_child()

函数对象无子节点

## Class ModuleFunctionObject

 模块函数文档节点对象，FunctionObject的特化

------

### Var linked_to  (*type*=list[ModuleObject])

为列表，也即一个模块函数可以定义在多个模块中

### method  init()



### method  add_parent()

param **parent** (*type=*ModuleObject)

> 



## Class ClassMethodObject

 类方法文档节点对象，FunctionObject的特化

------

### Var linked_to  (*type*=str)

为单个类节点对象

### method  init()



### method  add_parent()

param **parent** (*type=*ClassObject)

> 



# Module comments

 对文档注释的抽象，定义不同注释类型所对应的类别/定义不同类别 的注释的提取规则(正则）。如果需要添加新的注释类别，并且该类有除了name和desc以外的 其它属性字段，那么需要在新的类里对pattern字典进行更新，添加提取规则(re.compile)。 目前，ProjectObject是一个文档对象的根节点。更广泛的推广，根节点类型只能有一个。 每个ModuleObject必须从属于一个ProjectObject/一个ClassObject必须从属于一个ModuleObject 进而类推。这样可以建立起文档关系链接树。因此根节点类型不能处理链接（因为它没有父节点），从而 必须其pipeline必须不能处理_parse_link()。链接的创建定义在functional模块中，文档节点对象定义在codeObject模块中. 模块采用工厂模式，通过BlockFactory类向用户提供接口

------

## Ref

 re, logging, abc, codeObject

## Class CommentBlock

 抽象基类，所有注释块对象均继承自CommentBlock 子类中需要实现pipeline()函数, getObject()函数和_parse_name()函数

------

### Var chunk  (*type*=str)

 保存注释内容

### Var name  (*type*=str)

 从注释内容中解析出注释名

### Var desc  (*type*=ste)

 注释内容的描述部分，用于解释说明该对象的用途

### Var link_type  (*type*=str)

 链接的类型，目前只定义了两类链接，一类是LK类型，指该对象链接到模块(ModuleObject)或这项目(ProjectObject) 第二类是M类型，指该对象链接到类(ClassObject)

### Var link  (*type*=str)

 从注释内容中提取的链接到对象字符串，对该字符串的链接解析工作则有functional定义

### Var pattern  (*type*=dict[str:re.compile])

 提取规则，在子类中通过update方法拓展

### method  init()

param **comment** (*type=*str)

> 注释内容

 构造器

### method  _findall()

param **key** (*type=*str)

> 需要提取对象的提取规则，必须在pattern中，否则引发KeyError

param **do** (*type=*callable)

> 定义提取动作，一般是赋值或者列表拓展动作

 对re.findall的封装，根据提取规则key从chunk中提取目标内容，如果没有找到任何内容 会引发IndexError错误

### method  _parse_desc()

 因为desc的格式在每个注释块中的格式统一，因此该函数不可重写，除非重新定义一种desc格式

### method  _parse_name()

 由于子类的name格式不统一，因此子类必须在pattern中重新定义自己name的提取规则， 但提取name的行为一致，所以该类也不用在子类中重写

### method  pipeline()

 对所有需要从注释块中提取的字段进行批处理，由于每个子类的字段不同，在子类中必须重写该函数

### method  _parse_link()

 解析链接类型和链接到字符串

### method  getObject()

 从已提取的字段中生成对应的文档节点对象

## Class ClassBlock

 定义如何从注释中提取一个类的所有信息

------

### method  init()

param **comment** (*type=*str)

> 待提取注释

构造器

### method  pipeline()

仅处理类名的提取

### method  getObject()

 从注释中提取一个ClassObject对象

## Class FunctionBlock

 定义如何从注释中提取一个函数的所有信息

------

### Var ins  (*type*=tuple[type, name, desc])

 函数的输入参数，为一个元组，元组第一个元素为参数类型，第二元素为参数名，第三个元素为参数的描述

### Var out  (*type*=str[AnyType])

 函数的返回值，可以为任意类型，用一个str表示返回值的类型

### method  init()

param **comment** (*type=*str)

> 待提取注释

构造器

### method  _parse_name()



### method  __parse_ins()



### method  __parse_out()



### method  pipeline()



### method  getObject()

由于一个函数可以是一个模块内定义的模块级函数，也可以是一个类中定义的方法所以根据链接类型的不同，返回不同的FunctionObject.当链接到模块时，返回一个 ModuleFunctionObject；如果链接到类，则返回一个ClassMethodObject，二者同继承自FunctionObject

## Class ModuleBlock

 定义如何从注释中提取一个模块类的所有信息

------

### method  init()

param **comment** (*type=*str)

> 待提取注释

构造器

### method  pipeline()

 仅提取模块名

### method  getObject()

返回一个HaveRefsModuleObject对象

## Class VariableBlock

 定义如何从注释中提取一个变量类的所有信息

------

### Var type  (*type*=str[AnyType])

 变量的类型

### method  init()

param **comment** (*type=*str)

> 待提取注释

构造器

### method  _parse_type()

解析变量类型

### method  pipeline()



### method  getObject()

 根据链接性不同返回一个VariableObject的子类。当链接到模块时返回一个ModuleVariableObject对象 当链接到类时，返回一个MemberVariableObject对象

## Class ReferencedBlock

 定义如何从注释中提取一个依赖类的所有信息

------

### Var referenced  (*type*=list[str])

 该模块所依赖的所有对象

### method  init()

param **comment** (*type=*str)

> 待提取注释

构造器

### method  _parse_name()

 引用在一个模块中仅有一个，因此name未固定'Ref'

### method  _parse_desc()

 引用的desc未固定的'references'

### method  _parse_ref()

 从注释中提取出所有依赖

### method  pipeline()

 

### method  getObject()

 未完成，如何实现单例模式

## Class ProjectBlock

 定义如何从注释中提取一个项目类的所有信息

------

### method  init()

构造器

### method  pipeline()



### method  getObject()

 根据提取出的信息返回一个ProjectObject对象

## Class BlockFactory

 一个工厂模式，提供用户接口， 例如在代码中 `factory = BlockFactory(); factory.create_bobj_by_name('name')` 该类产生的对象将会被用在functional中实现链接

------

# Module functional

 模块的主要任务用来解决依赖关系实现对文档节点的链接，其次将链接好的文档节点 转换为指定的格式（如.md/.html等）。

------

## Ref

threading.Lock,comments.commentGenerator,ScopedObject

## Class AbstractSignalFunctional

 实现链接。把在解析文档的时候产生的注释对象节点按照其指定的链接规则链接起来，链接有两个 第一种是M类链接，它表示为将该节点链接到类节点对象，因此只能够将函数和变量定义给该链接类型 第二中是LK类链接，它表示将该节点链接到模块或者项目对象节点，因此可以定义给任意节点类型定义该链接 当然这是链接的内部实现，在使用时可以不用显式的定义LK或者M，但是当该节点对象需要链接到多个 父节点时，需要显示地标出LK。函数lazy_link()实现了隐式链接

------

### Var _unresolved_relations  (*type*=dict[str:BaseObject])

 存放未解决的关系

### Var _obj_set  (*type*=dict[str:BaseObject])

 存放文档的所有文档节点对象

### Var scope  (*type*=ScopedObject)

 每个项目项目仅有一个scope，随着注释的解析，每进入一个Scoped对象 scope就会将其进行代理，并将其压入scope的对象栈。具体参看codeObject/Scoped对象的实现

### method  init()

 构造器

### method  links()

param **tgt** (*type=*subClassOfBaseObject)

> 需要链接的对象

 link()的具体实现，在当前已经解析的所有文档对象_obj_set中依次查找 每个parent，如果找到则将tgt链接到_obj_set[parent]，否则将tgt加入的 _unresolved_relations中。

### method  link2()

 在解析完一个源码文件后对所有未解决的关系进行再一次链接 如果没有发现待解决的关系，将会报错

### method  link()

 从注释块对象bobj中获取一个BaseObject对象，并链接。是对\_\_link()的包装

### method  lazy_link()

param **bobj** (*type=*subClassOfCommentBlock)

> 文档注释对象

 对link()的包装。需要强调的一点是，由于scope对象在构造时使用自己自举 因此在解析文档时，如果不定义Pj/Module或者Class，而直接定义函数或者变量 那么会在解析第一个文档注释的时候进入第一个判断块，而此时scope的当前域为其自身（一个ScopedObject对象） 必然会引起错误。因此，在编写代码时，必须有项目有模块，结构逻辑清晰

### method  dump()

param **info** (*type=*str)

> 需要保存的信息

param **path** (*type=*path)

> 保存地点

 该方法放在这里意义不明确，待改进

### method  report()

 对所有产生的文档对象和链接进行报道，子类通过重写该方法实现 转换到指定文档格式的任务

## Class SynSignalFunctional

 提供写保护，但似乎没啥卵用

------

### Var file_lock  (*type*=threading.Lock)

提供对文件的互斥访问锁

### method  dump()

param **info** (*type=*str)

> 要输出到文件的信息

param **path** (*type=*str)

> 输出路径



## Class ReportSignalFunctional

 提供print风格的简单解析结果的报表格式类

------

## Class ToMarkdownSignalFunctional

 转换到markdown格式

------

# Module Loader

 定义加载器

------

## Ref

 os,re,logging,threading,SingleFileLoader,FileLoader

## Class MultipleFileLoader

 多文件加载器，仅处理一个目录下的所有文件，将所有文件加载 进入_loaded_file中，并进行分页。打开文件读操作使用匿名的线程处理

------

### Var path  (*type*=str)

 保存文档路径

### Var _loaded_file  (*type*=list[SingleFileLoader])

 保存_files_lib_path下所有文件的文件加载器

### method  init()

param **path** (*type=*str)

> 文档目录

构造器

### method  set_attr_by_path()

设置_files_lib_path属性，由于本人最早开始写该类并在此之前一直在用Java所以免不了有些Java的'不良习惯'，忍着吧

### method  load()

 加载文件进入内存，并启动加载线程

## Class MultipleDirsLoader

 递归查询整个目录并将文档加载进入内存

------

### method  load()

对函数load_recursion的包装

### method  __load_recursion()

param **_path** (*type=*str)

> 递归路径

递归查找路径下的所有文档，并加载进入内存，起始路径未_files_lib_path通过包装器load传入启动递归

## Class FileLoader

 抽象基类，定义一些函数, SingleFileLoad/MultipleFileLoader/MultipleDirsLoader均继承自它

------

## Class SingleFileLoader

 加载单个文件进入内存，并分页

------

### Var _file_path  (*type*=str)

文件路径

### Var _file_format  (*type*=str)

文件格式

### Var _file_name  (*type*=str)

文件名

### Var chunk  (*type*=str)

读入的文件内容缓冲区

### Var limitation  (*type*=str)

单页面的大小限制

### Var pages  (*type*=str)

 分页存储

### method  init()

param **limit** (*type=*int)

> 定义一个页面大小，默认未5KB

构造器

### method  set_attr_by_path()

param **path** (*type=*str)

> 文件路径

set方法

### method  set_attr()

param **path** (*type=*str)

> 文件路径

param **name** (*type=*str)

> 文件名

param **format** (*type=*str)

> 文件格式

set方法

### method  load()

加载单个文件进入你日常并分页

# Module Parser

该模块定义解析器

------

## Ref

rReportSignalFunctional, AbstractSignalFunctional,BlockFactory,multipleLoader,SingleLoader

## Class AbstractParser

 定义解析从指定文件中读取出来的块的行为，是一个抽象基类 目前出现的问题在于是否得把对文件注释块的解析工作交给FileLoader，因为在定义了CommentBlock之后 原本AbstractParser的解析工作突然全部抽象出来并移交给CommentBlock的pipeline函数和getObject函数

------

### Var _before  (*type*=str)

 注释开始符

### Var _after  (*type*=str)

 注释结束符

### Var _comment_list  (*type*=list)

 存放一整个注释块容器

### Var _comment_pattern  (*type*=re.compile)

 从文档流中提取注释块

### Var iter_of_comment  (*type*=iter)

 _comment_pattern的迭代器

### method  __init__()

param **after** (*type=*str)

> 注释后符号

param **before** (*type=*str)

> 注释前符号

param **path** (*type=*str)

> 需要加载的文档，批处理类为目录

param **mapper** (*type=*AbstractSignalFunctional)

> 默认使用ReportSignalFunctional,指定符号与CommentBlock的映射关系。该类使用工厂模式产生CommentBlock对象

param **loader** (*type=*FileLoader)

> 文件加载器，默认使用SingleFileLoader，批处理类使用MultipleFileLoader

 构造函数，必须的参数为after和before

### method  pre_symmetric_check()

param **page_content** (*type=*str)

> 注释内容

 对偶性检查，对_comment_list的每一块注释进行注释符号对偶检查 如果对称，那么返回True，parse_comment()函数将不再会检查下一条注释块的结束注释符号 否则返回False，parse_comment()函数就会进一步在下下面若干条注释块中查找结束注释符号 如果SingleFileLoader的limitation设置的足够大，足以容纳下文档中的最大注释块的大小，那么 只要编译器通过，则注释符号一定对称

### method  _safe_suffix()

param **who** (*type=*SingleFileLoader)

> 指定需要检查行结束安全性的对象

param **after** (*type=*str)

> 注释结束符

 当在_comment_list中的一个注释块结束时，由于FileLoader会分页，因此有可能块与块之间 隔断了一个完整的注释符号，因此要确保在每一页的最后有一个完整的注释符。函数总是检查结束符号， 这是由于在parse_comment中，函数不论注释符是否对称，都会用正则匹配一次，因此，经过正则匹配， 在该注释块中，总是第一个出现注释起始符。如果出现截断，那么函数会将下一块被截断的注释结束符 复制到上一块中，并删除掉下一行被截断的结束符

### method  parse_comments()

param **who** (*type=*FileLoader)

> 指定需要解析的对象

 将分页的注释块根据注释开始和结束符组合成一个完整的注释段，该函数在批处理类中重写

### method  parse_comment()

param **v** (*type=*void)

> 

 将分页的注释块根据注释开始和结束符组合成一个完整的注释段，parse_comments的一个包装器

### method  __get_next_comment()

param **v** (*type=*void)

> 

 从iter_of_comment迭代器中获取下一条注释块

### method  __prefix_standard()

param **comment** (*type=*str)

> 注释块

 从注释块comment中提取在CommentBlock的工程类中已定义的块前缀，如类&/函数@等

### method  resolve_unlinked()

param **v** (*type=*void)

> 

解决所有在处理单个文件时没出解决的链接，如果在处理完所有目标文件时没有发现需要链接的对象，则会报错

### method  switch()

param **v** (*type=*void)

> 

 从所有注释块中取出每个注释块，获取其前缀以从CommentBlock生成已定义的Block对象。 在生成指定的注释对象后，块对象会解析该注释块并产生一个Object.之后，函数将会第一次 尝试解决该Object的链接性，如果暂时没有解析则会等到处理完所有comment之后再次尝试 解决

### method  run()

param **v** (*type=*void)

> 

 用户接口，在使用类时，直接使用该函数即可产生所有对象

## Class BADiffCommentParser

 注释结束符和开始符不同的文档类型（如cpp,html)处理器 由于前后符号不同，处理方法相对简单，速读更快

------

### method  init()

param **args** (*type=*tuple)

> 位置参数

param **kwargs** (*type=*dict)

> 关键字参数

 构造器，其必须参数同AbstractParser

### method  __gleft__()

param **ps** (*type=*str)

> 注释内容

 找到一个注释块的所有注释开始符位置

### method  __gright__()

param **ps** (*type=*str)

> 注释内容

 找到一个注释块的所有注释结束符位置

### method  pre_symmetric_check()

param **page_content** (*type=*str)

> 同AbstractParser

 对偶检查的具体实现，该函数冗余，应当定义在AbstractParser中 

## Class GCommentParser

 通用注释解析器，不论注释结束和开始符是否相同都可以使用该类进行解析. 如果开始和结束符相同，则在类构造时会给开始符和结束符添加区分符，实现隐型替换 如果不同，则表现为BADiffCommentParser

------

### Var _org_ab  (*type*=str)

 未添加区分符的原始注释开始结束符

### method  init()

param **args** (*type=*tuple)

> 位置参数

param **kwargs** (*type=*dict)

> 关键字参数

构造器，必须参数同AbstractParser

### method  __differ()

param **who** (*type=*SingleFileLoader)

> 为了能够尽量通用化__differ函数，指定who为一个单文件加载

 对所有以确保安全的注释块添加区分符

## Class BatchDirParser

 批处理处理器，加载一个目录下的所有文件，一般不直接使用 而是使用其特化的子类，如专门批处理c++或者python源码的批处理器。它的FileLoader 是MultipleFileLoader。

------

### method  init()

构造器，必须参数同AbstractParser

### method  parse_comment()

 对AbstractParser.parse_comment的重写。对每个加载进入内存的文件对象(SingleFileLoader) 进行提取注释操作

## Class CppBatchDirParser

 c++源码批处理文档生成器，特化了注释起始和结束符为/* */

------

## Class HtmlBatchDirParser

 html源码批处理文档生成器，特化了注释起始和结束符<!-- -->

------

## Class PythonBatchDirParser

 python源码批处理文档生成器，特化了注释起始和结束符

------

## Class CppParser

 c++单源码文档处理器，用于解析单个c++源码文档

------

### method  init()

param **path** (*type=*str)

> 源码文档路径

param **mapper** (*type=*AbstractSignalFunctional)

> 匹配器，默认为报表匹配器*ReportSignalFunctional*，可以自定义匹配器，目前提供了转为Markdown格式的ToMarkdownSignalFunctional匹配器

param **loader** (*type=*FileLoader)

> 文档加载器，默认为SingleFileLoader

 构造器

## Class PyParser

 Python单源码文档处理器，用于解析单个Python源码文档

------

### method  init()

param **path** (*type=*str)

> 源码文档路径

param **mapper** (*type=*AbstractSignalFunctional)

> 匹配器，默认为报表匹配器*ReportSignalFunctional*，可以自定义匹配器，目前提供了转为Markdown格式的ToMarkdownSignalFunctional匹配器

param **loader** (*type=*FileLoader)

> 文档加载器，默认为SingleFileLoader

 构造器

## Class HtmlParser

 Html单源码文档处理器，用于解析单个Html源码文档

------

### method  init()

param **path** (*type=*str)

> 源码文档路径

param **mapper** (*type=*AbstractSignalFunctional)

> 匹配器，默认为报表匹配器*ReportSignalFunctional*，可以自定义匹配器，目前提供了转为Markdown格式的ToMarkdownSignalFunctional匹配器

param **loader** (*type=*FileLoader)

> 文档加载器，默认为SingleFileLoader

 构造器

