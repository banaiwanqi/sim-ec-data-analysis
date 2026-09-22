const purple = "#7c3aed";
const orange = "#f97316";
const palette = ["#7c3aed", "#f97316", "#06b6d4"]

function fmt(n){
    return n == null ? "--" : Number(n).toLocaleString("zh-CN")
}

// kpi
fetch("api/summary")
.then(r => r.json())
.then(data => {
    document.querySelector("#kpi-qty .kpi-value").textContent = fmt(data.total_quantity);
    document.querySelector("#kpi-rev .kpi-value").textContent = fmt(data.total_revenue);
    document.querySelector("#kpi-records .kpi-value").textContent = fmt(data.total_records);
    document.querySelector("#kpi-member .kpi-value").textContent = data.avg_member != null ? (Number(data.avg_member) * 100).toFixed(1) + "%" : "--";
})

// 月销售折线图柱状图
fetch("api/monthly")
.then(r => r.json())
.then(data => {
    // 月度数据图表
    const c = echarts.init(document.getElementById('chart-monthly'));
    c.setOption({
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross',
                crossStyle: {
                    color: '#999'
                }
            }
        },
        toolbox: {
            feature: {
                magicType: { show: true, type: ['line', 'bar'] },
                restore: { show: true },
                saveAsImage: { show: true }
            }
            },
        legend: {
            data: ['月销量', '月营收'],
            textStyle: {

            }},
        xAxis: {
            type: 'category',
            data: data.map(d => d.month_year),
        },
        yAxis: [
            {
                type: 'value',
                name: '月销量',
                position: 'left',
            },
            {
                type: 'value',
                name: '月营收',
                position: 'right',
            }
            ],
        series: [
            {
                name: '月销量',
                type: 'bar',
                data: data.map(d => d.total_quantity),
                itemStyle: {
                    color: '#2563EB',
                },
                smooth: true,
            },
            {
                name: '月营收',
                type: 'line',
                yAxisIndex: 1,
                data: data.map(d => d.total_revenue),
                itemStyle: {
                    color: '#F97316',
                },
                smooth: true,
            }
        ],
    })
})

//销量排行
fetch("api/products")
.then(r => r.json())
.then(data => {
    const c = echarts.init(document.getElementById('chart-products'));
    c.setOption({
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            }
        },
        toolbox: {
            show: true,
            feature: {
                dataView: { readOnly: false },
                saveAsImage: {}
            }
        },
        grid: {
            left: '10%', 
            right: '8%',
            top: '5%',
            bottom: '8%',
            containLabel: true
        },
        xAxis: {
            type: 'value',
            name: '销量',
            boundaryGap: [0, 0.01]
        },
        yAxis: {
            type: 'category',
            data: data.map(d => d.goods_name),
            inverse: true,
            axisLabel: {
                interval: 0,
                fontSize: 11,        
                width: 120,
                
            }

        },
        dataZoom: [
            {
                show: true,
                start: 0,
                end: 100,
                height: 20,
                bottom: 8,
            },
            {
                type: 'inside',
                yAxisIndex: 0,
                start: 75,
                end: 100,
                moveOnMouseWheel: true,
                zoomOnMouseWheel: false
            },
            {
                show: true,
                yAxisIndex: 0,
                start: 25,
                end: 0,
                filterMode: 'empty',
                width: 25,
                height: '80%',
                showDataShadow: false,
                left:'93%',
                right: '5%'
            }
        ],
        series: { 
            data: data.map(d => d.total_amount), 
            type: 'bar', 
            itemStyle: { color: '#2563EB' }      
        },
    })
})

//会员等级分布
fetch("api/members")
.then(r => r.json())
.then(data => {

    const c = echarts.init(document.getElementById('chart-members'));
    c.setOption({
        color:['#2563EB', '#F97316', '#10B981'],
        tooltip: {
            trigger: 'item'
        },
        toolbox: {
            show: true,
            feature: {
                dataView: { readOnly: false },
                saveAsImage: {}
            }
        },
        legend: {
            orient: 'vertical',
            left: 'left',
        },
        emphasis: {
            label: {
                show: true,
                fontSize: '16',
                fontWeight: 'bold'
            }
        },
        series: [
            {
                name: '会员等级分布',
                type: 'pie',
                radius: '50%',
                data: data.map(d => ({ value: d.member_count, name: `${d.user_level}级会员` })),
                emphasis: {
                    itemStyle: {
                        shadowBlur: 10, 
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(55, 39, 39, 0.8)'
                    }

                }
            }
        ]
    })
})

//地区销量分布
fetch("api/regions-sales")
.then(r => r.json())
.then(data => {
    const c = echarts.init(document.getElementById('chart-regions'));

    //寻找最大最小值
    const values = data.map(d => d.total_quantity);
    const maxVal = Math.max(...values);
    const minVal = Math.min(...values);

    c.showLoading();

    $.get('./static/china.json', function (chinaJson) {
        c.hideLoading();
        echarts.registerMap('china', chinaJson);
        c.setOption({
            title: {
                textContent: '地区销量分布',
                left: 'center',
                top: 20,
            },
            tooltip: {
                trigger: 'item',
                showDelay: 0,
                transitionDuration: 0.2,
            },
            visualMap: {
                left: 'right',
                min:minVal,
                max:maxVal,
                inRange: {
                    color: ['#f0f7ff', '#d9eafb', '#b1cff2', '#4575b4', '#2563EB']
                },
                text: ['高', '低'],
                calculable: true
            },
            toolbox: {
                show: true,
                feature: {
                    dataView: { readOnly: false },
                    saveAsImage: {}
                }
            },
            series: [
                {
                    name: '销量',
                    type: 'map',
                    map: 'china',
                    roam: true,
                    emphasis: {
                        label: {
                            show: true 
                        }
                    },

                    data: data.map(d => ({ name: d.province, value: d.total_quantity }))
                }
            ]
        });
    })
})

//月复购用户统计
fetch("api/repurchase")
.then(r => r.json())
.then(data => {
    
    const c = echarts.init(document.getElementById('chart-repurchase'));

    c.setOption({
        color: ['#2563EB', '#F97316'],
        tooltip: {
            trigger: 'item'
        },
        legend: {
            data: ['总购买用户', '多次购买用户']
        },
        toolbox: {
            feature: {
                magicType: { show: true, type: ['line', 'bar'] },
                dataView: { readOnly: false},
                saveAsImage: {}
            }
        },
        xAxis: {
            type: 'category',
            data: data.map(d => d.order_month)
        },
        yAxis: [
            {
            type: 'value',
            }
        ],

        
        series: [
            {
                name: '总购买用户',
                type: 'bar',
                data: data.map(d => d.total_user),
                smooth: true
            },
            {
                name: '多次购买用户',
                type: 'bar',
                data: data.map(d => d.rpc_user),
                smooth: true
            }
        ]
    })
})

//二次购买留存率
fetch("api/conversion")
.then(r => r.json())
.then(data => {

    const item = data[0];
    const c = echarts.init(document.getElementById('chart-conversion'));

    c.setOption({
        tooltip: {
            trigger:'item',
            formatter: function(params){
                return `${params.seriesName}<br/>${params.name}：${params.value}人<br/>转化率：${item.total_second_buy_rate}%`
            }
        },
        toolbox: {
            feature: {
                dataView: { readOnly: false},
                saveAsImage: {}
            }
        },
        series: [
            // 外层 基准漏斗
            {
                color:['#2563EB', '#F97316'],
                name: '理想状态',
                type: 'funnel',
                left: '10%',
                top: 60,
                bottom: 60,
                width: '80%',
                minSize: '0%',
                maxSize: '100%',
                sort: 'descending',
                gap: 2,
                label: {
                    show: false
                },
                itemStyle: {
                    borderColor: '#fff',
                    borderWidth: 1,
                    opacity:0.6
                },
                emphasis: {
                    label:{
                        show: false
                    },
                    labelLine: {
                        show: false
                    }
                },
                data: [
                    {value: item.first_buy_user, name: '第一次购买用户数' },
                    {value: item.first_buy_user, name: '多次购买用户数'}
                ]
            },
              
            // 内层 实际漏斗
            {
                type: 'funnel',
                left: '10%',
                top: 60,
                bottom: 60,
                width: '80%',
                minSize: '0%',
                maxSize: '80%',
                sort: 'descending',
                gap: 2,
                label: {
                    show: true,
                    position: 'inside'
                },
                labelLine: {
                    length: 10,
                    lineStyle: {
                        width: 1,
                        type: 'solid'
                    }
                },
                itemStyle: {
                    borderColor: '#fff',
                    borderWidth: 1,
                    opacity:0.8
                },
                emphasis: {
                    label: {
                        fontSize: 20
                    }
                },
                z:100,
                data: [
                    {value: item.first_buy_user, name: '首购用户' },
                    {value: item.repurchase_2nd_user, name: '二次购买用户'}
                ]
            }
        ]
    })
})