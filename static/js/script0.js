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
    current_element = elem
    change_focused_file(result, 2)


    // 获取的路径没问题 发送ajax请求
    $.ajax({
        type: 'POST',                                                               // 提交方式POST ajax 中 有6种提交方式
        url: '/readFile',                                                           // 提交目标地址
        data: {'filePath': result},                                                 // 提交的数据
        success: function(data) {                                                   // 成功提交以后的回调函数
            // 返回的data 就是文件内容(因为是按照图形化界面操作的，所以不会不存在)
            $('.fileBrief').text('文件名: ' + result + '文件内容: ')             // 更新显示的文件名
            $('.fileContext').val(data['data'])                                    // 更新显示文件内容

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
    while (!parent.hasClass('fileSystem')) {
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
        data: {'filePath': $('.filePath').text().replace("文件路径:", ""), 'Content': text},
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
        data: {'filePath': $('.filePath').text().replace("文件路径:", ""), 'newName': newName},
        success: function (data) {
            if ('Success!' === data['message']) {      // 允许修改
                if (1 === current_focused_file_type)
                    current_element.text('  ' + newName)
                else
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
            if ('Success!' === data['message']) {      // 允许创建 更新前端
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

// 系统时钟设定函数 (定时请求)
let system_clock = 0   // 单击测试时钟变量值
// 更新系统时间
function update_system_clock() {
    $.ajax({
        type: 'POST',
        url: '/updateSystemClock',
        // 无参数
        data: {'clock': system_clock},
        success: function (data) {
            // 更新系统时间
            $('.systemClock').text('系统时间: ' + system_clock)

            // 更新进程队列
            update_process_queue(data['queueInfo'])
        }
    })

    // 循环执行
    system_clock = system_clock + 1
    setTimeout("update_system_clock()", 1000)
}

update_system_clock()

function update_process_queue(data) {
    // 清空当前队列信息
    $('.waitingQueue').text('等待队列')
    $('.swapQueue').text('交换队列')
    $('.uncreatedQueue').text('未建队列')
    $('.runningQueue').text('运行队列')
    $('.destroyedQueue').text('销毁队列')

    // 获取新的队列信息
    for (let i in data['waiting'])
        $('.waitingQueue').append('<div class="processBlock" onclick="show_process_detail($(this))">' + data['waiting'][i] + '</div>')
    for (let i in data['running'])
        $('.runningQueue').append('<div class="processBlock" onclick="show_process_detail($(this))">' + data['running'][i] + '</div>')
    for (let i in data['uncreated'])
        $('.uncreatedQueue').append('<div class="processBlock" onclick="show_process_detail($(this))">' + data['uncreated'][i] + '</div>')
    for (let i in data['swap'])
        $('.swapQueue').append('<div class="processBlock" onclick="show_process_detail($(this))">' + data['swap'][i] + '</div>')
    for (let i in data['destroyed'])
        $('.destroyedQueue').append('<div class="processBlock" onclick="show_process_detail($(this))">' + data['destroyed'][i] + '</div>')

}

// 获得进程详细信息 getProcessDetailInfo
// 获得内存详细信息 getMemoryDetailInfo

// 点击显示详细信息 -- elem 是选择器元素
function show_process_detail(elem) {

    let processID = elem.text()

    // 发送ajax请求进程的详细信息
    $.ajax({
        type: 'POST',
        url: '/getProcessDetailInfo',
        // 参数进程id(注意是字符串)
        data: {'processID': processID},
        success: function (data) {
            // 等待json格式的确定
            $('.processId').text('进程Id:' + data['processId'])
            $('.processType').text('进程类型:' + data['processType'])
            $('.processArriveTime').text('到达时间:' + data['processArriveTime'])
            $('.processDuration').text('持续时间:' + data['processDuration'])
            $('.processState').text('进程状态:' + data['processState'])
            $('.processPriority').text('进程优先级:' + data['processPriority'])
            $('.processPageNumber').text('进程占用页数:' + data['processPageNumber'])

            // 调度信息解析所有二位数组
            let array1 = data['processSchedule']
            let info1 = '进程调度信息:'
            for (let i in array1) {
                let temp_str = '{'
                for (let j in array1[i]){
                    temp_str += array1[i] + ', '
                }
                temp_str += '}, '
            }
            $('.processSchedule').text(info1)


            // 解析所有页码
            let array2 = data['processPagesId']
            let info2 = '进程占用页id:'
            for(let i in array2) {
                info2 += array2[i] + ' '
            }
            $('.processPagesId').text(info2)

            $('.deviceRequest').text('设备请求:' + data['deviceRequest'])
            $('.deviceRequestBit').text('设备使用已完成:' + data['deviceRequestBit'])

            // 设备现场信息
            let info3 = '设备现场信息:'
            let object1 = data['processScene']
            info3 += '已使用时间: ' + object1['occupied_time'] + '</br>'
            info3 += '状态: ' + object1['state'] + '</br>'
            info3 += '系统时钟: ' + object1['system_clock']

            $('.processScene').html(info3)

        }
    })
}



