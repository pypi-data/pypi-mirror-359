# 🚀 快速开始

欢迎使用 EmailWidget！这个部分将帮助你在几分钟内上手使用EmailWidget创建你的第一个专业邮件报告。

## 📋 学习路径

<div class="grid cards" markdown>

- :material-download: **[安装配置](installation.md)**
  
  ---
  
  安装EmailWidget并验证环境配置
  
  **时间**: 2分钟 • **难度**: ⭐

- :material-email-fast: **[第一个邮件](first-email.md)**
  
  ---
  
  创建你的第一个邮件报告
  
  **时间**: 5分钟 • **难度**: ⭐⭐

- :material-book-open: **[基本概念](concepts.md)**
  
  ---
  
  理解EmailWidget的核心概念
  
  **时间**: 10分钟 • **难度**: ⭐⭐

- :material-help-circle: **[常见问题](faq.md)**
  
  ---
  
  解决使用过程中的常见问题
  
  **时间**: 按需查阅 • **难度**: ⭐

</div>

## ⚡ 30秒体验

如果你想立即体验EmailWidget的强大功能，这里有一个最简单的例子：

```python
from email_widget import Email, TextWidget
from email_widget.enums import TextType

# 创建邮件
email = Email("我的第一份报告")

# 添加标题
email.add_widget(
    TextWidget()
    .set_content("欢迎使用 EmailWidget! 🎉")
    .set_type(TextType.TITLE_LARGE)
)

# 导出HTML文件
file_path = email.export_html("my_first_report.html")
print(f"报告已生成: {file_path}")
```

运行这个代码，你将得到一个美观的HTML邮件文件！

## 🎯 学习目标

通过快速开始部分的学习，你将能够：

- ✅ **安装和配置** EmailWidget环境
- ✅ **创建基础邮件** 包含文本、表格等内容
- ✅ **理解核心概念** Widget、Email类、配置系统
- ✅ **导出和使用** 生成的HTML邮件文件
- ✅ **解决常见问题** 字体、图表、兼容性等

## 🛠️ 准备工作

在开始之前，请确保你的环境满足以下要求：

!!! info "前置条件"
    
    - **Python 3.10+** - 检查版本: `python --version`
    - **pip** - Python包管理器
    - **基础Python知识** - 了解类、方法调用等概念
    - **文本编辑器** - VS Code、PyCharm等

## 📖 相关资源

除了快速开始，你可能还对这些内容感兴趣：

### 📚 深入学习
- [用户指南](../user-guide/index.md) - 详细的组件使用教程
- [API参考](../api/index.md) - 完整的API文档
- [示例代码](../examples/index.md) - 实际应用场景

### 🤝 获取帮助
- [GitHub Issues](https://github.com/271374667/SpiderDaily/issues) - 问题反馈
- [GitHub Discussions](https://github.com/271374667/SpiderDaily/discussions) - 社区讨论
- [Bilibili视频](https://space.bilibili.com/282527875) - 视频教程

### 🔧 开发相关
- [开发指南](../development/index.md) - 参与项目开发
- [贡献代码](../development/contributing.md) - 贡献代码指南

## 🚦 开始学习

准备好了吗？让我们从[安装配置](installation.md)开始你的EmailWidget之旅！

---

!!! tip "💡 小贴士"
    
    建议按照顺序学习各个章节，每个章节的知识都会在后续章节中用到。如果遇到问题，可以随时查阅[常见问题](faq.md)部分。 