Class_diagram = """

```mermaid
classDiagram
Class01 <|-- AveryLongClass : Cool
Class03 *-- Class04
Class05 o-- Class06
Class07 .. Class08
Class09 --> C2 : Where am i?
Class09 --* C3
Class09 --|> Class07
Class07 : equals()
Class07 : Object[] elementData
Class01 : size()
Class01 : int chimp
Class01 : int gorilla
Class08 <--> C2: Cool label

```

"""

EntityRelationshipDiagram  = """

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    CUSTOMER }|..|{ DELIVERY-ADDRESS : uses


```


"""

Flowchart = """
```mermaid
graph TD;
	A[12]
    A-->B;
    A-->C;
    B-->D;
    B-->C;
    C-->D;
    D-->A;

```
"""

Gantt = """

```mermaid
gantt
dateFormat  YYYY-MM-DD
title Adding GANTT diagram to mermaid
excludes weekdays 2014-01-10

section A section
Completed task            :done,    des1, 2014-01-06,2014-01-08
Active task               :active,  des2, 2014-01-09, 3d
Future task               :         des3, after des2, 5d
Future task2               :         des4, after des3, 5d

```

```mermaid
gantt
    title 基于MCP的Agent工作流开发施工图
    dateFormat  HH:mm

    section 环境搭建
    环境评估与选择    :done,    des1, 08:00, 09:00
    工具安装与配置    :active,  des2, 09:00, 10:00
    环境测试         :         des3, 10:00, 11:00

    section 代码实现
    用户输入模块     :active,  des4, 11:00, 12:00
    Agent初始化模块  :         des5, 12:00, 13:00
    意图解析模块     :         des6, 13:00, 14:00
    工具调用判断模块 :         des7, 14:00, 15:00
    MCP客户端模块    :         des8, 15:00, 16:00
    MCP服务器模块    :         des9, 16:00, 17:00
    结果返回模块     :         des10,17:00, 18:00
    响应生成模块     :         des11,18:00, 19:00

    section 测试与优化
    单元测试         :         des12,19:00, 20:00
    集成测试         :         des13,20:00, 21:00
    性能优化         :         des14,21:00, 22:00
    安全测试         :         des15,22:00, 23:00

    section 部署与交付
    部署准备         :         des16,23:00, 00:00
    上线部署         :         des17,00:00, 01:00
    文档编写         :         des18,01:00, 02:00
    交付与验收       :         des19,02:00, 03:00
```
"""

Gitgraph  = """
```mermaid
    gitGraph
       commit
       commit
       branch develop
       commit
       commit
       branch ww
       commit
       checkout main
       commit
       commit

```
"""

OpenEditor = """
"""

QuadrantChart = """
```mermaid
quadrantChart
    title Reach and engagement of campaigns
    x-axis Low Reach --> High Reach
    y-axis Low Engagement --> High Engagement
    quadrant-1 We should expand
    quadrant-2 Need to promote
    quadrant-3 Re-evaluate
    quadrant-4 May be improved
    Campaign A: [0.3, 0.6]
    Campaign B: [0.45, 0.23]
    Campaign C: [0.57, 0.69]
    Campaign D: [0.78, 0.34]
    Campaign E: [0.40, 0.34]
    Campaign F: [0.35, 0.78]

```
"""

Sequencediagram = """
```mermaid
sequenceDiagram
    participant Alice
    participant Bob
    Alice->>John: Hello John, how are you?
    loop HealthCheck
        John->>John: Fight against hypochondria
    end
    Note right of John: Rational thoughts <br/>prevail!
    John-->>Alice: Great!
    John->>Bob: How about you?
    Bob-->>John: Jolly good!

```
"""

UserJourneyDiagram = """
```mermaid
journey
    title My working day
    section Go to work
      Make tea: 5: Me
      Go upstairs: 3: Me
      Do work: 1: Me, Cat
    section Go home
      Go downstairs: 5: Me
      Sit down: 5: Me

```
"""

XYChart = """
```mermaid
xychart-beta
    title "Sales Revenue"
    x-axis [jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec]
    y-axis "Revenue (in $)" 4000 --> 11000
    bar [5000, 6000, 7500, 8200, 9500, 10500, 11000, 10200, 9200, 8500, 7000, 6000]
    line [5000, 6000, 7500, 8200, 9500, 10500, 11000, 10200, 9200, 8500, 7000, 6000]

```
"""




from enum import Enum

class Mermaid(Enum):
    XYChart = XYChart
    EntityRelationshipDiagram = EntityRelationshipDiagram
    UserJourneyDiagram = UserJourneyDiagram
    Sequencediagram =Sequencediagram
    QuadrantChart = QuadrantChart
    Class_diagram = Class_diagram
    OpenEditor = OpenEditor
    Flowchart = Flowchart
    Gitgraph = Gitgraph
    Gantt = Gantt
    