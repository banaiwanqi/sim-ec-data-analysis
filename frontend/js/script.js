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
            data: data.map(d => d.month),
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
            }],
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
        series: { 
            data: data.map(d => d.total_amount), 
            type: 'bar', 
            itemStyle: { color: '#2563EB' }      
        },
    })
})
