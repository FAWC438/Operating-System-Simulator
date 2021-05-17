// 用于记录当前打开的文件的路径
let current_opened_file_path = ''

// 用于记录当前聚焦的文件/文件夹的路径
let current_focused_file_path = ''

// 当前聚焦的文件类型 1 文件夹 2 文件
let current_focused_file_type = 0

// 当前聚焦的文件的选择器形式元素
let current_element = $('#root')

// 打开文件 elem 是选择器元素
function open_file(elem) {
    // 将其他打开的文件样式设为关闭的
    $('.fileOpened').attr('class', 'file')

    // 打开该文件
    elem.attr('class', 'fileOpened')

    let result = get_file_path(elem)
    // 将当前打开文件的路径重新设置
    current_opened_file_path = result
    current_element = $(this)
    change_focused_file(result, 2)

    // 获取的路径没问题 发送ajax请求
    $.ajax({
        type: 'POST',                                                               // 提交方式POST ajax 中 有6种提交方式
        url: '/readFile',                                                           // 提交目标地址
        data: {'filePath': result},                                                 // 提交的数据
        success: function(data) {                                                   // 成功提交以后的回调函数
            // 返回的data 就是文件内容(因为是按照图形化界面操作的，所以不会不存在)
            $('.fileBrief').text('文件名: ' + result + '文件内容: ')            // 更新显示的文件名
            $('.fileContext').val(data["data"])                                            // 更新显示文件内容

        }
    })
}

// 点击文件夹 elem 是选择器元素
function click_folder(elem) {
    let text = elem.text()
    let len = text.length
    text = text.substr(2, len)

    // 聚焦
    change_focused_file(get_file_path(elem), 1)
    current_element = elem

    // 非空文件夹
    if (elem.siblings('div').length > 0) {
        // 展开
        if (elem.siblings('div').is(':hidden')) {
            elem.siblings('div').show()
            elem.text('- ' + text)
        }

        // 折叠
        else {
            elem.siblings('div').hide()
            elem.text('+ ' + text)
        }
    }
    else {
        ;
    }
}

// 由于删除文件或初始状态导致焦点失去
function lose_focus() {
    $('.filePath').hide()
    $('.fileType').hide()
    $('.newFile').hide()
    $('.newFileButton').hide()
    $('.newFolderButton').hide()
    $('.reName').hide()
    $('.reNameButton').hide()
    $('.deleteButton').hide()
}

lose_focus()

// 改变选中的文件 文件路径  类型1 文件夹 2文件
function change_focused_file(file_path, type) {
    $('.filePath').text('文件路径: ' + file_path)
    if (1 === type) { // 文件夹
        current_focused_file_type = 1
        $('.fileType').text('文件类型: 文件夹')
        $('.newFile').show()
        $('.newFileButton').show()
        $('.newFolderButton').show()
    }
    else {
        current_focused_file_type = 2
        $('.fileType').text('文件类型: 文件')
        $('.newFile').hide()
        $('.newFileButton').hide()
        $('.newFolderButton').hide()
    }
    current_focused_file_path = file_path

    $('.filePath').show()
    $('.fileType').show()
    $('.reName').show()
    $('.reNameButton').show()
    $('.deleteButton').show()
}



// 获取 文件或是 文件夹路径
function get_file_path(elem) {
    let i = 0
    let pathArray = new Array()

    // 获取文件名
    if (elem.hasClass('folderTitle'))              // 文件夹
        ;
    else
        pathArray[i++] = elem.text().trim().replace(/\s/g, '')// 文件

    let parent = elem.parent()
    while (!parent.is('body')) {
        if (parent.hasClass('folder')) {  // 是文件夹
            pathArray[i++] = parent.children('button').text().replace(/[+-]\s/g, '')   // 过滤空白字符和+-提示符号
        }
        else { // 是文件
            pathArray[i++] = parent.text().trim().replace(/\s/g, '')                        // 过滤空白字符
        }
        parent = parent.parent()
    }
    let result = ''
    for (let j = i -1; j >= 0; j--)
        result += '/' + pathArray[j]

    return result
}


// 递归创建文件树的文件节点
function create_file_node(fileName) {
    let result = '<div class="file" onclick="open_file($(this))">' + fileName + '</div>'
    return result
}

// 递归创建文件树的文件夹节点
function create_folder_node(folderObj, folderName) {
    let preString = '<div class="folder"><button class="folderTitle" onclick="click_folder($(this))">  ' + folderName +
        '</button>'  // 前缀
    let result = ''                    // 内容 递归确定
    let postString = '</div>'          // 后缀
    for (let j in folderObj) {         // 遍历
        // folderObj[j] 是对象
        let memberObject = folderObj[j]
        for (let k in memberObject) {   // 属性值
            if (memberObject[k] instanceof Array)   {   // 文件夹
                result += create_folder_node(memberObject[k], k)
            }
            else // 文件
                result += create_file_node(k)
        }
    }
    return preString + result + postString
}

// 初始化 发送 初始化文件树请求 并 根据获取的数据初始化文件树
$.ajax({
    type: 'POST',                                                               // 提交方式POST ajax 中 有6种提交方式
    url: '/Initialize',                                                         // 提交目标地址
    data: {'flag': 'ok'},                                                       // 提交的数据
    success: function(data) {                                                   // 成功提交以后的回调函数
        let result = ''
        for (let obj in data) {                               // 自身编号
            // root 对象是 data[obj]
            let rootObject = data[obj]
            for (let members in rootObject) {                       // 成员对象
                let membersObject = rootObject[members]
                for (let values in membersObject) {                 // 成员对象编号
                    // membersObject[values]  成员对象值
                    if (membersObject[values] instanceof Array) {   // 该成员是数组(文件夹)
                        // alert('array ' + values)
                        result += create_folder_node(membersObject[values], values)
                        //alert(membersObject[values].length)
                    }
                    else {                                          // 文件
                        // alert('number ' + values)
                        result += create_file_node(values)
                    }
                }
            }
        }
        $('#root').append(result)
    }
})

// 修改文件按钮 -- 这个按钮现在功能比较鸡肋 按一下 编辑框就从只读的变成可以写的了
$('.alterFile').click(function () {
    $('.fileContext').removeAttr('readonly')
})

// 保存文件按钮 -- 点击后将文件路径和新的文件内容发送给后端时
$('.saveFile').click(function () {
    let text = $('.fileContext').val()       // 获取当前编辑的文件内容
    $.ajax({
        type: 'POST',
        url: '/writeFile',
        // filePath 文件完整路径及文件名  Content 文件内容
        data: {'filePath': current_opened_file_path, 'Content': text},
        success: function (data) {
            alert('保存文件成功')
        }
    })
})

// 删除文件/文件夹
$('.deleteButton').click(function () {
    // 在前端中删除
    if (current_element.hasClass('folderTitle'))
        current_element.parent().remove()
    else
        current_element.remove()
    lose_focus()

    // 发送 ajax 信息 告知后端
    $.ajax({
        type: 'POST',
        url: '/delFile',
        // filePath 被删除的文件的全名及路径
        data: {'filePath': current_opened_file_path},
        success: function (data) {
            alert('删除文件成功')
        }
    })

})

// 重命名
$('.reNameButton').click(function () {
    let newName = $('.reName').val()

    // 发送 ajax信息 告知后端
    $.ajax({
        type: 'POST',
        url: '/renameFile',
        // 第一个参数是被修改文件的完整路径+文件名 第二个参数是被修改文件的新文件名(不含文件名)
        data: {'filePath': current_opened_file_path, 'newName': newName},
        success: function (data) {
            if ('Success!' === data["message"]) {      // 允许修改
                current_element.text(newName)
                change_focused_file(get_file_path(current_element), current_focused_file_type)
                $('.reName').val('')

                alert('文件重命名成功')
            }
            else                     // 重名或其他因素导致不能修改
                alert('文件重命名失败')
        }
    })
})

// 新建文件
$('.newFileButton').click(function () {
    let fileName = $('.newFile').val()

    // 判空
    if ('' === fileName) {
        alert('文件名不能为空')
        return
    }

    // 发送ajax信息 告知后端
    $.ajax({
        type: 'POST',
        url: '/createFile',
        // 参数 创建的文件的完整路径+文件名
        data: {'filePath': $('.filePath').text().replace("文件路径:", "") + '/' + fileName},
        success: function (data) {
            if ('Success!' === data["message"]) {      // 允许创建 更新前端
                current_element.parent().append('<div class="file" onclick="open_file($(this))">' + fileName + '</div>')
                alert('文件创建成功')
            }
            else                     // 重名或其他因素导致不能修改
                alert('文件创建失败')
        }
    })
})

// 新建文件夹
$('.newFolderButton').click(function () {
    let folderName = $('.newFile').val()

    // 判空
    if ('' === folderName) {
        alert('文件夹名不能为空')
        return
    }

    // 发送ajax信息 告知后端
    $.ajax({
        type: 'POST',
        url: '/createFolder',
        // 参数 创建的文件的完整路径+文件名
        // data: {'filePath': current_opened_file_path + '/' + folderName},
        data: {'filePath': $('.filePath').text().replace("文件路径:", "") + '/' + folderName},
        success: function (data) {
            if ('Success!' === data['message']) {      // 允许创建 更新前端
                current_element.parent().append('<div class="folder"><button class="folderTitle" ' +
                    'onclick="click_folder($(this))">' + '  ' + folderName + '</button></div>')
                alert('文件夹创建成功')
            }
            else                     // 重名或其他因素导致不能修改
                alert('文件夹创建失败')
        }
    })
})
