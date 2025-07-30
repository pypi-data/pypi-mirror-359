def dataview():
    return """


## 意像


表头: dataview
### 全体笔记
```
TABLE 
```

### 查询特定的文档的列并排序
```
table topic, creation-date, type, tags, 编辑状态
from "工程系统级设计" 
sort type
```

### 条件查询
```
where contains(file.tags, "TODO")
```
### 多条件查询
```
table file.name as "文档名称"
from ""
where contains(file.outlinks, "TODO") && contains(file.outlinks, "Important")
sort file.name asc
```

未知
```
TABLE file.name AS "Filess", rating AS "Rating" FROM #编程环境   
```


未知2 表头为: dataviewjs
```
dv.taskList(dv.pages().file.tasks.where(t => !t.completed));
```


dataview
```
list from "工程技术/编程环境"
```

### 统治所有的任务
```
task from "工程技术"
```


"""


def set_date():
    return """
    // Date now 
    <% tp.date.now() %> 

    // Date now with format
    <% tp.date.now("Do MMMM YYYY") %>

    // Last week 
    <% tp.date.now("YYYY-MM-DD", -7) %>

    // Next week 
    <% tp.date.now("YYYY-MM-DD", 7) %> 

    // Last month 
    <% tp.date.now("YYYY-MM-DD", "P-1M") %>


    // 显示时分秒级别, 并可以控制前后时间  hh 是12小时制, HH 是24小时制
    <% tp.date.now("YYYY-MM-DD hh:mm:ss", '-01:02:11') %>

    <% tp.date.now("YYYY-MM-DD HH:mm:ss", '01:02:11') %>
    """


def network():
    return """
网络模块

每日一句
<% tp.web.daily_quote() %>

随机图片
<% tp.web.random_picture("200x200", "landscape,water") %>

网络请求
<% tp.web.request("https://jsonplaceholder.typicode.com/todos", "0.title") %>

"""

def user():
    return """


###


得到所有文件夹
<%
tp.app.vault.getAllLoadedFiles()
  .filter(x => x instanceof tp.obsidian.TFolder)
  .map(x => x.name)
%>

  
将HTML转化为markdown , 意味着可以使用html 的配置来美化页面

<% tp.obsidian.htmlToMarkdown("\<h1>Heading\</h1>\<p>Paragraph\</p>") %>


获取网络请求的响应

<%* const response = await tp.obsidian.requestUrl("https://jsonplaceholder.typicode.com/todos/1"); tR += response.json.title; %>


######



设置属性

```
---
alias: myfile
note type: seedling
categories: - book - movie 
---
file content
```


获取数据

```
File's metadata alias: <% tp.frontmatter.alias %>
Note's type: <% tp.frontmatter["note type"] %>
列表: <% tp.frontmatter.categories.map(prop => `  - "${prop}"`).join("\n") %>
```

"""



def files():
    return """

标题
<% tp.file.title %>

标签
<% tp.file.tags %>

重命名
<% await tp.file.rename("MyNewName") %>

相对/绝对路径
<% tp.file.path() %> # 绝对路径
<% tp.file.path(true) %> # 相对路径

文件移动
// File move <% await tp.file.move("/A/B/" + tp.file.title) %> 
// File move and rename <% await tp.file.move("/A/B/NewTitle") %>

文件最后修改日期
// File last modified date
<% tp.file.last_modified_date() %>
// File last modified date with format
<% tp.file.last_modified_date("dddd Do MMMM YYYY HH:mm") %>


"""